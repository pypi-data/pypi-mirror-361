"""
XDS Input Module
================

This module provides tools for managing and modifying XDS input files (`XDS.INP`). It automates the correction and
updating of these files based on metadata and user-specified parameters, streamlining crystallographic data processing
workflows.

Features:
    - Locate and set up directories for XDS input files.
    - Update experimental parameters in `XDS.INP` files, such as detector settings, image ranges, unit cell constants.
    - Batch processing of multiple `XDS.INP` files for corrections and compatibility.
    - Graphical user interface (GUI) for managing keywords in `XDS.INP` files with autocomplete functionality.
    - Validation utilities to ensure the correctness of input parameters.

Dependencies:
    - Standard Libraries:
        - `configparser`
        - `glob`
        - `collections.Counter`
        - `os`
        - `re`
        - `shutil`
    - Third-party Libraries:
        - `fabio`

Classes:
    - `AutocompleteEntry`: A GUI entry widget with autocomplete functionality for keywords.
    - `BaseTab`: Base class for managing the layout and behavior of the AddTab and DeleteTab in the GUI.
    - `AddTab`: Handles adding new keywords to `XDS.INP` files.
    - `DeleteTab`: Handles deleting keywords from `XDS.INP` files.
    - `CalibrateTab`: Manages detector calibration parameters through the GUI.
    - `KeywordManagerApp`: Main GUI application for managing `XDS.INP` keywords and calibration.

Functions:
    - `find_xds_inp_paths(input_path: str, path_filter: bool) -> Tuple[Dict[str, str], List[str]]`:
      Finds `XDS.INP` file paths within a directory.
    - `setup_xds_directory(img_folder_paths: List[str], paths_dict: Dict[str, str]) -> List[str]`:
      Creates or updates directories for XDS processing.
    - `update_xds_files(work_path: List[str]) -> None`:
      Updates `XDS.INP` files with image-related metadata.
    - `update_img_info(xds_inp_file: str) -> None`:
      Updates the image information in a given `XDS.INP` file.
    - `write_xds_file(input_path: str, settings_file_path: str, path_filter: bool) -> None`:
      Writes and sets up `XDS.INP` files in a directory.
    - `instamatic_modify(file_path: str) -> None`:
      Modifies `XDS.INP` files for compatibility with Instamatic data collection.
    - `cell_correct(folder_path: str, path_filter: bool) -> None`:
      Updates cell and space group information in `XDS.INP` files based on a configuration file.
    - `validate_data(keyword: str, value: str) -> str`:
      Validates the provided keyword and value against predefined rules.
    - `create_keyword_manager_app(xds_list: List[str]) -> None`:
      Launches the GUI for managing keywords in `XDS.INP` files.

Usage:
    - To set up XDS input files for data processing:
        ```python
        from xds_input_module import write_xds_file
        write_xds_file(input_path="/path/to/data", settings_file_path="/path/to/settings.txt")
        ```
    - To launch the GUI for editing `XDS.INP` files:
        ```python
        from xds_input_module import create_keyword_manager_app
        create_keyword_manager_app(["/path/to/XDS.INP"])
        ```

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen and Lei Wang
    - License: BSD 3-clause
"""
from __future__ import annotations

import configparser
import glob
import os.path
from typing import List, Dict

import fabio
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QTabWidget,
    QCheckBox,
    QDoubleSpinBox,
    QCompleter, QFormLayout, QDialogButtonBox,
)

from .util import *
from .symm_shelx.space_group_finder import DEFAULT_SGC

spgfinder = DEFAULT_SGC

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, '..', 'setting.ini'))

max_core = config["XDSInput"]["max_core"]
max_job = config["XDSInput"]["max_job"]


def find_xds_inp_paths(input_path: str, path_filter: bool = False) -> tuple:
    """Finds XDS.INP file paths in the specified directory.

    Args:
        input_path (str): Directory containing image folders.
        path_filter (bool, optional): Whether to filter paths. Defaults to False.

    Returns:
        tuple: A dictionary mapping image folder paths to XDS.INP paths and a list of image folder paths.
    """
    paths_dict = {}
    img_folder_paths = find_folders_with_images(input_path, path_filter=path_filter)
    for path in img_folder_paths:
        possible_locations = [path, os.path.dirname(path), os.path.join(path, 'xds')]
        for loc in possible_locations:
            if os.path.exists(os.path.join(loc, 'XDS.INP')):
                paths_dict[path] = os.path.join(loc, 'XDS.INP')
                break
    return paths_dict, img_folder_paths


def setup_xds_directory(img_folder_paths: List[str], paths_dict: Dict[str, str]) -> List[str]:
    """Sets up the XDS directory for image folders.

    Args:
        img_folder_paths (List[str]): List of image folder paths.
        paths_dict (Dict[str, str]): Mapping of image folder paths to XDS.INP paths.

    Returns:
        List[str]: List of paths to newly created XDS.INP files.
    """
    work_path = []
    for path in img_folder_paths:
        if path not in paths_dict:
            xds_dir = os.path.join(path, 'xds')
            os.makedirs(xds_dir, exist_ok=True)
            xds_inp_path = os.path.join(xds_dir, 'XDS.INP')
            shutil.copy(os.path.join(script_dir, "_XDSINP"), xds_inp_path)
            print(f'{os.path.abspath(xds_dir)} xds created.')
            work_path.append(xds_inp_path)
    return work_path


def update_xds_files(work_path: List[str]) -> None:
    """Updates XDS.INP files with image information.

    Args:
        work_path (List[str]): List of paths to XDS.INP files.
    """
    for xds_inp_file in work_path:
        update_img_info(xds_inp_file)


def update_img_info(xds_inp_file: str) -> None:
    """Updates image-specific information in an XDS.INP file.

    Args:
        xds_inp_file (str): Path to the XDS.INP file to update.
    """
    parent_path = os.path.abspath(os.path.join(xds_inp_file, "../../"))
    image_files = sorted(glob.glob(os.path.join(parent_path, '*.img')))
    if not image_files:
        return

    template, start, end = extract_pattern(image_files)
    template = f"../{os.path.basename(template)}" if config["XDSInput"]["use_relative_path"] else template
    start = max(start, 1)

    try:
        start_angle = fabio.open(image_files[0]).header.get("PHI", "0.0")
    except Exception as e:
        print(f"{xds_inp_file} cannot be created due to {e}")
        os.remove(xds_inp_file)
        return

    with open(xds_inp_file, 'r+', errors="replace") as file:
        content = file.read().replace('{$1}', f"{max_job}").replace('{$2}', f"{max_core}")
        file.seek(0)
        file.write(content)
        file.truncate()

    with open(xds_inp_file, 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if "NAME_TEMPLATE_OF_DATA_FRAMES=" in line:
                lines[i] = f" NAME_TEMPLATE_OF_DATA_FRAMES= {template}  SMV\n"
            elif any(key in line for key in ["DATA_RANGE=", "SPOT_RANGE=", "BACKGROUND_RANGE="]):
                lines[i] = f" {line.split('=')[0]}=  {start}  {end}\n"
            elif "STARTING_ANGLE=" in line:
                lines[i] = f" STARTING_ANGLE= {start_angle}\n"
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def update_experiment_information(
        input_path: str, xds_inp_files: List[str],
        settings_file_path: str = None) -> None:
    """Updates experiment information in XDS.INP files.

    Args:
        input_path (str): Directory containing the settings file.
        xds_inp_files (List[str]): List of paths to XDS.INP files.
        settings_file_path (str, optional): Path to the settings file. Defaults to `Input_parameters.txt`.
    """

    single_line_dict = {'NX': "NY", "QX": "QY", "ORGX": "ORGY"}
    if not settings_file_path:
        settings_file_path = os.path.join(input_path, 'Input_parameters.txt')
    with open(settings_file_path, 'r') as file:
        settings = extract_keywords(file.readlines())

    for xds_inp_file in xds_inp_files:
        if not os.path.isfile(xds_inp_file):
            continue
        with open(xds_inp_file, 'r+') as file:
            updated_settings = set()
            updated_lines = []
            lines = file.readlines()
            for line in lines:
                for key, values in settings.items():
                    if line.strip().startswith(key + "="):
                        if key in single_line_dict:
                            paired_key = single_line_dict[key]
                            line = f" {key}= {settings[key][0]} {paired_key}= {settings[paired_key][0]}\n"
                            updated_settings.add(key)
                            updated_settings.add(paired_key)
                            break
                        else:
                            line = "".join([f" {key}= {val}\n" for val in values])
                            updated_settings.add(key)
                            break
                updated_lines.append(line)

            # Append settings that weren't found and updated
            for key, values in settings.items():
                if key not in updated_settings:
                    if key in single_line_dict:
                        paired_key = single_line_dict[key]
                        updated_lines.append(f" {key}= {settings[key][0]} {paired_key}= {settings[paired_key][0]}\n")
                    else:
                        updated_lines.extend([f" {key}= {val}\n" for val in values])
            file.seek(0)
            file.writelines(updated_lines)
            file.truncate()


def write_xds_file(
        input_path: str, settings_file_path: str = None, path_filter: bool = False
) -> None:
    """Writes and sets up XDS.INP files in a directory.

    Args:
        input_path (str): Directory to process.
        settings_file_path (str, optional): Path to the settings file. Defaults to None.
        path_filter (bool, optional): Whether to filter paths. Defaults to False.
    """
    if not settings_file_path:
        settings_file_path = os.path.join(input_path, 'Input_parameters.txt')
    if not os.path.isfile(settings_file_path):
        print("The specified settings file does not exist.")
        return

    required_keys = ['NX', 'NY', 'OVERLOAD', 'QX', 'QY', 'DETECTOR_DISTANCE', 'OSCILLATION_RANGE',
                     'ROTATION_AXIS', 'X-RAY_WAVELENGTH', 'INCLUDE_RESOLUTION_RANGE']
    with open(settings_file_path, 'r') as file:
        settings = extract_keywords(file.readlines())
    missing_keys = [key for key in required_keys if not (key in settings and settings[key])]
    if missing_keys:
        print(f'Missing settings: {", ".join(missing_keys)}')
        return

    print("********************************************")
    print("*                 XDS Writer               *")
    print("********************************************\n")
    paths_dict, img_folder_paths = find_xds_inp_paths(input_path, path_filter)
    work_paths = setup_xds_directory(img_folder_paths, paths_dict)
    update_xds_files(work_paths)
    update_experiment_information(input_path, work_paths, settings_file_path)
    print("Setup complete.\n")


def extract_keywords(lines: List[str]) -> Dict[str, List[str]]:
    """Extracts key-value pairs from XDS input file lines.

    Args:
        lines (List[str]): Lines from an XDS input file.

    Returns:
        Dict[str, List[str]]: Dictionary of extracted parameters.
    """

    # pattern = r'(\b[A-Z_\'\.\-]+\b)\s*=\s*([^=]*?)(?=\b[A-Z_\'\.\-]+\b\s*=|$)'
    pattern = r'(\b[A-Z_\'\.\-\/]+\b)\s*=\s*((?:(?!\b[A-Z_\'\.\-\/]+\b=).)*?)\s*(?=\b[A-Z_\'\.\-\/]+\b\s*=|$)'
    extracted_values = {}
    for line in lines:
        line = line.split('!', 1)[0].strip()
        matches = re.findall(pattern, line)
        for key, value in matches:
            value = value.strip()
            if key in extracted_values:
                if value and value not in extracted_values[key]:
                    extracted_values[key].append(value)
            else:
                extracted_values[key] = [value] if value else []
    return extracted_values


def load_XDS_excluded_range(lines: List[str]) -> List[int]:
    """Extracts ranges to exclude from XDS.INP lines.

    Args:
        lines (List[str]): Lines from an XDS.INP file.

    Returns:
        List[int]: Excluded frame ranges.
    """
    excluded_ranges = []
    for line in lines:
        line = line.strip()
        if line.startswith("EXCLUDE_DATA_RANGE=") and not line.startswith("!"):
            start, end = map(int, line.split("=")[-1].split())
            excluded_ranges.extend(range(start, end + 1))
    return excluded_ranges


def generate_exclude_data_ranges(exclude_list: List[int]) -> List[str]:
    """Generates EXCLUDE_DATA_RANGE lines for an XDS.INP file.

    Args:
        exclude_list (List[int]): List of excluded frame numbers.

    Returns:
        List[str]: Lines for the EXCLUDE_DATA_RANGE parameter.
    """
    add_lines = []
    if exclude_list:
        start = exclude_list[0]
        prev = start
        for num in exclude_list[1:]:
            if num != prev + 1:
                if start == prev:
                    add_lines.append(f" EXCLUDE_DATA_RANGE= {start} {start}\n")
                else:
                    add_lines.append(f" EXCLUDE_DATA_RANGE= {start} {prev}\n")
                start = num
            prev = num
        if start == prev:
            add_lines.append(f" EXCLUDE_DATA_RANGE= {start} {start}\n")
        else:
            add_lines.append(f" EXCLUDE_DATA_RANGE= {start} {prev}\n")
    return add_lines


def instamatic_modify(file_path: str) -> None:
    """Modifies an XDS.INP file for compatibility with Instamatic.

    Args:
        file_path (str): Path to the XDS.INP file.
    """
    with open(file_path, 'r', errors="replace") as file:
        content = file.readlines()
    # Modify the content as require
    exist_corr = False
    new_content = []
    xds_dir = os.path.dirname(file_path)
    if os.path.isfile(os.path.join(xds_dir, 'XCORR.cbf')):
        exist_corr = True
    for line in content:
        temp_line = line.strip()
        # Replace the problematic character
        line = line.replace('�', '-')
        # Modify lines based on specific starts
        if any(temp_line.startswith(prefix) for prefix in
               ["AIR=", "SENSOR_THICKNESS=", "STRONG_PIXEL=", "MINIMUM_FRACTION_OF_BACKGROUND_REGION=",
                "BACKGROUND_PIXEL="] + (["X-GEO_CORR=", "Y-GEO_CORR="] if not exist_corr else [])):
            line = "! " + line
        elif temp_line.startswith("TRUSTED_REGION="):
            line = " TRUSTED_REGION= 0.0  1.35   !default 0.0 1.05. Corners for square detector max 0.0 1.4142\n"
        new_content.append(line)
    # Write the modified content back to the file using UTF-8 encoding
    with open(file_path, 'w') as file:
        file.writelines(new_content)


def instamatic_update(folder: str, path_filter: bool) -> None:
    """Updates all XDS.INP files in a directory for Instamatic.

    Args:
        folder (str): Directory containing XDS.INP files.
        path_filter (bool): Whether to apply filtering.
    """
    matching_files = find_files(folder, "XDS.INP", path_filter=path_filter)
    for file_path in matching_files:
        instamatic_modify(file_path)
        print(f"{file_path} from Instamatic has been updated.")
    print("All XDS.INP files have been updated.\n")


def cell_correct_folder(folder_path: str, path_filter: bool = False) -> None:
    """Corrects unit cell and space group information in XDS.INP files.

    Args:
        folder_path (str): Directory containing Cell_information.txt.
        path_filter (bool, optional): Whether to filter paths. Defaults to False.
    """
    if folder_path:
        print(f"cell_correct has received input path: {folder_path}")

        txt_path = os.path.join(folder_path, "Cell_information.txt")
        print(f"Using txt file: {txt_path}")

        try:
            with open(txt_path, 'r') as file:
                txt_content = file.readlines()
        except FileNotFoundError:
            print(f"Could not find the file: {txt_path}")
            return

        space_group_provided_by_user = None
        unitcell_provided_by_user = None

        for line in txt_content:
            if "SPACE_GROUP_NUMBER=" in line:
                space_group_provided_by_user = line.strip()
            elif "UNIT_CELL_CONSTANTS=" in line:
                unitcell_provided_by_user = line.strip()

        if not space_group_provided_by_user:
            print("There is no crystal information of space group!")
            return
        if not unitcell_provided_by_user:
            print("There is no crystal information of unit cell!")
            return

            # Find and update xds.inp in all folders
        for dirpath, dirnames, filenames in os.walk(folder_path):
            if path_filter and ("!" in dirpath or "/." in dirpath or "!" in dirnames or "/." in dirnames):
                pass
            else:
                for filename in filenames:
                    if filename.lower() == "xds.inp":
                        inp_file_path = os.path.join(dirpath, filename)
                        if not os.path.exists(os.path.join(dirpath, "BACKUP-P1")):
                            shutil.copy(inp_file_path, os.path.join(dirpath, "BACKUP-P1"))
                        with open(inp_file_path, 'r', errors="ignore") as file:
                            inp_content = file.readlines()

                        # Modify the unit cell and space group in xds.inp
                        for i, line in enumerate(inp_content):
                            if "SPACE_GROUP_NUMBER=" in line and space_group_provided_by_user:
                                inp_content[i] = space_group_provided_by_user + "\n"
                            elif "UNIT_CELL_CONSTANTS=" in line and unitcell_provided_by_user:
                                inp_content[i] = unitcell_provided_by_user + "\n"

                        # Write the changes back to xds.inp
                        with open(inp_file_path, 'w') as file:
                            file.writelines(inp_content)

        print("Finished processing all xds.inp files in the selected folder.\n")
    else:
        print("No input path provided.\n")


def cell_correct_online(xds: str, cell: str, sg: str) -> None:
    """Corrects cell parameters and space group information online.

    Args:
        xds (str): Path to the XDS.INP file.
        cell (str): Cell parameters to update.
        sg (str): Space group to update.
    """
    with open(xds, "r+") as f:
        lines = f.readlines()
        lines = replace_value(lines, "SPACE_GROUP_NUMBER", [sg], comment=False)
        lines = replace_value(lines, "UNIT_CELL_CONSTANTS", [cell], comment=False)
        f.seek(0)
        f.writelines(lines)
        f.truncate()
    print("Finished processing all xds.inp files in the selected folder.\n")


def cell_correct_batch(xds_list: List[str], cell: str, sg: str) -> None:
    """Corrects cell parameters and space group information online.

    Args:
        xds_list: List of paths to XDS.INP files.
        cell (str): Cell parameters to update.
        sg (str): Space group to update.
    """
    for xds in xds_list:
        with open(xds, "r+") as f:
            lines = f.readlines()
            lines = replace_value(lines, "SPACE_GROUP_NUMBER", [sg], comment=False)
            lines = replace_value(lines, "UNIT_CELL_CONSTANTS", [cell], comment=False)
            f.seek(0)
            f.writelines(lines)
            f.truncate()
    print("Finished processing all xds.inp files in the selected folder.\n")


def correct_xds_file_SMV(img_path: str, xds_path: str) -> None:
    """Corrects an XDS.INP file using image metadata.

    Args:
        img_path (str): Directory containing image files.
        xds_path (str): Path to the XDS.INP file.
    """
    print(f"Correct {xds_path} with \nimage in {img_path}.\n")
    replace_nx, replace_ny, replace_q, replace_d, replace_wl, replace_a = [False] * 6
    img_files = sorted(glob.glob(os.path.join(img_path, '*.img')), key=natural_sort_key)
    if len(img_files) < 10:
        print("Too few images found.")
        return
    try:
        img = fabio.open(img_files[0])
    except Exception as e:
        print(f"image file may be broken due to {e}")
        return
    header_dict = dict(img.header)
    img2 = fabio.open(img_files[-1])
    header_dict_last = dict(img2.header)
    if "PHI" in header_dict:
        try:
            osc_total = float(header_dict_last["PHI"]) - float(header_dict["PHI"])
            osc_range = round(osc_total / (len(img_files) - 1), 4)
        except KeyError:
            osc_range = None
    else:
        osc_range = None

    first_occurrence = 0
    rotation_axis_inverse = False
    with open(xds_path, "r") as _file:
        xds_lines = _file.readlines()
        xds_parameters = extract_keywords(xds_lines)
    if "SIZE1" in header_dict and int(header_dict["SIZE1"]) != int(xds_parameters["NX"][0]):
        replace_nx = True
    if "SIZE2" in header_dict and int(header_dict["SIZE2"]) != int(xds_parameters["NY"][0]):
        replace_ny = True
    if ("PIXEL_SIZE" in header_dict and float(header_dict["PIXEL_SIZE"]) != float(xds_parameters["QX"][0])
            or float(header_dict["PIXEL_SIZE"]) != float(xds_parameters["QY"][0])):
        replace_q = True
    if "DISTANCE" in header_dict and float(header_dict["DISTANCE"]) != float(xds_parameters["DETECTOR_DISTANCE"][0]):
        replace_d = True
    if "WAVELENGTH" in header_dict and float(header_dict["WAVELENGTH"]) != float(xds_parameters["X-RAY_WAVELENGTH"][0]):
        replace_wl = True
    if osc_range != 0 and osc_range != float(xds_parameters["OSCILLATION_RANGE"][0]):
        replace_a = True
    if replace_nx or replace_ny or replace_q or replace_d or replace_wl or replace_a:
        new_line = []
        for i, line in enumerate(xds_lines):
            if (replace_nx or replace_ny) and (line.strip().startswith("NX") or line.strip().startswith("NY")):
                first_occurrence = i
                if "QX" in line:
                    replace_q = True
            elif replace_q and (" QX=" in line or line.strip().startswith("QY")):
                first_occurrence = i
                if " NX=" in line:
                    replace_q = True
            elif replace_wl and line.strip().startswith("X-RAY_WAVELENGTH"):
                new_line.append(" X-RAY_WAVELENGTH= {}\n".format(header_dict["WAVELENGTH"]))
            elif replace_d and line.strip().startswith("DETECTOR_DISTANCE"):
                new_line.append(" DETECTOR_DISTANCE= {}\n".format(header_dict["DISTANCE"]))
            elif replace_a and line.strip().startswith("OSCILLATION_RANGE"):
                if osc_range > 0:
                    new_line.append(" OSCILLATION_RANGE= {}\n".format(osc_range))
                else:
                    new_line.append(" OSCILLATION_RANGE= {}\n".format(-osc_range))
                    rotation_axis_inverse = True
            else:
                new_line.append(line)
        if replace_q:
            new_line.insert(first_occurrence,
                            " QX= {}  QY= {}\n".format(header_dict["PIXEL_SIZE"], header_dict["PIXEL_SIZE"]))
        if replace_nx or replace_ny:
            new_line.insert(first_occurrence, " NX= {}  NY= {}\n".format(header_dict["SIZE1"], header_dict["SIZE2"]))
        if rotation_axis_inverse:
            rotation_axis_text = xds_parameters["ROTATION_AXIS"][0]
            rotation_axis_text_new = "  ".join(str(-float(element)) for element in rotation_axis_text.split())
            new_line = replace_value(new_line, "ROTATION_AXIS", [rotation_axis_text_new], comment=False)
        with open(xds_path, "w") as _file:
            _file.writelines(new_line)


def correct_inputs(input_path: str) -> None:
    """Processes and corrects XDS.INP files using metadata.

    Args:
        input_path (str): Directory containing image folders and XDS.INP files.
    """
    if input_path:
        print(f"Try to correct input with metadate in {input_path}")
        paths_dict = get_xds_inp_image_dict(input_path)
        for xds_path in paths_dict.keys():
            img_dir = os.path.dirname(paths_dict[xds_path]["image_path"])
            img_format = paths_dict[xds_path]["image_format"]
            if img_format == "SMV":
                print(f"Entering folder: {img_dir}")
                correct_xds_file_SMV(img_dir, xds_path)
        print(f"Finished Correct input with metadata in {input_path}.\n")


def replace_value(
        lines: List[str], keyword: str, values: List[str], comment: bool, add: bool = False
) -> List[str]:
    """Replaces or adds values for a keyword in XDS.INP lines.

    Args:
        lines (List[str]): Lines from an XDS input file.
        keyword (str): The keyword to replace or add.
        values (List[str]): Values to set for the keyword.
        comment (bool): Whether to comment out old values.
        add (bool, optional): Whether to add new entries instead of replacing. Defaults to False.

    Returns:
        List[str]: Modified lines.
    """
    keyword_eq = f"{keyword}="
    underscore_keyword_eq = f"_{keyword}="
    comment_prefix = " !" if comment else " "
    assignment_suffix = "\n"

    new_assignments = [
        f"{comment_prefix}{keyword}= {value}{assignment_suffix}"
        for value in values
    ]

    new_lines = []
    action_performed = False  # Flag to ensure single replace/add action

    for line in lines:
        contains_keyword = keyword_eq in line and underscore_keyword_eq not in line

        if contains_keyword:
            if not action_performed:
                if add:
                    new_lines.append(line)
                    new_lines.extend(new_assignments)
                else:
                    if line.count('=') >= 2:
                        temp_dict = extract_keywords([line])
                        for key, _values in temp_dict.items():
                            if key != keyword:
                                for _value in _values:
                                    new_lines.append(f"{key}={_value}{assignment_suffix}")
                    new_lines.extend(new_assignments)
                action_performed = True
            else:
                if add:
                    new_lines.append(line)
        else:
            new_lines.append(line)

    if not action_performed:
        new_lines.extend(new_assignments)

    return new_lines


def delete_xds(input_path: str) -> None:
    """Deletes XDS.INP files and related folders in a directory.

    Args:
        input_path (str): Directory containing XDS.INP files and folders.
    """
    if input_path:
        print(f"Deleted XDS files and folders in: {input_path}")
        delete_files(input_path, 'xds.inp')
        delete_folders(input_path, 'xds')
        print(f"XDS folders have been removed under the path.\n")
    else:
        print("No input path provided.")


def get_xds_inp_image_dict(input_path: str) -> Dict[str, Dict[str, str]]:
    """Retrieves a mapping of XDS.INP files to image paths and formats.

    Args:
        input_path (str): Directory containing XDS.INP files.

    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping XDS.INP paths to image information.
    """
    xds_files = find_files(input_path, "XDS.INP")
    xds_image_dict = {}
    for xds_path in xds_files:
        with open(xds_path) as _file:
            keyword_dict = extract_keywords(_file.readlines())
        if not keyword_dict["NAME_TEMPLATE_OF_DATA_FRAMES"]:
            print(f"{xds_path} is not valid. Check it carefully.")
        image_path, file_format = (" ".join(keyword_dict["NAME_TEMPLATE_OF_DATA_FRAMES"][0].split()[:-1]),
                                   keyword_dict["NAME_TEMPLATE_OF_DATA_FRAMES"][0].split()[-1])
        if "?" in file_format:
            image_path = file_format
            file_format = "SMV"
        if not (image_path.startswith("/") or image_path.startswith("~")):
            xds_dir = os.path.dirname(xds_path)
            image_path = os.path.abspath(os.path.join(xds_dir, image_path))
        xds_image_dict[xds_path] = {"image_path": image_path,
                                    "image_format": file_format}
    return xds_image_dict


def change_path_input(input_path: str, mode: str = "absolute") -> None:
    """Changes paths in XDS.INP files to absolute or relative.

    Args:
        input_path (str): Directory containing XDS.INP files.
        mode (str): Path mode ("absolute" or "relative"). Defaults to "absolute".
    """
    xds_image_dict = get_xds_inp_image_dict(input_path)
    for xds_path in xds_image_dict.keys():
        if not os.path.isdir(os.path.dirname(xds_image_dict[xds_path]["image_path"])):
            image_list = find_folders_with_images(os.path.dirname(xds_path))
            if not image_list:
                image_list = find_folders_with_images(os.path.dirname(os.path.dirname(xds_path)))
            if not image_list:
                image_list = find_folders_with_images(os.path.dirname(os.path.dirname(os.path.dirname(xds_path))))
            try:
                xds_image_dict[xds_path]["image_path"] = os.path.join(
                    image_list[0], os.path.basename(xds_image_dict[xds_path]["image_path"]))
            except IndexError:
                print(f"No image folder found for {xds_path}")
                continue
        else:
            img_files = sorted(glob.glob(
                os.path.join(os.path.dirname(xds_image_dict[xds_path]["image_path"]), '*.img')), key=natural_sort_key)
            file_groups = {}
            for file in img_files:
                filename = os.path.basename(file)
                # Check if the filename ends with a digit before .mrc
                if re.search(r'\d+\.img$', filename):
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
            img_files = sorted(max_group, key=natural_sort_key)
            if len(xds_image_dict[xds_path]["image_path"]) != len(img_files[0]):
                (xds_image_dict[xds_path]["image_path"], xds_image_dict[xds_path]["start"],
                 xds_image_dict[xds_path]["end"]) = extract_pattern(img_files)
        with open(xds_path, "r+", errors="replace") as f:
            if mode == "absolute":
                path = os.path.abspath(xds_image_dict[xds_path]["image_path"])
            elif mode == "relative":
                path = os.path.relpath(xds_image_dict[xds_path]["image_path"], os.path.dirname(xds_path))
            lines = f.readlines()
            lines = replace_value(lines,
                                  "NAME_TEMPLATE_OF_DATA_FRAMES",
                                  ["{} {}".format(path, xds_image_dict[xds_path]["image_format"])],
                                  comment=False)
            if "start" in xds_image_dict[xds_path]:
                lines = replace_value(lines,
                                      "DATA_RANGE",
                                      ["{} {}".format(xds_image_dict[xds_path]["start"],
                                                      xds_image_dict[xds_path]["end"])],
                                      comment=False)
                lines = replace_value(lines,
                                      "SPOT_RANGE",
                                      ["{} {}".format(xds_image_dict[xds_path]["start"],
                                                      xds_image_dict[xds_path]["end"])],
                                      comment=False)
                lines = replace_value(lines,
                                      "BACKGROUND_RANGE",
                                      ["{} {}".format(xds_image_dict[xds_path]["start"],
                                                      xds_image_dict[xds_path]["end"])],
                                      comment=False)
            f.seek(0)
            f.writelines(lines)
            f.truncate()


class AutocompleteLineEdit(QLineEdit):
    def __init__(self, keyword_list, parent=None):
        super().__init__(parent)

        # Create a QCompleter for the given list of keywords:
        self.completer = QCompleter(keyword_list, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setMaxVisibleItems(5)
        self.setCompleter(self.completer)
        self.completer.popup().setStyleSheet("""
                    QAbstractItemView {
                        font-size: 16px;  /* Font size for dropdown list */
                        background-color: white;  /* Background color */
                        selection-background-color: lightblue;
                    }
                """)


class BaseTab(QWidget):
    """
    Base class for AddTab and DeleteTab to reduce redundancy, adapted for PyQt6.
    """

    def __init__(self, keywords: List[str], max_rows: int = 8, has_value: bool = True, parent=None):
        super().__init__(parent)
        self.keywords = keywords
        self.max_rows = max_rows
        self.has_value = has_value

        self.rows = []  # Each row is a dict: {"autocomplete": QLineEdit, "value": QLineEdit, ...}

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Buttons at the top
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addLayout(self.button_layout)

        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.setStyleSheet("padding: 5px 10px;")
        self.add_row_button.clicked.connect(self.add_row)
        self.button_layout.addWidget(self.add_row_button)
        self.button_layout.addSpacing(20)

        self.delete_row_button = QPushButton("Delete Row")
        self.delete_row_button.setStyleSheet("padding: 5px 10px;")
        self.delete_row_button.clicked.connect(self.delete_row)
        self.button_layout.addWidget(self.delete_row_button)
        self.button_layout.addSpacing(20)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_rows)
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addStretch()

        # Container layout for row entries
        self.rows_container = QVBoxLayout()
        self.main_layout.addLayout(self.rows_container)
        self.main_layout.addStretch()

        # Start with 3 rows
        for _ in range(3):
            self.add_row()

    def add_row(self):
        if len(self.rows) >= self.max_rows:
            QMessageBox.warning(
                self,
                "Maximum Rows Reached",
                f"Cannot add more than {self.max_rows} rows."
            )
            return

        row_layout = QHBoxLayout()
        row_data = {}

        # Autocomplete line edit
        autocomplete = AutocompleteLineEdit(self.keywords)
        row_layout.addWidget(autocomplete)
        row_data["autocomplete"] = autocomplete

        if self.has_value:
            # equals label
            eq_label = QLabel("=")
            eq_label.setFont(QFont("Liberation Sans", 15))
            row_layout.addWidget(eq_label)

            # Value entry
            value_edit = QLineEdit()
            value_edit.setFont(QFont("Liberation Sans", 15))
            row_layout.addWidget(value_edit)
            row_data["value"] = value_edit

        self.rows_container.addLayout(row_layout)
        row_data["layout"] = row_layout
        self.rows.append(row_data)

    def delete_row(self):
        if len(self.rows) < 2:
            # For safety, disallow going below 1 row (or adapt to your preference)
            return

        # Delete the last unfilled row
        for row in reversed(self.rows):
            key_text = row["autocomplete"].text().strip()
            val_text = row["value"].text().strip() if self.has_value else ""

            if not key_text and not val_text:
                # remove from layout
                layout_to_remove = row["layout"]
                while layout_to_remove.count():
                    item = layout_to_remove.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

                self.rows_container.removeItem(layout_to_remove)
                self.rows.remove(row)
                return

        QMessageBox.information(self, "No Unfilled Rows", "There are no unfilled rows to delete.")

    def reset_rows(self):
        for row in self.rows:
            row["autocomplete"].clear()
            if self.has_value:
                row["value"].clear()

    def get_data(self) -> List[Dict[str, str]]:
        data = []
        key_incomplete = []
        value_incomplete = []

        for row in self.rows:
            key_txt = row["autocomplete"].text().strip()
            val_txt = row["value"].text().strip() if self.has_value else ""

            if self.has_value:
                # We require both key and value if it has_value
                if key_txt and val_txt:
                    data.append({"key": key_txt, "value": val_txt})
                elif key_txt:
                    key_incomplete.append(key_txt)
                elif val_txt:
                    value_incomplete.append(val_txt)
            else:
                if key_txt:
                    data.append({"key": key_txt, "value": ""})

        if self.has_value and (key_incomplete or value_incomplete):
            QMessageBox.warning(
                self,
                "Warning",
                f"You have {len(key_incomplete)} values and {len(value_incomplete)} keywords unfilled."
            )
            return "error"

        return data


class AddTab(BaseTab):
    """Tab for adding keywords with corresponding values."""

    def __init__(self, keywords: List[str], parent=None):
        super().__init__(keywords, has_value=True, parent=parent)


class DeleteTab(BaseTab):
    """Tab for deleting keywords (no value)."""

    def __init__(self, keywords: List[str], parent=None):
        super().__init__(keywords, has_value=False, parent=parent)


class CalibrateTab(QWidget):
    """
    Tab for calibrating detector parameters within the GUI.
    """

    def __init__(self, keywords: List[str], xds_list: List[str], parent=None):
        super().__init__(parent)
        self.keywords = keywords
        self.xds_list = xds_list
        self.calibration_entries = {}  # Maps float camera length -> QDoubleSpinBox (ratio)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Buttons: Load / Clean
        btn_layout = QHBoxLayout()
        self.main_layout.addLayout(btn_layout)

        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_calibration)
        btn_layout.addWidget(self.load_btn)

        self.clean_btn = QPushButton("Clean")
        self.clean_btn.clicked.connect(self.clean_calibration)
        btn_layout.addWidget(self.clean_btn)

        # Description
        desc_label = QLabel(
            "Calibration Ratio will be > 1 when the measured cell is larger than the ideal one."
        )
        desc_label.setWordWrap(True)
        self.main_layout.addWidget(desc_label)

        # Universe Ratio / Distance Factor
        ratio_layout = QHBoxLayout()
        self.main_layout.addLayout(ratio_layout)

        ulab = QLabel("Universe Ratio:")
        ulab.setFont(QFont("Liberation Sans", 15))
        ratio_layout.addWidget(ulab)

        self.universe_ratio_box = QDoubleSpinBox()
        self.universe_ratio_box.setValue(1.00)
        self.universe_ratio_box.setDecimals(5)
        self.universe_ratio_box.setSingleStep(0.01)
        ratio_layout.addWidget(self.universe_ratio_box)

        dlab = QLabel("Distance Factor:")
        dlab.setFont(QFont("Liberation Sans", 15))
        ratio_layout.addWidget(dlab)

        self.distance_factor_box = QDoubleSpinBox()
        self.distance_factor_box.setValue(1.00)
        self.distance_factor_box.setDecimals(3)
        self.distance_factor_box.setSingleStep(0.01)
        ratio_layout.addWidget(self.distance_factor_box)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(sep)

        # Vertical layout for dynamic camera-length entries
        self.cl_entries_layout = QVBoxLayout()
        self.main_layout.addLayout(self.cl_entries_layout)
        self.main_layout.addStretch()

    def load_calibration(self):
        cl_dict = self.get_detector_distances(self.xds_list)
        unique_cl = set(cl_dict.values())
        unique_count = len(unique_cl)

        if unique_count > 5:
            QMessageBox.warning(
                self,
                "Too Many Camera Lengths",
                f"Too many different Camera Lengths: {unique_count} kinds."
            )
            return

        # Clear existing
        for i in reversed(range(self.cl_entries_layout.count())):
            item = self.cl_entries_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.cl_entries_layout.removeItem(item)

        self.calibration_entries.clear()

        distance_factor = self.distance_factor_box.value()
        if distance_factor == 0:
            QMessageBox.critical(self, "Invalid Input", "Distance Factor cannot be zero.")
            return

        universe_ratio = self.universe_ratio_box.value()

        # Create entries for each unique camera length
        for cl in unique_cl:
            # Real CL
            cl_real = cl / distance_factor

            row_layout = QHBoxLayout()

            label = QLabel(f"CL {cl_real:.2f} mm, Ratio:")
            label.setFont(QFont("Liberation Sans", 15))
            row_layout.addWidget(label)

            ratio_box = QDoubleSpinBox()
            ratio_box.setValue(universe_ratio)
            ratio_box.setDecimals(5)
            ratio_box.setSingleStep(0.01)
            row_layout.addWidget(ratio_box)

            # Container widget to hold this row
            container = QWidget()
            container.setLayout(row_layout)
            self.cl_entries_layout.addWidget(container)

            # Store in dict
            self.calibration_entries[cl] = ratio_box

    def clean_calibration(self):
        for i in reversed(range(self.cl_entries_layout.count())):
            item = self.cl_entries_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.cl_entries_layout.removeItem(item)

        self.calibration_entries.clear()
        self.universe_ratio_box.setValue(1.00)
        self.distance_factor_box.setValue(1.00)

    def get_calibration_data(self) -> Dict[float, float]:
        """
        Return {original_CL: ratio} for each camera length.
        """
        data = {}
        for cl, ratio_box in self.calibration_entries.items():
            data[cl] = ratio_box.value()
        return data

    def has_calibration_changes(self) -> bool:
        if abs(self.universe_ratio_box.value() - 1.0) > 1e-9:
            return True
        if abs(self.distance_factor_box.value() - 1.0) > 1e-9:
            return True
        for box in self.calibration_entries.values():
            if abs(box.value() - 1.0) > 1e-9:
                return True
        return False

    def get_detector_distances(self, xds_list: List[str]) -> Dict[str, float]:
        """Retrieves the detector distances from XDS.INP files.

        Args:
            xds_list (List[str]): List of XDS.INP file paths.

        Returns:
            Dict[str, float]: Dictionary mapping XDS.INP paths to detector distances.
        """
        detector_distances = {}
        for xds_inp in xds_list:
            try:
                with open(xds_inp, 'r') as file:
                    keyword_temp = extract_keywords(file.readlines())
                    distance = float(keyword_temp["DETECTOR_DISTANCE"][0])
                    detector_distances[xds_inp] = distance
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read {xds_inp}: {e}")
        return detector_distances


class KeywordManagerApp(QDialog):
    """
    Main application (QDialog) for managing keywords in XDS.INP files.
    Replaces the tkinter-based KeywordManagerApp.
    """

    def __init__(self, xds_list: List[str], parent=None):
        super().__init__(parent)
        self.xds_list = xds_list

        self.setWindowTitle("Keyword Manager")
        self.resize(700, 700)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Title label
        title_lbl = QLabel(
            "Add, Replace or Delete Keywords in XDS.INPs.\n"
            "The Keyword Entry has AutoComplete Function."
        )
        title_lbl.setWordWrap(True)
        self.main_layout.addWidget(title_lbl)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        keywords = self.get_keywords()

        # Add tab
        self.add_tab = AddTab(keywords)
        self.tab_widget.addTab(self.add_tab, "Add")

        # Delete tab
        self.delete_tab = DeleteTab(keywords)
        self.tab_widget.addTab(self.delete_tab, "Delete")

        # Calibrate tab
        self.calibrate_tab = CalibrateTab(keywords, self.xds_list)
        self.tab_widget.addTab(self.calibrate_tab, "Calibrate")

        # Bottom layout with 'Force Replace' checkbox, Cancel, and Save
        bottom_layout = QHBoxLayout()
        self.main_layout.addLayout(bottom_layout)

        self.force_replace_chk = QCheckBox("Force Replace")
        bottom_layout.addWidget(self.force_replace_chk)

        # Save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        bottom_layout.addWidget(self.save_btn)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_data)
        bottom_layout.addWidget(self.cancel_btn)

        self.apply_modern_style()

    def apply_modern_style(self):
        """Apply a simple modern QSS-based style to the dialog."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f5f5f5;
            }

            QLabel {
                font-size: 16px;
                color: #333;
            }
            QAbstractItemView {
                font-size: 14px;  /* Font size for dropdown list */
                background-color: white;  /* Background color */
                selection-background-color: lightblue;  /* Selected item background */
                selection-color: black;  /* Selected item text color */
                border: 1px solid gray;  /* Border */
                padding: 3px; /* Padding around text */
            }
            QLineEdit {
                font-size: 16px;  /* Font size for input text */
                padding: 5px;  /* Padding inside the box */
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #fff;
            }

            QTabBar::tab {
                background-color: #e2e2e2;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 16px;
            }

            QTabBar::tab:selected {
                background-color: #fff;
                border-bottom: 1px solid #fff;
            }

            QCheckBox {
                font-size: 14px;
                color: #333;
                padding: 4px;
            }
            """
        )

    def get_keywords(self) -> List[str]:
        """
        Equivalent to the original classmethod get_keywords().
        You can customize the list as needed.
        """
        return [
            "MAXIMUM_NUMBER_OF_JOBS", "MAXIMUM_NUMBER_OF_PROCESSORS", "SECONDS",
            "NUMBER_OF_IMAGES_IN_CACHE", "TEST", "OVERLOAD", "GAIN",
            "TRUSTED_REGION", "VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS",
            "INCLUDE_RESOLUTION_RANGE", "MINIMUM_ZETA", "ORGX", "ORGY",
            "ROTATION_AXIS", "WFAC1", "FRACTION_OF_POLARIZATION", "AIR",
            "FRIEDEL'S_LAW", "MAX_CELL_AXIS_ERROR", "MAX_CELL_ANGLE_ERROR",
            "TEST_RESOLUTION_RANGE", "MIN_RFL_Rmeas", "MAX_FAC_Rmeas",
            "NBX", "NBY", "BACKGROUND_PIXEL", "STRONG_PIXEL",
            "MAXIMUM_NUMBER_OF_STRONG_PIXELS", "MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT",
            "MAXIMUM_IMAGE_GAP_FOR_ADDING_PARTIALS", "SPOT_MAXIMUM-CENTROID",
            "RGRID", "SEPMIN", "CLUSTER_RADIUS", "INDEX_ERROR",
            "INDEX_MAGNITUDE", "INDEX_QUALITY", "MERGE_TREE",
            "MAXIMUM_ERROR_OF_SPOT_POSITION", "MAXIMUM_ERROR_OF_SPINDLE_POSITION",
            "MINIMUM_FRACTION_OF_INDEXED_SPOTS", "DEFAULT_REFINE_SEGMENT",
            "MINIMUM_I/SIGMA", "REFLECTING_RANGE", "REFLECTING_RANGE_E.S.D.",
            "BEAM_DIVERGENCE", "MINPK", "BEAM_DIVERGENCE_E.S.D.",
            "RELRAD", "RELBET", "NUMBER_OF_PROFILE_GRID_POINTS_ALONG_ALPHA/BETA",
            "NUMBER_OF_PROFILE_GRID_POINTS_ALONG_GAMMA", "CUT",
            "DELPHI", "SIGNAL_PIXEL", "NBATCH", "STRICT_ABSORPTION_CORRECTION",
            "SNRC", "BATCHSIZE", "REFLECTIONS/CORRECTION_FACTOR",
            "DETECTOR_DISTANCE", "UNIT_CELL_CONSTANTS",
            "UNTRUSTED_RECTANGLE", "UNTRUSTED_ELLIPSE", "UNTRUSTED_QUADRILATERAL",
            "EXCLUDE_RESOLUTION_RANGE", "JOB", 'SPACE_GROUP_NUMBER'
        ]

    @pyqtSlot()
    def save_data(self):
        """
        Handles validation and saving from all tabs or calibration, emulating
        the same flow as the tkinter-based code.
        """
        add_data = self.add_tab.get_data()
        delete_data = self.delete_tab.get_data()
        calibration_active = self.calibrate_tab.has_calibration_changes()

        if add_data == "error" or delete_data == "error":
            return

        force_replace = self.force_replace_chk.isChecked()

        add_delete_active = ((add_data != "error" and add_data) or
                             (delete_data != "error" and delete_data))

        # If user has something in Add/Delete plus something in Calibrate => conflict
        if add_delete_active and calibration_active:
            QMessageBox.warning(
                self,
                "Operation Conflict",
                "Add/Delete Keyword cannot perform at the same time with Calibration."
            )
            return

        # If we are Add/Delete
        if add_delete_active:
            # Simple validation check (placeholder)
            ret = QMessageBox.question(
                self,
                "Add/Delete Keywords",
                f"{len(add_data)} Parameters will be "
                f"{'replaced' if force_replace else 'added'}\n"
                f"and {len(delete_data)} Parameters will be muted.\n\n"
                "Continue?"
            )
            if ret == QMessageBox.StandardButton.Yes:
                self.process_save(add_data, delete_data, force_replace, self.xds_list)
                self.close()
            return

        # If we are calibrating
        if calibration_active:
            calibration_data = self.calibrate_tab.get_calibration_data()
            if not calibration_data:  # or if it's 'error'
                return
            universe_ratio = self.calibrate_tab.universe_ratio_box.value()
            distance_factor = self.calibrate_tab.distance_factor_box.value()

            details = ""
            for cl, ratio in calibration_data.items():
                cl_real = cl / distance_factor
                details += f"CL {cl_real:.2f} mm: {ratio:.4f}\n"

            ret = QMessageBox.question(
                self,
                "Calibrate Keywords",
                f"Calibration will be applied with Universe Ratio = {universe_ratio:.4f} "
                f"under Distance Factor = {distance_factor:.3f}.\n\n"
                f"Camera Length Ratios:\n{details}\nDo you wish to continue?"
            )
            if ret == QMessageBox.StandardButton.Yes:
                self.calibrate_CL(calibration_data, universe_ratio)
                self.close()
            return

        # Else, no operation
        QMessageBox.information(self, "No Action", "No data to save.")

    def process_save(self, add_data, delete_data, force_replace, xds_list):
        """
        Save add_data and delete_data changes to the XDS.INP files.
        Emulates the original process_save logic.
        """
        for xds_inp in xds_list:
            try:
                with open(xds_inp, "r+") as f:
                    lines = f.readlines()

                    # handle add_data
                    for d in add_data:
                        lines = replace_value(
                            lines,
                            d["key"],
                            [d["value"]],
                            comment=False,
                            add=(not force_replace and validate_data(d["key"], d["value"]) == "pass-multi")
                        )
                    # handle delete_data
                    for d in delete_data:
                        lines = replace_value(
                            lines,
                            d["key"],
                            [d["value"]],
                            comment=True
                        )

                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save {xds_inp}: {str(e)}")

    def calibrate_CL(self, calibration_data: Dict[float, float], universe_ratio: float):
        """
        Applies calibration changes to XDS.INP files for DETECTOR_DISTANCE.
        If no per-CL data is provided, uses universe_ratio.
        """
        if calibration_data:
            # Actual per-CL logic
            cl_dict = self.get_detector_distances(self.xds_list)
            for path, camera_length in cl_dict.items():
                with open(path, "r+") as f:
                    lines = f.readlines()
                    lines = replace_value(
                        lines,
                        "DETECTOR_DISTANCE",
                        [f"{camera_length / calibration_data[camera_length]:.2f}"],
                        comment=False
                    )
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()
        else:
            # Universe ratio only
            cl_dict = self.get_detector_distances(self.xds_list)
            for path, camera_length in cl_dict.items():
                with open(path, "r+") as f:
                    lines = f.readlines()
                    lines = replace_value(
                        lines,
                        "DETECTOR_DISTANCE",
                        [f"{camera_length / universe_ratio:.2f}"],
                        comment=False
                    )
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()

    def cancel_data(self):
        """
        Equivalent to cancel button: ask user to confirm.
        """
        ret = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to discard and close?"
        )
        if ret == QMessageBox.StandardButton.Yes:
            self.close()

    def get_detector_distances(self, xds_list: List[str]) -> Dict[str, float]:
        """Retrieves the detector distances from XDS.INP files.

        Args:
            xds_list (List[str]): List of XDS.INP file paths.

        Returns:
            Dict[str, float]: Dictionary mapping XDS.INP paths to detector distances.
        """
        detector_distances = {}
        for xds_inp in xds_list:
            try:
                with open(xds_inp, 'r') as file:
                    keyword_temp = extract_keywords(file.readlines())
                    distance = float(keyword_temp["DETECTOR_DISTANCE"][0])
                    detector_distances[xds_inp] = distance
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read {xds_inp}: {e}")
        return detector_distances


def create_keyword_manager_app(xds_list: List[str]) -> None:
    dialog = KeywordManagerApp(xds_list)
    dialog.exec()


def validate_data(keyword: str, value: str) -> str:
    """Validates a keyword and its value.

    Args:
        keyword (str): Keyword to validate.
        value (str): Associated value.

    Returns:
        str: Validation result ("fix", "pass-single", "pass-multi", "value-err", or "wrong").
    """
    keyword_dict = {
        "fix": [
            "CLUSTER_NODES",
            "DETECTOR",
            "NX",
            "NY",
            "QX",
            "QY",
            "MINIMUM_VALID_PIXEL_VALUE",
            "SILICON",
            "SENSOR_THICKNESS",
            "ROFF",
            "TOFF",
            "STOE_CALIBRATION_PARAMETERS",
            "BRASS_PLATE_IMAGE",
            "HOLE_DISTANCE",
            "MXHOLE",
            "MNHOLE",
            "X-GEO_CORR",
            "Y-GEO_CORR",
            "DARK_CURRENT_IMAGE",
            "OFFSET",
            "DIRECTION_OF_DETECTOR_X-AXIS",
            "DIRECTION_OF_DETECTOR_Y-AXIS",
            "SEGMENT",
            "REFINE_SEGMENT",
            "DIRECTION_OF_SEGMENT_X-AXIS",
            "DIRECTION_OF_SEGMENT_Y-AXIS",
            "SEGMENT_ORGX",
            "SEGMENT_ORGY",
            "SEGMENT_DISTANCE",
            "OSCILLATION_RANGE",
            "STARTING_ANGLE",
            "STARTING_FRAME",
            "STARTING_ANGLES_OF_SPINDLE_ROTATION",
            "TOTAL_SPINDLE_ROTATION_RANGES",
            "RESOLUTION_SHELLS",
            "X-RAY_WAVELENGTH",
            "INCIDENT_BEAM_DIRECTION",
            "POLARIZATION_PLANE_NORMAL",
            "UNIT_CELL_A-AXIS",
            "UNIT_CELL_B-AXIS",
            "UNIT_CELL_C-AXIS",
            "REIDX",
            "INDEX_ORIGIN",
            "PROFILE_FITTING",
            "PATCH_SHUTTER_PROBLEM",
            "CORRECTIONS",
            "REFERENCE_DATA_SET",
            "FIT_B-FACTOR_TO_REFERENCE_DATA_SET",
            "REJECT_ALIEN",
            "DATA_RANGE_FIXED_SCALE_FACTOR",
            "NAME_TEMPLATE_OF_DATA_FRAMES",
            "LIB",
            "DATA_RANGE",
            "EXCLUDE_DATA_RANGE",
            "SPOT_RANGE",
            "BACKGROUND_RANGE",
            "MINIMUM_NUMBER_OF_REFLECTIONS/SEGMENT",
        ],
        "single_value": [
            "MAXIMUM_NUMBER_OF_JOBS",
            "MAXIMUM_NUMBER_OF_PROCESSORS",
            "SECONDS",
            "NUMBER_OF_IMAGES_IN_CACHE",
            "TEST",
            "OVERLOAD",
            "GAIN",
            "TRUSTED_REGION",
            "VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS",
            "INCLUDE_RESOLUTION_RANGE",
            "MINIMUM_ZETA",
            "ORGX",
            "ORGY",
            "ROTATION_AXIS",
            "WFAC1",
            "FRACTION_OF_POLARIZATION",
            "AIR",
            "FRIEDEL'S_LAW",
            "MAX_CELL_AXIS_ERROR",
            "MAX_CELL_ANGLE_ERROR",
            "TEST_RESOLUTION_RANGE",
            "MIN_RFL_Rmeas",
            "MAX_FAC_Rmeas",
            "NBX",
            "NBY",
            "BACKGROUND_PIXEL",
            "STRONG_PIXEL",
            "MAXIMUM_NUMBER_OF_STRONG_PIXELS",
            "MINIMUM_NUMBER_OF_PIXELS_IN_A_SPOT",
            "MAXIMUM_IMAGE_GAP_FOR_ADDING_PARTIALS",
            "SPOT_MAXIMUM-CENTROID",
            "RGRID",
            "SEPMIN",
            "CLUSTER_RADIUS",
            "INDEX_ERROR",
            "INDEX_MAGNITUDE",
            "INDEX_QUALITY",
            "MERGE_TREE",
            "MAXIMUM_ERROR_OF_SPOT_POSITION",
            "MAXIMUM_ERROR_OF_SPINDLE_POSITION",
            "MINIMUM_FRACTION_OF_INDEXED_SPOTS",
            "DEFAULT_REFINE_SEGMENT",
            "MINIMUM_I/SIGMA",
            "REFLECTING_RANGE",
            "REFLECTING_RANGE_E.S.D.",
            "BEAM_DIVERGENCE",
            "MINPK",
            "BEAM_DIVERGENCE_E.S.D.",
            "RELRAD",
            "RELBET",
            "NUMBER_OF_PROFILE_GRID_POINTS_ALONG_ALPHA/BETA",
            "NUMBER_OF_PROFILE_GRID_POINTS_ALONG_GAMMA",
            "CUT",
            "DELPHI",
            "SIGNAL_PIXEL",
            "NBATCH",
            "STRICT_ABSORPTION_CORRECTION",
            "SNRC",
            "BATCHSIZE",
            "REFLECTIONS/CORRECTION_FACTOR",
            "DETECTOR_DISTANCE",
            "UNIT_CELL_CONSTANTS",
            'SPACE_GROUP_NUMBER'
        ],
        "multi_value": [
            "UNTRUSTED_RECTANGLE",
            "UNTRUSTED_ELLIPSE",
            "UNTRUSTED_QUADRILATERAL",
            "EXCLUDE_RESOLUTION_RANGE",
            "JOB",
        ],
    }

    value_num = {
        "JOB": 0,
        "TRUSTED_REGION": 2,
        "UNTRUSTED_RECTANGLE": 4,
        "UNTRUSTED_ELLIPSE": 4,
        "UNTRUSTED_QUADRILATERAL": 8,
        "VALUE_RANGE_FOR_TRUSTED_DETECTOR_PIXELS": 2,
        "INCLUDE_RESOLUTION_RANGE": 2,
        "EXCLUDE_RESOLUTION_RANGE": 2,
        "ROTATION_AXIS": 3,
        "UNIT_CELL_CONSTANTS": 6,
        "TEST_RESOLUTION_RANGE": 2,
    }

    if keyword in keyword_dict["fix"]:
        return "fix"

    if keyword in keyword_dict["single_value"] or keyword in keyword_dict["multi_value"]:
        split_value = value.split()
        expected_num = value_num.get(keyword)

        if expected_num is None:
            return (
                "pass-single"
                if keyword in keyword_dict["single_value"]
                else "pass-multi"
            )

        if len(split_value) == expected_num or expected_num == 0:
            return (
                "pass-single"
                if keyword in keyword_dict["single_value"]
                else "pass-multi"
            )
        else:
            return "value-err"
    return "wrong"


def read_cRED_log(file_path: str) -> int:
    """Reads a cRED log file and extracts the total number of frames and images.

    Args:
        file_path (str): Path to the cRED log file.

    Returns:
        int: Total number of frames and images combined.
    """
    frames = 0
    images = 0
    with open(file_path, 'r', errors="ignore") as file:
        for line in file.readlines():
            if "Number of frames" in line:
                frames = int(line.split(":")[1].strip())
            elif "Number of images" in line:
                images = int(line.split(":")[1].strip())

    return frames + images


class SgUnitCellDialog(QDialog):
    """Simple dialog to input Space Group and Unit Cell values."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Edit SG and Unit Cell")
        self.setModal(True)

        # Provide more space for the Unit Cell input
        self.setMinimumWidth(400)

        layout = QFormLayout(self)
        self.sg_edit = QLineEdit(self)
        self.cell_edit = QLineEdit(self)
        self.cell_edit.setMinimumWidth(600)
        layout.addRow("SG:", self.sg_edit)
        layout.addRow("Unit Cell:", self.cell_edit)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_accept(self) -> None:
        sg_text = self.sg_edit.text().strip()
        cell_text = self.cell_edit.text().strip()
        if sg_text:
            try:
                self.space_group_num = spgfinder.get_int_number(sg_text)
                self.sg_name = spgfinder.get_int_short(sg_text)
            except Exception as e:
                QMessageBox.critical(self.window(), "Error", f"Invalid space group: {e}")
                return
        if not sg_text or not cell_text or len(cell_text.split()) != 6:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please fill in both Space Group and Unit Cell before proceeding.",
            )
            return
        self.accept()
