import configparser
import glob
import os
import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import fabio
import mrcfile
import numpy as np
from fabio import adscimage
from pkg_resources import parse_version
from tqdm import tqdm

from ..util import clean_string, timestamp_string, find_folders_with_images, natural_sort_key, extract_pattern

script_dir = os.path.dirname(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])

# wavelength for different voltage
WAVELENGTHS = {
    '400': 0.016439,
    '300': 0.019687,
    '200': 0.025079,
    '150': 0.029570,
    '120': 0.033492,
    '100': 0.037014,
    '400000.0': 0.016439,
    '300000.0': 0.019687,
    '200000.0': 0.025079,
    '150000.0': 0.029570,
    '120000.0': 0.033492,
    '100000.0': 0.037014,
}


# ****************
# MRC Conversion
# ****************


def head_opener(input_mrc: str, new_version: bool = True) -> dict:
    """
    Extracts header information from an MRC file.

    Args:
        input_mrc (str): Path to the MRC file.
        new_version (bool, optional): Flag indicating the header structure version. Defaults to True.

    Returns:
        dict: Dictionary containing the extracted header information.
    """
    with mrcfile.open(input_mrc, header_only=True) as mrc:
        head_dict = {item: clean_string(str(getattr(mrc.header, item)))
                     for item in mrc.header.dtype.names}

        extended_header = 'indexed_extended_header' if new_version else 'extended_header'
        if mrc.header.exttyp in [b"FEI2", b"FEI1"]:
            for exthead_field in getattr(mrc, extended_header).dtype.names:
                head_dict[exthead_field] = clean_string(str(getattr(mrc, extended_header)[exthead_field][0]))

        return {k: v for k, v in head_dict.items() if v not in ("0", "0.0", "")}


def process_mrc_file(args: tuple) -> None:
    """
    Processes and converts an MRC file to a new format.

    Args:
        args (tuple): Tuple containing:
            - `mrc_path (str)`: Path to the MRC file.
            - `path (str)`: Output directory path.
    """
    mrc_path, path = args
    with mrcfile.open(mrc_path) as mrc:
        data = mrc.data
        mrcfile.new(os.path.join(path, 'redp', os.path.basename(mrc_path)), data, overwrite=True)


def process_single_mrc_file(
        mrc_path: str,
        new_prefix: str,
        digit: int,
        start_index: int,
        min_val: float,
        scale: float) -> tuple:
    """
    Converts a single MRC file to IMG format.

    Args:
        mrc_path (str): Path to the MRC file.
        new_prefix (str): Prefix for the output IMG files.
        digit (int): Number of digits in the filename index.
        start_index (int): Starting index for the filenames.
        min_val (float): Minimum value for scaling.
        scale (float): Scaling factor.

    Returns:
        tuple: Tuple containing the MRC file path and a boolean indicating success.
    """

    def conditional_update(dictionary, key, value):
        if value is not None and value != "":
            dictionary[key] = value

    with mrcfile.open(mrc_path) as mrc:
        img_data = mrc.data
    header = head_opener(mrc_path, parse_version(mrcfile.__version__) >= parse_version("1.5.0"))

    # Avoid division by zero in case min_val equals max_val
    pedestal = np.flip((img_data - min_val) / scale, axis=0)
    pedestal[pedestal > 65000] = 65000
    pedestal[pedestal < 0] = 0

    img = fabio.adscimage.AdscImage(data=pedestal.astype(np.uint16))
    conditional_update(img.header, 'SIZE1', header["nx"])
    conditional_update(img.header, 'SIZE2', header["ny"])

    bin_value = header.get("Binning Width", "1") + "x" + header.get("Binning Height", "1")
    if bin_value != "1x1":
        img.header['BIN'] = bin_value

    img.header['BIN_TYPE'] = "HW"

    timestamp = header.get("Timestamp", 0)
    if timestamp:
        img.header['DATE'] = timestamp_string(float(timestamp))

    conditional_update(img.header, 'TIME', header.get("Integration time", None))
    conditional_update(img.header, 'BEAMLINE', header.get("Microscope type", None))
    conditional_update(img.header, 'DETECTOR', header.get("Camera name", None))
    conditional_update(img.header, 'PEDESTAL', int(-min_val / scale))

    ht_value = header.get("HT", "0.0")
    if ht_value != "0.0":
        img.header['WAVELENGTH'] = WAVELENGTHS[ht_value]

    conditional_update(img.header, 'SPOT_SIZE', header.get("Spot index", None))

    alpha_value = header.get("Alpha tilt", 0)
    if alpha_value:
        img.header['PHI'] = "{:.4f}".format(float(alpha_value))

    if 'exttyp' in header and header['exttyp'] == "FEI2":
        img.header.update({
            "OSC_START": "{:.4f}".format(
                float(header.get("Alpha tilt", 0.0)) - float(header.get("Tilt per image", 0.0))),
            "OSC_RANGE": "{:.4f}".format(float(header.get("Tilt per image", 0.0)))
        })
    if 'Camera name' in header and header['Camera name'] == "BM-Ceta":
        img.header.update({"PIXEL_SIZE": int(header.get("Binning Width", "1")) * 0.014,
                           "DISTANCE": "{:.2f}".format(0.014 * 10 ** 10 * int(header["Binning Width"]) /
                                                       WAVELENGTHS[ht_value] / float(header['Pixel size X']))
                           })

    new_filename = f"{new_prefix}{str(start_index).zfill(digit)}.img"
    img.write(new_filename)
    return mrc_path, True


def conversion_mrc_file(
        mrc_files: list,
        new_prefix: str,
        digit: int,
        max_worker: int = set_max_worker) -> int:
    """
    Converts multiple MRC files to IMG format using parallel processing.

    Args:
        mrc_files (list): List of MRC files to convert.
        new_prefix (str): Prefix for the output filenames.
        digit (int): Number of digits in the filename index.
        max_worker (int, optional): Maximum number of threads to use. Defaults to `set_max_worker`.

    Returns:
        int: Number of successfully converted files.
    """
    results = []
    start_index = 1

    with mrcfile.open(mrc_files[-9]) as mrc:
        img_data = mrc.data
        min_val = int(np.min(img_data) * 0.2)
        scale = ((np.max(img_data) - np.min(img_data)) / 65536) if (np.max(img_data) - np.min(img_data)) > 65000 else 1
        if scale > 3:
            scale = 1

    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        # Submit all MRC files for conversion in parallel
        future_to_mrc = {
            executor.submit(process_single_mrc_file, mrc_path, new_prefix, digit, start_index + i, min_val, scale):
                mrc_path for i, mrc_path in enumerate(mrc_files)}
        for future in tqdm(as_completed(future_to_mrc), total=len(mrc_files), desc="Converting", ascii=True):
            mrc_path = future_to_mrc[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'{mrc_path} generated an exception: {exc}')
    # Log the results
    converted_count = sum(1 for _, converted in results if converted)
    print(f"{converted_count} of {len(mrc_files)} converted.\n")
    return converted_count


def convert_mrc2img(directory: str, path_filter: bool = False) -> None:
    """
    Converts all MRC files in a directory to IMG format.

    Args:
        directory (str): Directory containing MRC files.
        path_filter (bool, optional): Flag to filter paths during conversion. Defaults to False.
    """
    print("********************************************")
    print("*             MRC to SMV Image             *")
    print("********************************************\n")
    if not directory:
        print("No directory selected. Exiting.")
        return None
    """ Convert all .mrc files in a directory to .img format, with checks for specific conditions. """
    folder_paths = find_folders_with_images(directory, extension=".mrc", path_filter=path_filter)

    for path in folder_paths:
        # Check if directory is collected by specific criteria or has already been converted
        parent_folder = os.path.dirname(path)
        cred_log_path = os.path.join(parent_folder, 'cRED_log.txt')
        print(f"Entering Folder {path}")

        # Skip if path is specifically an 'redp' output directory or has a corresponding cRED log
        if path.endswith("redp") or os.path.isfile(cred_log_path) or path.lower().endswith("atlas"):
            continue

        mrc_files = sorted(glob.glob(os.path.join(path, '*.mrc')), key=natural_sort_key)

        file_groups = {}
        for file in mrc_files:
            filename = os.path.basename(file)

            # Check if the filename ends with a digit before .mrc
            if re.search(r'\d+\.mrc$', filename):
                length = len(filename)

                # Group files based on the length of the filename
                if length not in file_groups:
                    file_groups[length] = [file]
                else:
                    file_groups[length].append(file)

        # Find the largest group based on the number of files
        max_group_size = 0
        max_group = []

        for length, files in file_groups.items():
            if len(files) > max_group_size:
                max_group_size = len(files)
                max_group = files

        # mrc_files now contains only files from the largest group by filename length
        mrc_files = sorted(max_group, key=natural_sort_key)

        img_files = sorted(glob.glob(os.path.join(os.path.join(parent_folder, 'SMV', 'data'), '*.img')),
                           key=natural_sort_key)
        if not img_files:
            img_files = sorted(glob.glob(os.path.join(path, '*.img')), key=natural_sort_key)

        # Check if the count of .img files matches the count of .mrc files, indicating conversion might already be done
        if len(img_files) >= len(mrc_files):
            print(f"Directory {path} don't need to convert.")
            continue

        file_base_name, first, last = extract_pattern(mrc_files)
        digit = file_base_name.count("?") if last not in [9, 99, 999] else file_base_name.count("?") + 1
        new_prefix = extract_pattern(mrc_files)[0].split("?")[0] \
            if last not in [9, 99, 999] else extract_pattern(mrc_files)[0].split("?")[0][:-1]
        # Proceed with conversion if the above conditions are not met
        conversion_mrc_file(mrc_files, new_prefix, digit)
    print("Conversion Finished.\n")


# ****************
# REDp input file
# ****************
def generate_redp(input_path: str, max_worker: int = set_max_worker) -> None:
    """
    Generates `.redp` files and organizes metadata for MRC files.

    Args:
        input_path (str): Directory containing MRC files.
        max_worker (int, optional): Maximum number of threads to use. Defaults to `set_max_worker`.
    """

    print("********************************************")
    print("*            REDp ED3D Generator           *")
    print("********************************************\n")
    folder_path = find_folders_with_images(input_path, extension=".mrc")
    for path in folder_path:
        redp_path = os.path.join(path, 'redp')
        os.makedirs(redp_path, exist_ok=True)
        if ([file for file in os.listdir(path) if file.endswith('.ed3d')] or path.endswith("redp")
                or path.lower().endswith("atlas")
                or [file for file in os.listdir(os.path.join(path, 'redp')) if file.endswith('.ed3d')]):
            continue

        mrc_files = sorted(glob.glob(os.path.join(path, '*.mrc')), key=natural_sort_key)
        if not mrc_files:
            continue

        # Create a dictionary to group files by their filename length
        file_groups = {}
        for file in mrc_files:
            filename = os.path.basename(file)

            # Check if the filename ends with a digit before .mrc
            if re.search(r'\d+\.mrc$', filename):
                length = len(filename)

                # Group files based on the length of the filename
                if length not in file_groups:
                    file_groups[length] = [file]
                else:
                    file_groups[length].append(file)

        # Find the largest group based on the number of files
        max_group_size = 0
        max_group = []

        for length, files in file_groups.items():
            if len(files) > max_group_size:
                max_group_size = len(files)
                max_group = files

        # mrc_files now contains only files from the largest group by filename length
        mrc_files = sorted(max_group, key=natural_sort_key)

        tilt_key = ""
        mrc_version_check = parse_version(mrcfile.__version__) >= parse_version("1.5.0")
        rot_dict, wl_list, pixel_list, steps = {}, [], [], []

        with ThreadPoolExecutor(max_workers=max_worker) as executor:
            list(tqdm(executor.map(process_mrc_file, [(mrc_path, path) for mrc_path in mrc_files]),
                      total=len(mrc_files), desc="Converting", ascii=True))
        print("Image has downgraded to the version REDp can read.")

        for mrc_path in mrc_files:
            header = head_opener(mrc_path, new_version=mrc_version_check)
            tilt_key = "Alpha tilt" if "Alpha tilt" in header else "Beta tilt"
            rot_dict[os.path.basename(mrc_path)] = float(header.get(tilt_key, 0.0))
            wl_list.append(WAVELENGTHS[header['HT']])
            pixel_list.append(float(header['Pixel size X']) * 10 ** -10)
            steps.append(float(header["Tilt per image"]))

        with open(os.path.join(redp_path, '1.ed3d'), "w") as out_f:
            out_f.write(f"WAVELENGTH    {wl_list[0]} \n")
            out_f.write(f"CCDPIXELSIZE    {pixel_list[0]}\n")
            rotation_axis = 1.0 if tilt_key == "Alpha tilt" else -89.0
            out_f.write(f"ROTATIONAXIS    {rotation_axis}\n")
            out_f.write(f"GONIOTILTSTEP    {steps[0]:.4f}\n")
            out_f.write("BEAMTILTSTEP    0\nBEAMTILTRANGE    0.000\nSTRETCHINGMP    0.0\nSTRETCHINGAZIMUTH   0.0\n")
            out_f.write("\n\nFILELIST\n")
            sorted_dict = dict(sorted(rot_dict.items(), key=lambda item: item[1]))
            for key, value in sorted_dict.items():
                out_f.write(f"FILE {key} {value:.4f} 0 {value:.4f}\n")
            out_f.write("ENDFILELIST\n\n")
            print(f"redp input for REDp successfully generated in {redp_path}.")
