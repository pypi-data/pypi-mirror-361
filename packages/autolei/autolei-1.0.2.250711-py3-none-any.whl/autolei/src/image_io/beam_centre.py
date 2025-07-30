import configparser
import glob
import os
import random
from concurrent.futures import ThreadPoolExecutor

import fabio
import numpy as np
from tqdm import tqdm

from ..util import natural_sort_key, remove_outliers_iqr
from ..xds_input import get_xds_inp_image_dict, replace_value

script_dir = os.path.dirname(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])


def find_direct_beam_center(img_path: str) -> tuple:
    """
    Finds the approximate center of the direct beam in an IMG file.

    Args:
        img_path (str): Path to the IMG file.

    Returns:
        tuple: (center_x, center_y) coordinates of the beam center.
    """
    # 1. Read in the image
    img = fabio.open(img_path)
    img_array = img.data

    # 2. Find global maximum intensity
    max_intensity = np.max(img_array)

    # 3. Check fraction of pixels at this max intensity (handle saturation)
    total_points = img_array.size
    num_max_intensity_points = np.sum(img_array == max_intensity)
    if num_max_intensity_points / total_points > 0.02:
        img_array = np.where(img_array == max_intensity, 0, img_array)
        max_intensity = np.max(img_array)

    # 4. Create an intensity mask to ignore very low background
    threshold = 0.2 * max_intensity
    above_threshold = (img_array > threshold)

    # 5. If nothing is above threshold, fall back to the absolute max position
    if not np.any(above_threshold):
        max_pos = np.argmax(img_array)
        center_y, center_x = np.unravel_index(max_pos, img_array.shape)
        return float(center_x), float(center_y)

    # 6. Otherwise, compute an intensity-weighted center of mass
    coords = np.indices(img_array.shape)
    sum_intensity = np.sum(img_array[above_threshold])
    sum_y = np.sum(coords[0][above_threshold] * img_array[above_threshold])
    sum_x = np.sum(coords[1][above_threshold] * img_array[above_threshold])

    # Avoid division by zero (in case of weird edge cases)
    if sum_intensity == 0:
        max_pos = np.argmax(img_array)
        center_y, center_x = np.unravel_index(max_pos, img_array.shape)
    else:
        center_y = sum_y / sum_intensity
        center_x = sum_x / sum_intensity

    return float(center_x), float(center_y)


def process_folder_beam_centre(img_path: str, xds_path: str, max_files: int = 50):
    """
    Processes a folder of IMG files to calculate the beam center.

    Args:
        img_path (str): Directory containing IMG files.
        xds_path (str): Path to the XDS.INP file.
        max_files (int, optional): Maximum number of files to process. Defaults to 50.
    """

    img_files = sorted(glob.glob(os.path.join(img_path, '*.img')), key=natural_sort_key)
    if not img_files:
        print("No images found in that folder, please check if your path in XDS.INP is correct.\n")
        return None

    # If there are more than max_files, sample max_files evenly
    if len(img_files) > max_files:
        img_files = random.sample(img_files, max_files)

    with ThreadPoolExecutor(max_workers=set_max_worker) as executor:
        results = list(tqdm(executor.map(find_direct_beam_center, img_files),
                            total=len(img_files), desc="Processing images", ascii=True))

    x_values, y_values = [], []
    for x, y in results:
        if x != 0:
            x_values.append(x)
        if y != 0:
            y_values.append(y)

    x_values_filtered = remove_outliers_iqr(x_values, offset=1)
    y_values_filtered = remove_outliers_iqr(y_values, offset=1)

    # Calculate averages of the filtered values
    if x_values_filtered and y_values_filtered:
        avg_x = sum(x_values_filtered) / len(x_values_filtered)
        avg_y = sum(y_values_filtered) / len(y_values_filtered)
        print(f"Average beam center position: ({avg_x}, {avg_y})")
        update_beam_centers_file(img_path, avg_x, avg_y)
        update_xds_inp(xds_path, avg_x, avg_y)
    else:
        print("Unable to calculate average beam center.")


def update_beam_centers_file(img_directory: str, avr_x: float, avr_y: float) -> None:
    """
    Writes the average beam center to a text file.

    Args:
        img_directory (str): Directory containing IMG files.
        avr_x (float): Average X coordinate of the beam center.
        avr_y (float): Average Y coordinate of the beam center.
    """

    """Write the average beam center to a text file in the image directory."""
    centers_file_path = os.path.join(img_directory, 'direct_beam_centers.txt')
    with open(centers_file_path, 'w') as file:
        file.write(f"Average beam center: ({avr_x}, {avr_y})\n")


def update_xds_inp(xds_inp_path: str, avr_x: float, avr_y: float) -> None:
    """
    Updates the ORGX and ORGY values in the XDS.INP file.

    Args:
        xds_inp_path (str): Path to the XDS.INP file.
        avr_x (float): Average X coordinate of the beam center.
        avr_y (float): Average Y coordinate of the beam center.
    """
    if os.path.exists(xds_inp_path):
        with open(xds_inp_path, 'r', errors="ignore") as file:
            lines = file.readlines()
        lines = [line for line in lines if
                 not line.strip().startswith('ORGX=') and not line.strip().startswith('ORGY=')]
        with open(xds_inp_path, 'w') as file:
            file.writelines(lines)
            file.write(f'ORGX= {avr_x:.3f} ORGY= {avr_y:.3f}\n')
        print(f"xds.inp successfully updated with ORGX= {avr_x:.2f}, ORGY= {avr_y:.2f}.\n")
    else:
        print(f"xds.inp not found at the expected path: {xds_inp_path}.\n")


def centre_calculate(input_path: str) -> None:
    """
    Calculates the beam center for all IMG files in a directory.

    Args:
        input_path (str): Directory containing IMG files.
    """
    if input_path:
        print("********************************************")
        print("*            Beam Centre Finder            *")
        print("*--------   No Beam Stop Version   --------*")
        print("********************************************\n")

        print(f"Self beam centre finding has received input path: {input_path}")
        paths_dict = get_xds_inp_image_dict(input_path)
        if not paths_dict:
            print("No XDS.inp found.\n")
            return
        for xds_path in paths_dict.keys():
            img_dir = os.path.dirname(paths_dict[xds_path]["image_path"])
            img_format = paths_dict[xds_path]["image_format"]
            if img_format == "SMV":
                print(f"Entering folder: {img_dir}")
                process_folder_beam_centre(img_dir, xds_path)
        print("Beam Centre Finder Complete.\n")
    else:
        print("No input path provided.\n")
