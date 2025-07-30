import configparser
import glob
import os
from concurrent.futures import ThreadPoolExecutor
import random

import fabio
import numpy as np
from scipy.ndimage import binary_closing
from scipy.optimize import minimize
from skimage import exposure, measure, filters, draw
from skimage.morphology import remove_small_objects
from tqdm import tqdm

from ..util import natural_sort_key, remove_outliers_iqr
from ..xds_input import get_xds_inp_image_dict, replace_value

script_dir = os.path.dirname(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])


def analysis_beam_stop(image_path: str) -> tuple:
    """
    Analyzes an IMG file to find the beam stop position and radius.

    Args:
        image_path (str): Path to the IMG file.

    Returns:
        tuple: (centre, beam_stop_pos, beam_stop_r, angle_degrees) where:
            - centre: (x_center, y_center) of the beam [float, float]
            - beam_stop_pos: (x_pos, y_pos) of the beam stop [float, float]
            - beam_stop_r: radius of the beam stop [float]
            - angle_degrees: angle of the beam stop direction in degrees [float]
            Returns (None, None, None, None) if detection fails.
    """
    # Read image
    image_data = fabio.open(image_path).data.astype(np.uint16)
    # Enhance contrast
    image_data_autocontrast = exposure.equalize_hist(image_data)

    # Apply a high threshold to find bright regions (assumed direct beam area)
    threshold_value = np.percentile(image_data_autocontrast, 97.5)
    binary_image_bright_regions = image_data_autocontrast > threshold_value

    # Label the connected components for bright regions
    label_image_bright = measure.label(binary_image_bright_regions)
    regions_bright = measure.regionprops(label_image_bright)

    if not regions_bright:
        return None, None, None, None

    # Find the largest bright region, assumed the main direct beam area
    largest_bright_region = max(regions_bright, key=lambda r: r.area)
    min_row, min_col, max_row, max_col = largest_bright_region.bbox

    # Center of the main bright region
    centre = (0.5 * (min_col + max_col), 0.5 * (min_row + max_row))

    # Crop out the main bright region
    central_bright_region = image_data_autocontrast[min_row:max_row, min_col:max_col]

    # Prepare an inverted version for subsequent analysis
    inverted_central_bright_region = 1 - central_bright_region

    # Segment out dark regions within the bright region by Otsu's threshold
    otsu_threshold = filters.threshold_otsu(central_bright_region)
    binary_dark_central_otsu = central_bright_region < otsu_threshold

    # Morphological closing to reduce noise, and remove small objects
    binary_dark_central_cleaned = binary_closing(binary_dark_central_otsu, np.ones((3, 3)))
    binary_dark_central_cleaned = remove_small_objects(binary_dark_central_cleaned, min_size=5)

    # Label the connected components (dark patches in the bright region)
    label_image_dark_central_cleaned = measure.label(binary_dark_central_cleaned)
    regions_dark_central_cleaned = measure.regionprops(label_image_dark_central_cleaned)

    if not regions_dark_central_cleaned:
        return None, None, None, None

    # Find the largest dark patch, presumably the beam stop
    largest_dark_patch = max(regions_dark_central_cleaned, key=lambda r: r.area)
    coords = largest_dark_patch.coords

    # Approximate radius of that dark patch (ellipse -> average of major/minor axis)
    yc, xc = np.mean(coords, axis=0)
    a = largest_dark_patch.major_axis_length / 2
    b = largest_dark_patch.minor_axis_length / 2
    refined_circle_radius = (a + b) / 2

    # Refine location using the centroid of the detected region
    cy, cx = largest_dark_patch.centroid
    ig_yc = (cy + yc) / 2
    ig_xc = (cx + xc) / 2

    def intensity_sum(params: tuple) -> float:
        """
        A function to be minimized, summing pixel intensities inside a disk
        of a given radius in the inverted image.

        Args:
            params: (y_center, x_center, radius)

        Returns:
            float: Negative of sum of intensities inside the disk (to maximize).
        """
        _yc, _xc, radius = params
        rr, cc = draw.disk(
            center=(int(_yc), int(_xc)),
            radius=int(radius),
            shape=inverted_central_bright_region.shape
        )
        # The negative sign is because we want to maximize the sum of the
        # (inverted) intensities, which is equivalent to minimizing its negative.
        return -np.sum(inverted_central_bright_region[rr, cc]) / (radius ** 1.8)

    # Use the initial guess for the optimization
    initial_guess = [ig_yc, ig_xc, refined_circle_radius]
    result = minimize(intensity_sum, initial_guess, method='Nelder-Mead', options={'maxiter': 100})
    refined_yc, refined_xc, refined_circle_radius = result.x

    # Convert beam stop position back to the coordinate system of the original image
    beam_stop_pos = (refined_xc + min_col, refined_yc + min_row)
    beam_stop_r = refined_circle_radius + 0.015 * image_data.shape[0]

    # Determine the slope and direction (use negative to measure direction "away" from center)
    angle_radians = np.arctan2(-(refined_yc - ig_yc), -(refined_xc - ig_xc))
    angle_degrees = np.degrees(angle_radians)

    return centre, beam_stop_pos, beam_stop_r, angle_degrees if angle_degrees >= -90 else angle_degrees + 180


def process_folder_beam_stop(img_path: str, xds_path: str, max_files: int = 20) -> None:
    """
    Processes a folder of IMG files to calculate beam stop information.

    Args:
        img_path (str): Directory containing IMG files.
        xds_path (str): Path to the XDS.INP file.
        max_files (int, optional): Maximum number of files to process. Defaults to 20.
    """
    img_files = sorted(glob.glob(os.path.join(img_path, '*.img')), key=natural_sort_key)
    if not img_files:
        print("No images found in that folder, please check if your path in XDS.INP is correct.\n")
        return None

    # If there are more than max_files, sample max_files evenly
    if len(img_files) > max_files + 100:
        img_files = random.sample(img_files[10:-10], max_files + 20)
    elif len(img_files) > max_files + 50:
        img_files = random.sample(img_files[10:-10], max_files + 10)
    elif len(img_files) > max_files + 20:
        img_files = random.sample(img_files[10:-10], max_files)
    elif len(img_files) > max_files + 10:
        img_files = random.sample(img_files[5:-5], max_files)
    elif len(img_files) > max_files:
        img_files = random.sample(img_files, max_files)

    size = fabio.open(img_files[0]).data.shape[0]

    with ThreadPoolExecutor(max_workers=set_max_worker) as executor:
        results = list(tqdm(executor.map(analysis_beam_stop, img_files),
                            total=len(img_files), desc="Processing images", ascii=True))

    centre_xs, centre_ys, beam_stop_pos_xs, beam_stop_pos_ys, beam_stop_rs, angle_degrees = [], [], [], [], [], []
    for centre, beam_stop_pos, beam_stop_r, angle in results:
        if centre:
            centre_xs.append(centre[0])
            centre_ys.append(centre[1])
        if beam_stop_pos:
            beam_stop_pos_xs.append(beam_stop_pos[0])
            beam_stop_pos_ys.append(beam_stop_pos[1])
        if beam_stop_r:
            beam_stop_rs.append(beam_stop_r)
        if angle:
            angle_degrees.append(angle)

    filtered_centre_xs = remove_outliers_iqr(centre_xs)
    filtered_centre_ys = remove_outliers_iqr(centre_ys)
    filtered_beam_stop_pos_xs = remove_outliers_iqr(beam_stop_pos_xs)
    filtered_beam_stop_pos_ys = remove_outliers_iqr(beam_stop_pos_ys)
    filtered_beam_stop_rs = remove_outliers_iqr(beam_stop_rs)
    filtered_angle_degrees = angle_degrees

    update_beam_stop_file(
        img_path,
        (np.average(filtered_centre_xs), np.average(filtered_centre_ys)),
        (np.average(filtered_beam_stop_pos_xs), np.average(filtered_beam_stop_pos_ys)),
        np.average(filtered_beam_stop_rs),
        np.average(filtered_angle_degrees),
    )

    update_xds_inp_beam_stop(
        xds_path,
        size,
        (np.average(filtered_centre_xs), np.average(filtered_centre_ys)),
        (np.average(filtered_beam_stop_pos_xs), np.average(filtered_beam_stop_pos_ys)),
        np.average(filtered_beam_stop_rs),
        np.average(filtered_angle_degrees),
    )

    print("Beam Stop Information Collected.\n")
    return


def update_beam_stop_file(
        img_directory: str,
        centre: tuple,
        beam_stop_pos: tuple,
        beam_stop_r: np.floating,
        angle_degrees: np.floating) -> None:
    """
    Writes the beam stop information to a text file in the image directory.

    Args:
        img_directory (str): Directory containing IMG files.
        centre (tuple): Center of the beam.
        beam_stop_pos (tuple): Position of the beam stop.
        beam_stop_r (np.floating): Radius of the beam stop.
        angle_degrees (np.floating): Angle of the beam stop direction in degrees.
    """
    centers_file_path = os.path.join(img_directory, 'beam_stop_info.txt')
    if angle_degrees < -120 or angle_degrees > 120:
        direction = "x-"
    elif -60 < angle_degrees < 60:
        direction = "x+"
    else:
        direction = "undetermined direction"
    print(f"Est. beam center: ({centre[0]:.2f}, {centre[1]:.2f})")
    with open(centers_file_path, 'w') as file:
        file.write(f"Est. beam center: ({centre[0]}, {centre[1]})\n")
        file.write(f"Average beam stop position: ({beam_stop_pos[0]}, {beam_stop_pos[1]})\n")
        file.write(f"Average beam stop radius: {beam_stop_r}\n")
        file.write(f"Beam Stop Position: {direction}\n")


def update_xds_inp_beam_stop(
        xds_inp_path: str,
        size: int,
        centre: tuple,
        beam_stop_pos: tuple,
        beam_stop_r: np.floating,
        angle_degrees: np.floating
) -> None:
    """
    Updates the XDS.INP file with beam stop information.

    Args:
        xds_inp_path (str): Path to the XDS.INP file.
        size (int): Size of the image.
        centre (tuple): Center of the beam.
        beam_stop_pos (tuple): Position of the beam stop.
        beam_stop_r (float): Radius of the beam stop.
        angle_degrees (float): Angle of the beam stop direction in degrees.
    """
    if os.path.exists(xds_inp_path):
        with open(xds_inp_path, 'r+', errors="replace") as file:
            lines = file.readlines()
            lines = replace_value(lines, "ORGX", [f"{centre[0]:.3f}"], False)
            lines = replace_value(lines, "ORGY", [f"{centre[1]:.3f}"], False)
            lines = replace_value(lines, "UNTRUSTED_ELLIPSE",
                                  [f"{beam_stop_pos[0] - beam_stop_r:.0f} {beam_stop_pos[0] + beam_stop_r:.0f} "
                                   f"{beam_stop_pos[1] - beam_stop_r:.0f} {beam_stop_pos[1] + beam_stop_r:.0f}"],
                                  False)
            if angle_degrees < -120 or angle_degrees > 120:
                area = (f"0  {beam_stop_pos[0]:.0f}  "
                        f"{beam_stop_pos[1] - 0.5 * beam_stop_r:.0f}  {beam_stop_pos[1] + 0.5 * beam_stop_r:.0f}")
                lines = replace_value(lines, "UNTRUSTED_RECTANGLE", [area], False)
            elif -60 < angle_degrees < 60:
                area = (f"{beam_stop_pos[0]:.0f}  {size:.0f}  "
                        f"{beam_stop_pos[1] - 0.5 * beam_stop_r:.0f}  {beam_stop_pos[1] + 0.5 * beam_stop_r:.0f}")
                lines = replace_value(lines, "UNTRUSTED_RECTANGLE", [area], False)
            file.seek(0)
            file.writelines(lines)
            file.truncate()


def beam_stop_calculate(input_path: str) -> None:
    """
    Calculates the beam stop position for all IMG files in a directory.

    Args:
        input_path (str): Directory containing IMG files.
    """
    if input_path:
        print("\n********************************************")
        print("*            Beam Centre Finder            *")
        print("*--------   w/ Beam Stop Version   --------*")
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
                process_folder_beam_stop(img_dir, xds_path)
        print("*** Beam Stop Calculation Complete. ***\n")
    else:
        print("No input path provided.\n")



