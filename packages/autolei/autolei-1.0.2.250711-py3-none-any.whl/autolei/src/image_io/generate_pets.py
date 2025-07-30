"""
PETS Module - Generate

This module facilitates the batch conversion of MRC files into 32-bit floating-point monochrome TIFF images.
It includes features for compression, file merging, and generating PETS-compatible input files for Rotation
Electron Diffraction (RED) analysis.

Overview:
    - Recursive folder scanning for MRC files.
    - Parallel processing for efficient batch conversion.
    - Support for flexible merging and TIFF compression.
    - PETS-compatible `.pts` file generation for RED analysis.
    - Detailed logging of the conversion process.

Features:
    - Standalone usage or integration into Python workflows.
    - Handles large datasets common in crystallography and electron microscopy.

Credits:
    - Date: 2024-12-15
    - Authors: Yinlin Chen
    - License: BSD 3-Claude

Dependencies:
    - Standard Libraries:
        - argparse
        - concurrent.futures
        - datetime
        - glob
        - os
        - re
        - sys
    - Third-party Libraries:
        - mrcfile
        - numpy
        - tqdm
        - fabio
    - Custom Modules:
        - .util
        - .image

Notes:
    - Ensure all dependencies are installed in the working environment.
    - PETS file generation requires specific metadata in the MRC headers.
    - Parallel processing requires sufficient system resources for optimal performance.
"""

import argparse
import concurrent.futures
import glob
import os
import re
import sys
from datetime import datetime

import fabio
import mrcfile
import numpy as np
from fabio.tifimage import tifimage
from pkg_resources import parse_version
from tqdm import tqdm

from .mrc import head_opener
from ..util import natural_sort_key, windows_to_linux_path

WAVELENGTHS = {
    '400000.0': 0.016439,
    '300000.0': 0.019687,
    '200000.0': 0.025079,
    '150000.0': 0.029570,
    '120000.0': 0.033492,
    '100000.0': 0.037014,
}


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for configuring the MRC to TIFF conversion process.

    Returns:
        argparse.Namespace: Parsed arguments including:
            - `root_dir` (str): Root directory for scanning MRC files.
            - `file_extensions` (list): Target file extensions.
            - `save_subfolder` (str): Subfolder for saving TIFF files.
            - `overwrite` (bool): Flag to overwrite existing TIFF files.
            - `compression` (int): Compression level (0: None, 1: LZW).
            - `merge` (int): Number of frames to merge (default: 1).
    """
    parser = argparse.ArgumentParser(
        description="Batch convert MRC files to 32-bit floating point monochrome "
                    "TIFF with various compression methods.")
    parser.add_argument('root_dir', type=str, help='Root directory to start processing.')
    parser.add_argument('-f', '--file_extensions', type=str, nargs='+', default=['.mrc'],
                        help='File extensions to look for (default: .mrc).')
    parser.add_argument('-s', '--save_subfolder', type=str, default='tiff',
                        help='Name of the output subfolder for TIFF files.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Overwrite existing TIFF files if set.')
    parser.add_argument('-c', '--compression', type=int, default=0, choices=range(0, 2),
                        help=(
                            '0: None\n'
                            '1: LZW\n'
                        ))
    parser.add_argument('-m', '--merge', type=int, default=1,
                        help='Number of frames to merge together (default: 1).')
    return parser.parse_args()


def find_folders_with_files(root_dir: str, target_extensions: list, min_files: int = 10) -> list:
    """
    Recursively scans directories for folders containing a minimum number of files with specified extensions.

    Args:
        root_dir (str): Root directory to scan.
        target_extensions (list): List of file extensions to search for (e.g., ['.mrc']).
        min_files (int, optional): Minimum number of matching files per folder. Defaults to 10.

    Returns:
        list: List of folder paths meeting the criteria.
    """
    process_list = []
    for folder, _, files in os.walk(root_dir):
        matching_files = [f for f in files if os.path.splitext(f)[1].lower() in target_extensions]
        if len(matching_files) > min_files and os.path.basename(folder) not in ["redp", "ed3d"]:
            process_list.append(folder)
    return process_list


def suggest_compression(compression_level: int) -> tuple:
    """
    Maps a compression level to Fabio-compatible options and descriptions.

    Args:
        compression_level (int): Compression level (0: None, 1: LZW).

    Returns:
        tuple: Compression method, Fabio tag, and description.
    """
    compression_modes = {
        1: ("LZW", "lzw", "LZW Compression"),
        0: ("None", None, "None (1:1)"),
    }
    return compression_modes.get(compression_level, ("None", None, "None (1:1)"))


def convert_mrc_to_array(file_path: str) -> tuple:
    """
    Reads an MRC file and converts its data into a 32-bit floating-point NumPy array.

    Args:
        file_path (str): Path to the MRC file.

    Returns:
        tuple:
            - NumPy array of image data.
            - Header information from the MRC file.
        If an error occurs, returns (None, None).
    """
    try:
        with mrcfile.open(file_path, permissive=True) as mrc:
            img_data = mrc.data

            pedestal = np.flip(img_data, axis=0).astype(np.float32)
            pedestal = np.ascontiguousarray(pedestal)

            header = head_opener(file_path, parse_version(mrcfile.__version__) >= parse_version("1.5.0"))
            return pedestal, header
    except Exception as e:
        print(f"Error reading MRC file '{file_path}': {e}")
        return None, None


def convert_to_tiff(args: tuple) -> tuple:
    """
    Converts a single MRC file to a TIFF file with optional compression.

    Args:
        args (tuple): Tuple containing:
            - `input_path` (str): Path to the input MRC file.
            - `output_path` (str): Path to save the TIFF file.
            - `compression_tag`: Compression tag for TIFF files.

    Returns:
        tuple: Conversion status, input file path, and output details.
            - On success: (True, input_path, (output_path, alpha_tilt)).
            - On failure: (False, input_path, None).
    """
    input_path, output_path, compression_tag = args
    try:
        ext = os.path.splitext(input_path)[1].lower()
        if ext == '.mrc':
            img_array, header = convert_mrc_to_array(input_path)
            if img_array is None:
                return False, input_path, None
        else:
            raise ValueError(f"Unsupported file extension '{ext}' for file '{input_path}'.")

        # Save using Fabio
        img = tifimage()
        img.data = img_array
        if compression_tag:
            img.write(output_path)
        else:
            img.write(output_path)

        alpha_tilt = header.get("Alpha tilt", 0) if header else 0
        return True, input_path, (output_path, alpha_tilt)
    except Exception as e:
        print(f"Error converting '{input_path}' to TIFF: {e}")
        return False, input_path, None


def merge_and_convert(args: tuple) -> tuple:
    """
    Merges multiple MRC files into a single image and converts it to one TIFF file.

    Args:
        args (tuple): Tuple containing:
            - `input_paths` (list): List of input MRC file paths.
            - `output_path` (str): Path to save the merged TIFF file.
            - `compression_tag`: Compression tag for TIFF files.

    Returns:
        tuple: Merge status, input file paths, and output details.
            - On success: (True, input_paths, (output_path, alpha_tilt)).
            - On failure: (False, input_paths, None).
    """
    input_paths, output_path, compression_tag = args
    try:
        total_data = None
        for file_path in input_paths:
            img_array, _ = convert_mrc_to_array(file_path)
            if img_array is None:
                raise ValueError(f"Failed to read '{file_path}' during merging.")

            if total_data is None:
                total_data = img_array
            else:
                # Ensure shapes match
                if total_data.shape != img_array.shape:
                    raise ValueError(f"Image dimensions do not match for merging: '{input_paths[0]}' and '{file_path}'")
                total_data += img_array

        # Save using Fabio
        img = tifimage()
        img.data = total_data
        if compression_tag:
            img.write(output_path)
        else:
            img.write(output_path)

        # Extract header information from the first file in the group
        _, header = convert_mrc_to_array(input_paths[0])
        alpha_tilt = header.get("Alpha tilt", 0) if header else 0

        return True, input_paths, (output_path, alpha_tilt)
    except Exception as e:
        print(f"Error merging and converting files '{input_paths}': {e}")
        return False, input_paths, None


def generate_pts_file(
        output_folder: str,
        converted_files: list,
        lambda_val: float,
        aperpixel: float,
        merge: int) -> bool:
    """
    Generates a PETS-compatible `.pts` file for converted TIFF files.

    Args:
        output_folder (str): Path to save the `.pts` file.
        converted_files (list): List of converted TIFF file paths with alpha tilts.
        lambda_val (float): Experimental wavelength.
        aperpixel (float): Pixel size in reciprocal space.
        merge (int): Number of merged frames.

    Returns:
        bool: True if the `.pts` file is created successfully, otherwise False.
    """

    pts_file = os.path.join(os.path.dirname(output_folder), f'PETS_merge{merge}.pts' if merge > 1 else f'PETS.pts')
    current_time = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    try:
        # Compute phi as half of the average difference between consecutive frames
        if len(converted_files) < 2:
            avg_diff = 0.0
        else:
            alpha_tilts = [float(alpha) for _, alpha in converted_files]
            diffs = np.diff(alpha_tilts)
            avg_diff = np.mean(np.abs(diffs))
        phi = 0.5 * avg_diff

        # Compute bin based on image dimensions
        # Open the first TIFF to get dimensions
        first_tiff = converted_files[0][0]
        try:
            with fabio.open(first_tiff) as tif:
                img_shape = tif.data.shape  # (height, width)
                height, width = img_shape
        except Exception as e:
            print(f"Error reading TIFF file '{first_tiff}' for bin calculation: {e}")
            height, width = 1024, 1024  # Default dimensions if reading fails

        if max(height, width) >= 1536:
            bin_computed = 2
        elif max(height, width) >= 3072:
            bin_computed = 4
        else:
            bin_computed = 1

        with open(pts_file, 'w') as f:
            # Write header
            f.write("# PETS input file for Rotation Electron Diffraction generated by `generate_pets`.\n")
            f.write(f"# {current_time}\n\n")

            # Write parameters
            f.write(f"lambda {lambda_val}\n")
            f.write(f"aperpixel {aperpixel}\n")
            f.write(f"phi {phi:.4f}\n")  # Updated phi
            f.write(f"omega 5.6545\n")
            f.write(f"bin {bin_computed}\n")  # Updated bin
            f.write(f"reflectionsize 15\n")
            f.write(f"noiseparameters 28 760\n")
            f.write(f"geometry continuous\n\n")

            f.write(f"detector cetad\n")
            f.write(f"center AUTO\n")
            f.write(f"centermode friedelpairs 1\n")
            f.write(f"i/sigma    10.00   10.00\n")
            f.write(f"cellrefinemode cellanddistort\n\n")
            f.write(f"autotask\npeak search\ntilt axis\npeak analysis\nfind cell\nendautotask\n\n")

            # Write image list
            f.write("imagelist\n")
            for tiff_file, alpha_tilt in converted_files:
                relative_path = os.path.relpath(tiff_file, start=os.path.dirname(output_folder))
                f.write(f"{relative_path}  {float(alpha_tilt):<8.3f}  0.0\n")
            f.write("endimagelist\n\n\n\n")
        return True
    except Exception as e:
        print(f"Error writing PETS.pts file in '{output_folder}': {e}")
        return False


def delete_files(file_list: list) -> None:
    """
    Deletes specified files from the filesystem.

    Args:
        file_list (list): List of file paths to delete.
    """
    for file in file_list:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Error deleting {file}: {e}")


def process_folders(
        process_list: list,
        save_subfolder: str,
        overwrite: bool,
        compression_level: int,
        merge: int) -> list:
    """
    Processes a list of folders by converting MRC files to TIFF, optionally merging frames,
    and generating PETS-compatible `.pts` files.

    Args:
        process_list (list): List of folder paths to process.
        save_subfolder (str): Subfolder for saving TIFF files.
        overwrite (bool): Whether to overwrite existing TIFF files.
        compression_level (int): Compression level for TIFF (0: None, 1: LZW).
        merge (int): Number of frames to merge.

    Returns:
        list: Log entries summarizing the conversion process.
    """
    log_entries = []
    compression_method, compression_tag, compression_description = suggest_compression(compression_level)

    for folder in tqdm(process_list, desc="Processing Folders", unit="folder"):
        folder_path = folder
        if (folder_path.lower().endswith("ed3d") or folder_path.lower().endswith("atlus") or
                folder_path.lower().endswith("red") or folder_path.lower().endswith("redp")):
            continue
        output_folder = os.path.join(folder_path, save_subfolder)
        tiff_files_existing = glob.glob(os.path.join(output_folder, '*.tiff')) + glob.glob(
            os.path.join(output_folder, '*.tif'))

        if os.path.exists(output_folder) and tiff_files_existing and not overwrite:
            print(
                f"\nSkipping '{folder}' as '{save_subfolder}' "
                f"with TIFF files already exists. Use --overwrite to overwrite.")
            continue
        elif os.path.exists(output_folder) and tiff_files_existing:
            delete_files(tiff_files_existing)

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder, exist_ok=True)
            except Exception as e:
                print(f"\nError creating output folder '{output_folder}': {e}")
                continue

        files_in_folder = os.listdir(folder_path)
        files_to_convert = [os.path.join(folder_path, f) for f in files_in_folder if
                            os.path.splitext(f)[1].lower() == '.mrc']
        files_to_convert = sorted(files_to_convert, key=natural_sort_key)

        file_groups = {}
        for file in files_to_convert:
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

        files_to_convert = sorted(max_group, key=natural_sort_key)

        if not files_to_convert:
            print(f"No MRC files found in '{folder}'. Skipping.")
            continue

        sample_file_index = min(len(files_to_convert) - 1, 8)

        header = head_opener(files_to_convert[sample_file_index],
                             parse_version(mrcfile.__version__) >= parse_version("1.5.0"))
        try:
            lambda_val = WAVELENGTHS[header['HT']]
        except KeyError:
            print(f"HT value '{header.get('HT')}' not found in WAVELENGTHS. Using default value 0.025079.")
            lambda_val = 0.025079  # Default value or handle as per requirement

        pixel_size = float(header.get('Pixel size X', 0)) * 1e-10

        converted_files = []
        args_list = []

        if merge <= 1:
            # No merging, process individually
            for file_path in files_to_convert:
                output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(file_path))[0] + '.tiff')
                args_list.append((file_path, output_file, compression_tag))

            # Use ProcessPoolExecutor for parallel processing
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(tqdm(executor.map(convert_to_tiff, args_list), total=len(args_list),
                                    desc=f"Converting in {os.path.basename(folder)}", unit="file", leave=False))

            for success, input_file, result in results:
                if success:
                    output_file, alpha_tilt = result
                    log_entries.append(
                        f"Converted: {input_file} -> {output_file} | Compression: {compression_description}")
                    converted_files.append((output_file, alpha_tilt))
                else:
                    log_entries.append(f"Failed to convert: {input_file}")
        else:
            # Merging enabled
            merged_groups = [files_to_convert[i:i + merge] for i in range(0, len(files_to_convert), merge)]
            for group in merged_groups:
                first_file = group[0]
                output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(first_file))[0] + '.tiff')
                args_list.append((group, output_file, compression_tag))

            # Use ProcessPoolExecutor for parallel processing
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(tqdm(executor.map(merge_and_convert, args_list), total=len(args_list),
                                    desc=f"Merging & Converting in {os.path.basename(folder)}", unit="group",
                                    leave=False))

            for success, input_files, result in results:
                if success:
                    output_file, alpha_tilt = result
                    log_entries.append(
                        f"Merged: {input_files} -> {output_file} | Compression: {compression_description}")
                    converted_files.append((output_file, alpha_tilt))
                else:
                    log_entries.append(f"Failed to merge and convert: {input_files}")

        if converted_files:
            pts_success = generate_pts_file(
                output_folder,
                converted_files,
                lambda_val,
                pixel_size,
                merge
            )
            if pts_success:
                log_entries.append(f"Generated PETS.pts in '{output_folder}'")
            else:
                log_entries.append(f"Failed to generate PETS.pts in '{output_folder}'")

    return log_entries


def write_log(log_entries: list, parent_dir: str) -> None:
    """
    Writes a log file summarizing the conversion process.

    Args:
        log_entries (list): List of log entry strings.
        parent_dir (str): Directory to save the log file.
    """
    log_file = os.path.join(parent_dir, 'conversion_log.txt')
    try:
        with open(log_file, 'w') as f:
            for entry in log_entries:
                f.write(entry + '\n')
        print(f"\nLog written to '{log_file}'")
    except Exception as e:
        print(f"\nError writing log file: {e}")


def main() -> None:
    """
    Main function to execute the batch MRC to TIFF conversion process.

    Steps:
        1. Parse command-line arguments.
        2. Scan directories for target file extensions.
        3. Convert MRC files to TIFF.
        4. Generate `.pts` files and log the results.

    Returns:
        None
    """
    args = parse_arguments()
    root_directory = args.root_dir
    target_extensions = [ext.lower() for ext in args.file_extensions]
    merge_factor = args.merge

    if ":" in root_directory and "\\" in root_directory:
        root_directory = windows_to_linux_path(root_directory)

    if root_directory.startswith("."):
        root_directory = os.path.abspath(os.path.join(os.getcwd(), root_directory))

    if not os.path.exists(root_directory) or not os.path.isdir(root_directory):
        print(f"Error: The specified root directory '{root_directory}' does not exist or is not a directory.")
        sys.exit(1)

    print("Scanning directories...")
    folders_to_process = find_folders_with_files(root_directory, target_extensions)
    print(f"Found {len(folders_to_process)} folders with more than 10 files ({', '.join(target_extensions)}).")

    if not folders_to_process:
        print("No folders meet the criteria. Exiting.")
        sys.exit(0)

    print("Starting conversion process...")
    log_entries = process_folders(
        folders_to_process,
        args.save_subfolder,
        args.overwrite,
        args.compression,
        merge_factor,
    )

    if log_entries:
        write_log(log_entries, root_directory)


def run_pets_function(root_dir: str, overwrite: bool, merge: int = 1) -> None:
    """
    External function for triggering PETS processing workflows from other scripts.

    Args:
        root_dir (str): Root directory containing MRC files.
        overwrite (bool): Whether to overwrite existing TIFF files.
        merge (int, optional): Number of frames to merge (default: 1).
    """
    target_extensions = [".mrc"]

    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        print(f"Error: The specified root directory '{root_dir}' does not exist or is not a directory.")
        sys.exit(1)

    print("Scanning directories...")
    folders_to_process = find_folders_with_files(root_dir, target_extensions)
    print(f"Found {len(folders_to_process)} folders with more than 10 files ({', '.join(target_extensions)}).")

    if not folders_to_process:
        print("No folders meet the criteria. Exiting.")
        sys.exit(0)

    print("Starting conversion process...")
    log_entries = process_folders(
        folders_to_process,
        "tiff",
        overwrite,
        0,
        merge,
    )

    if log_entries:
        write_log(log_entries, root_dir)


if __name__ == "__main__":
    main()
