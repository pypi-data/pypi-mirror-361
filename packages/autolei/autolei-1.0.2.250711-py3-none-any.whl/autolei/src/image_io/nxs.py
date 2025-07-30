import configparser
import glob
import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import h5py
import numpy as np
from fabio import adscimage
from tqdm import tqdm

from ..util import find_folders_with_images, natural_sort_key

script_dir = os.path.dirname(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])


# ****************
# DLS NXS to IMG
# ****************

def read_nxs_file(file_path: str) -> tuple:
    """
    Reads a NeXus (NXS) file and extracts data and metadata.

    Args:
        file_path (str): Path to the NXS file.

    Returns:
        tuple: Tuple containing:
            - `data (numpy.ndarray)`: The image data.
            - `metadict (dict)`: Metadata extracted from the file.
    """
    metadict = {}
    with h5py.File(file_path, 'r') as file:
        # Adjust this path based on the actual structure of your NeXus file
        data = file['/entry/data/data'][()]
        metadict['wavelength'] = float(file['/entry/instrument/beam/incident_wavelength'][()])
        metadict['orgx'] = float(file['/entry/instrument/detector/beam_center_x'][()])
        metadict['orgy'] = float(file['/entry/instrument/detector/beam_center_y'][()])
        metadict['time'] = round(float(file['/entry/instrument/detector/count_time'][()]), 4)
        metadict['detector'] = file['/entry/instrument/detector/description'][()].decode('ascii')
        metadict['camera_length'] = float(file['/entry/instrument/detector/distance'][()]) * 1000
        metadict['pixel_size_x'] = float(file['/entry/instrument/detector/x_pixel_size'][()]) * 1000
        metadict['pixel_size_y'] = float(file['/entry/instrument/detector/y_pixel_size'][()]) * 1000
        metadict['HT'] = int(file['/entry/instrument/detector/photon_energy'][()]) // 1000
        metadict['overload'] = int(file['/entry/instrument/detector/saturation_value'][()])
        metadict['beamline'] = file['/entry/instrument/name'][()].decode('ascii')
        metadict['phi'] = list(file['/entry/data/alpha'][()])
        metadict['start_time'] = file['/entry/start_time'][()].decode('ascii')
    return data, metadict


def write_smv_nxs(img_data: np.ndarray, index: int, metadict: dict, img_folder: str) -> None:
    """
    Writes image data to a SMV file from NXS metadata.

    Args:
        img_data (numpy.ndarray): Image data array.
        index (int): Image index.
        metadict (dict): Metadata dictionary.
        img_folder (str): Directory to save the SMV files.
    """
    # Create a Fabio image object
    file_path = os.path.join(img_folder, f'1_{index + 1:04d}.img')

    pedestal = img_data + 0
    np.clip(pedestal, 0, metadict["overload"], out=pedestal)

    img = adscimage.AdscImage(data=pedestal.astype(np.uint16))
    # Optionally, set the header
    img.header = {
        'DIM': 2,
        'SIZE1': img_data.shape[1],
        'SIZE2': img_data.shape[0],
        'BYTE_ORDER': 'little_endian',
        'TYPE': 'unsigned_short',
        'HEADER_BYTES': 512,
        'DATE': metadict['start_time'],
        'TIME': metadict['time'],
        'BEAMLINE': metadict['beamline'],
        'DETECTOR': metadict['detector'],
        'WAVELENGTH': metadict['wavelength'],
        'PHI': metadict['phi'][index],
        'OSC_START': metadict['phi'][index],
        'OSC_RANGE': metadict['phi'][1] - metadict['phi'][0],
        'PIXEL_SIZE': metadict['pixel_size_x'],
        'DISTANCE': metadict['camera_length'],
        'Data_type': "unsigned short int"
    }
    # Write the image to an SMV file
    img.write(file_path)


def convert_nxs2img(directory: str, path_filter: bool = False) -> None:
    """
    Converts all NXS files in a directory to IMG format.

    Args:
        directory (str): Directory containing NXS files.
        path_filter (bool, optional): Flag to filter paths during conversion. Defaults to False.
    """
    print("********************************************")
    print("*           DLS NXS to SMV Image           *")
    print("********************************************\n")
    if not directory:
        print("No directory selected. Exiting.")
        return

    nxs_folders = find_folders_with_images(directory, extension=".nxs", min_img_count=1, path_filter=path_filter)
    for nxs_folder in nxs_folders:
        nxs_file_path = glob.glob(os.path.join(nxs_folder, '*.nxs'))[0]
        print(f"Convert {nxs_file_path}")
        try:
            data, metadata = read_nxs_file(nxs_file_path)
            num_images = data.shape[0]
        except Exception as exc:
            print(f"{nxs_file_path} reading fail due to {exc}.")
            continue

        img_folder = os.path.join(nxs_folder, "SMV")
        os.makedirs(img_folder, exist_ok=True)
        img_files = sorted(glob.glob(os.path.join(img_folder, '*.img')), key=natural_sort_key)
        if len(img_files) >= num_images:
            print(f"Directory {nxs_folder} is already converted.")
            continue

        with ThreadPoolExecutor(max_workers=set_max_worker) as executor:
            futures = [executor.submit(write_smv_nxs, data[i], i, metadata, img_folder) for i in range(num_images)]
            for future in tqdm(as_completed(futures), total=num_images, desc="Converting", ascii=True):
                future.result()
        print("Converted successfully.\n")
