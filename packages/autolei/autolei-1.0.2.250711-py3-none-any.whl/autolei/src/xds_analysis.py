"""
XDS Analysis Module
===================

This module provides tools for analyzing XDS (X-ray Detector Software) output files and performing crystallographic
data processing. It extracts metadata, computes statistical measures, processes unit cell parameters, and handles
batch datasets for high-throughput crystallographic analysis.

Overview:
    The XDS Analysis Module simplifies the handling of `.LP` and `.HKL` files by extracting meaningful crystallographic
    statistics, enabling comprehensive analysis. It supports tasks such as parsing indexing and scaling files,
    processing spot and integration data, and generating metadata summaries for large datasets.

Features:
    - Parse and analyze XDS output files like `IDXREF.LP`, `XSCALE.LP`, and `CORRECT.LP`.
    - Extract unit cell parameters, rotation axis, completeness, R factors, and more.
    - Load and process spot and scale factor data for visualization or further refinement.
    - Generate metadata summaries for batch datasets in JSON format.
    - Analyze HKL files for lattice symmetry and reflection statistics.

Attributes:
    config (ConfigParser): Configuration settings loaded from `setting.ini`.
    set_max_worker (int): Maximum number of threads for processing.
    bool_use_short_name (bool): Flag to determine short naming conventions.
    engine_hkl_analysis (str): Default analysis engine for HKL files.
    is_MM (bool): Flag indicating whether molecular mechanics (MM) is enabled.

Dependencies:
    - Standard Libraries:
        - `configparser`, `glob`, `json`, `os`, `re`, `warnings`
        - `concurrent.futures` (for multi-threading)
        - `functools` (for caching)
    - Third-Party Libraries:
        - `fabio`, `pandas`, `numpy`, `scipy`
    - Custom Modules:
        - `.analysis_hkl`: Handles HKL file processing and symmetry tests.
        - `.util`: Utility functions for file handling and path operations.
        - `.xds_input`: Extracts keywords from XDS input files.

Usage:
    This module is designed to be used in automated workflows for processing XDS outputs. It can also be utilized
    interactively for specific analyses, such as examining individual LP or HKL files.

    Example:
        ```python
        from xds_analysis_module import analysis_folder, extract_run_result

        # Analyze an entire folder of XDS outputs
        merged_params, dataset_count = analysis_folder("/path/to/xds/outputs")

        # Extract detailed run results from a specific directory
        run_results = extract_run_result("/path/to/specific/xds_run")
        ```

Notes:
    - Ensure the `setting.ini` and other required configuration files are correctly set up in the module's directory.
    - Batch processing relies on consistent directory organization for XDS output files.
    - This module is designed to handle errors gracefully during batch processing, ensuring interruptions are minimized.

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen and Lei Wang
    - License: BSD 3-clause
"""

import configparser
import glob
import json
import os
import re
import warnings
from concurrent.futures import as_completed, ProcessPoolExecutor
from functools import lru_cache

import fabio
import pandas as pd

try:
    from numpy.exceptions import ComplexWarning
except ImportError:
    from numpy import ComplexWarning

from .analysis_hkl import analysis_xds_hkl, test_lattice_symmetry_hkl
from .util import find_folders_with_images, natural_sort_key, strtobool
from .xds_input import extract_keywords

warnings.simplefilter(action='ignore', category=ComplexWarning)

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])
bool_use_short_name = strtobool(config["XDSRunner"]["use_short_path"])
engine_hkl_analysis = config["XDSRunner"]["engine_hkl_analysis"]
is_MM = strtobool(config["General"]["is_MM"])

if not strtobool(config["General"]["multi-process"]):
    set_max_worker = 1


def analysis_idxref_lp(idxref_lp: str) -> dict:
    """Analyzes an `IDXREF.LP` file to extract indexing statistics and unit cell parameters.

    Args:
        idxref_lp (str): Path to the `IDXREF.LP` file.

    Returns:
        dict: Contains indexing statistics, spot numbers, index numbers, unit cell parameters,
        cell coordinates, rotation axis, and alternative solutions if any.
        Returns `None` if the file does not exist or contains errors.
    """
    if not os.path.exists(idxref_lp):
        return {}
    parameters = {
        "spot_number": None,
        "index_number": 0,
        "unit_cell_index": [],
        "cell_coordinates": [],
        "rotation_axis": [],
        "other_solution": []
    }

    with open(idxref_lp, 'r') as file:
        lines = file.readlines()

    integration_section = False
    warning_section = False
    input_section = True
    input_lines = []

    for line in lines:
        if "!!! ERROR !!!" in line:
            print("The indexing process was interrupted or produced poor results.")
            return {}
        if "***** DIFFRACTION PARAMETERS USED AT START OF INTEGRATION *****" in line:
            integration_section = True
            warning_section = False
        if "!!! WARNING !!! SOLUTION MAY NOT BE UNIQUE" in line:
            warning_section = True
            integration_section = False
        if "AUTOINDEXING IS BASED ON" in line:
            input_section = False
            spot_number = int(line.split()[4])
            parameters["spot_number"] = spot_number

        if input_section:
            input_lines.append(line)

        if integration_section:
            if "REFINED VALUES OF DIFFRACTION PARAMETERS DERIVED FROM" in line:
                index_number = int(line.split()[-3])
                parameters["index_number"] = index_number
            if "UNIT CELL PARAMETERS" in line:
                unit_cell_parameters = list(map(float, line.split()[3:]))
                parameters["unit_cell_index"] = unit_cell_parameters
            if "COORDINATES OF UNIT CELL A-AXIS" in line:
                a_axis = list(map(float, line.split()[5:8]))
                parameters["cell_coordinates"].append(a_axis)
            if "COORDINATES OF UNIT CELL B-AXIS" in line:
                b_axis = list(map(float, line.split()[5:8]))
                parameters["cell_coordinates"].append(b_axis)
            if "COORDINATES OF UNIT CELL C-AXIS" in line:
                c_axis = list(map(float, line.split()[5:8]))
                parameters["cell_coordinates"].append(c_axis)
            if "LAB COORDINATES OF ROTATION AXIS" in line:
                rotation_axis = list(map(float, line.split()[5:8]))
                parameters["rotation_axis"] = rotation_axis

        if warning_section:
            if "UNIT_CELL_A-AXIS=" in line:
                a_axis = list(map(float, line.split('=')[1].split()))
                parameters["other_solution"].append(a_axis)
            if "UNIT_CELL_B-AXIS=" in line:
                b_axis = list(map(float, line.split('=')[1].split()))
                parameters["other_solution"].append(b_axis)
            if "UNIT_CELL_C-AXIS=" in line:
                c_axis = list(map(float, line.split('=')[1].split()))
                parameters["other_solution"].append(c_axis)

        # Group other_solution into 3x3 matrices
    if len(parameters["other_solution"]) % 3 == 0:
        other_solution_grouped = [parameters["other_solution"][i:i + 3] for i in
                                  range(0, len(parameters["other_solution"]), 3)]
        parameters["other_solution"] = other_solution_grouped
    return parameters


def analysis_xscale_lp(xscale_lp: str) -> dict:
    """Analyzes an `XSCALE.LP` file to extract scaling statistics.

    Args:
        xscale_lp (str): Path to the `XSCALE.LP` file.

    Returns:
        dict: Contains extracted statistical data including resolution, number of observations,
        completeness, R factors, ISa measurements, CC1/2, input file paths, average unit cell
        dimensions, and their standard deviations.
    """
    info_dict = {}
    input_files = []
    found_statistics = False
    with open(xscale_lp, "r") as f:
        lines = f.readlines()
        for line in lines:
            if "INPUT_FILE=" in line:
                input_files.append(line.strip().split("=")[-1])
            if "STATISTICS OF SCALED OUTPUT DATA SET : all.HKL" in line:
                found_statistics = True
            if found_statistics:
                if "*" in line and "**" not in line and "total" not in line:
                    resolution_str = line.strip().split()[0]
                    info_dict["resolution"] = float(resolution_str)
                if line.strip().startswith("total"):
                    summary_line = line.strip()
                    break
    if not summary_line:
        print(f"Warning: No summary line found in {xscale_lp}.")
        return {}
    info_dict["N_obs"] = int(summary_line.split()[1])
    info_dict["N_uni"] = int(summary_line.split()[2])
    info_dict["completeness"] = float(summary_line.split()[4].replace('%', ''))
    info_dict["R_exp"] = float(summary_line.split()[6].replace('%', ''))
    info_dict["ISa_meas"] = float(summary_line.split()[8])
    info_dict["R_meas"] = float(summary_line.split()[9].replace('%', ''))
    info_dict["CC1/2"] = float(summary_line.split()[10].replace('*', ''))
    info_dict["input"] = sorted(input_files, key=natural_sort_key)
    info_dict["unit_cell"], info_dict["unit_cell_esd"], _ = get_avg_esd_cell(
        "", multi=True, mode="list", folder_list=[os.path.dirname(path) for path in info_dict["input"]])
    return info_dict


def analysis_correct_lp(correct_lp: str) -> dict:
    """Parses a `CORRECT.LP` file to extract crystallographic parameters and statistics.

    Args:
        correct_lp (str): Path to the `CORRECT.LP` file.

    Returns:
        dict: Contains parameters such as number of observations, completeness, R factors,
        ISa measurements, CC1/2, resolution, unit cell parameters, wavelength, mosaicity,
        and detector information.
    """
    info_dict = {}
    with open(correct_lp, "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "WILSON STATISTICS OF DATA SET" in line:
            info_dict["resolution"] = 99.0
            info_dict["N_obs"] = int(lines[i - 12].split()[1])
            info_dict["N_uni"] = int(lines[i - 12].split()[2])
            info_dict["completeness"] = float(lines[i - 12].split()[4].replace('%', ''))
            info_dict["R_exp"] = float(lines[i - 12].split()[6].replace('%', ''))
            info_dict["ISa_meas"] = float(lines[i - 12].split()[8])
            info_dict["R_meas"] = float(lines[i - 12].split()[9].replace('%', ''))
            info_dict["CC1/2"] = float(lines[i - 12].split()[10].replace('*', ''))

            for j in range(1, len(lines)):
                if i - j - 13 < 0:
                    break
                elif not lines[i - j - 12].strip():
                    if info_dict["resolution"] == 99.0:
                        info_dict["resolution"] = 5.0
                    break
                elif "*" in lines[i - j - 12]:
                    resolution_str = lines[i - j - 12].strip().split()[0]
                    info_dict["resolution"] = float(resolution_str)
                elif info_dict["resolution"] != 99.0:
                    info_dict["resolution"] = 99.0
        elif "a        b          ISa" in line:
            info_dict["ISa_model"] = float(lines[i + 1].strip().split()[2])
        elif "UNIT CELL PARAMETERS" in line:
            cell = line.strip().split()[3:]
            info_dict["unit_cell"] = [float(value) for value in cell]
            for j, element in enumerate(info_dict["unit_cell"]):
                if element in [90.0, 120.0]:
                    info_dict["unit_cell"][j] = int(info_dict["unit_cell"][j])
        elif "E.S.D. OF CELL PARAMETERS" in line:
            cell_esd = line.strip().split()[4:]
            if len(cell_esd) == 6:
                info_dict["unit_cell_esd"] = [float(value) for value in cell_esd]
            else:
                info_dict["unit_cell_esd"] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        elif "X-RAY_WAVELENGTH=" in line:
            info_dict["wavelength"] = float(line.strip().split("=")[-1].strip())
        elif "REFINED VALUES OF DIFFRACTION PARAMETERS" in line:
            pattern = r"FROM\s+(\d+)\s+INDEXED"
            match = re.search(pattern, line)
            info_dict["cell_rfl_num"] = int(match.group(1))
        elif "NAME_TEMPLATE_OF_DATA_FRAMES=" in line and False:
            image_path_dir = os.path.dirname(line.split("=")[1].strip().split()[0])
            if not image_path_dir.startswith("/"):
                image_path_dir = os.path.join(os.path.dirname(correct_lp), image_path_dir)
            info_dict["image_folder"] = image_path_dir
        elif "OSCILLATION_RANGE=" in line:
            info_dict["step"] = float(line.strip().split("=")[-1].strip())
        elif "DATA_RANGE=" in line and "frames" not in info_dict:
            start, end = map(int, line.strip().split("=")[-1].strip().split())
            info_dict["frames"] = end - start + 1
        elif "STARTING_ANGLE=" in line:
            info_dict["start_angle"] = float(line.strip().split("=")[1].strip().split()[0])
        elif "DETECTOR_DISTANCE=" in line:
            info_dict["camera_length"] = float(line.strip().split("=")[-1].strip())
        elif "QX=" in line and "pixel_size" not in info_dict:
            values = re.findall(r"(NX|NY|QX|QY)=\s*([0-9.]+)", line)
            values_dict = {key: float(value) for key, value in values}
            info_dict["pixel_size"] = float(values_dict.get("QX"))
    return info_dict


def get_avg_esd_cell(
        file_folder: str, multi: bool = False, mode: str = "folder", folder_list: list = None
) -> tuple:
    """Computes average unit cell parameters and their standard deviations (E.S.D.).

    Args:
        file_folder (str): Directory containing XDS files.
        multi (bool, optional): If `True`, averages across multiple datasets. Defaults to `False`.
        mode (str, optional): Mode of processing. Defaults to `"folder"`.
        folder_list (list, optional): List of folders to process. Defaults to `None`.

    Returns:
        tuple: Average unit cell dimensions, their E.S.D.s, and the wavelength used.
    """
    if mode == "folder":
        xds_folder = []
        if multi:
            with open(os.path.join(file_folder, "XSCALE.INP"), "r") as f:
                for line in f.readlines():
                    if line.strip().startswith("INPUT_FILE="):
                        xds_folder.append(os.path.dirname((line.strip().split("=")[1])))
        else:
            xds_folder.append(file_folder)
    else:
        xds_folder = folder_list
    cell_list = []
    error_list = []
    for path in xds_folder:
        correct_lp = os.path.join(path, "CORRECT.LP")
        if os.path.isfile(correct_lp):
            with open(correct_lp) as f:
                lines = f.readlines()
                for line in lines:
                    if "UNIT CELL PARAMETERS" in line:
                        cell = line.strip().split()[3:]
                        cell_list.append([float(value) for value in cell])
                    elif "E.S.D. OF CELL PARAMETERS" in line:
                        cell_esd = line.strip().split()[4:]
                        try:
                            error_list.append([float(value) for value in cell_esd])
                        except:
                            error_list.append([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
                    elif "X-RAY_WAVELENGTH=" in line:
                        wavelength = line.strip().split("=")[-1].strip()
        else:
            continue
    avg_cell = []
    esd_cell = []

    for param_index in range(6):
        weights = [1 / (error ** 2) if error != 0 else 1 for error in [errors[param_index] for errors in error_list]]
        sum_weight = sum(weights) if sum(weights) != 0 else 1
        values = [values[param_index] for values in cell_list]
        weighted_average = sum(w * v for w, v in zip(weights, values)) / sum_weight
        weighted_variance = sum(w * ((v - weighted_average) ** 2) for w, v in zip(weights, values)) / sum_weight
        weighted_std_dev = weighted_variance ** 0.5 / (len(cell_list) ** 0.5 if len(cell_list) > 1 else 1)

        avg_cell.append(weighted_average)
        esd_cell.append(weighted_std_dev)
    return avg_cell, esd_cell, wavelength


def load_list_integrate_lp(lines: list, pos: int) -> dict:
    """Extracts specific data from an integration LP file at a given position.

    Args:
        lines (list): Lines from an XDS integration LP file.
        pos (int): Position index of the data to extract within each relevant line.

    Returns:
        dict: Maps image numbers to the extracted values based on the specified position.
    """
    scales = {}
    in_image_block = False
    for line in lines:
        line = line.strip()
        if line.startswith("IMAGE IER  SCALE") or line.startswith("IMAGE IER    SCALE"):
            in_image_block = True
        elif not line:
            in_image_block = False
        elif line.startswith("!!!"):
            in_image_block = False
        elif in_image_block:
            parts = line.split()
            image_number = int(parts[0])
            scale_factor = float(parts[pos])
            scales[image_number] = scale_factor
    return scales


def load_scale_list(lines: list) -> dict:
    """Extracts scale factors from an integration LP file.

    Args:
        lines (list): Lines from an XDS integration LP file.

    Returns:
        dict: Maps image numbers to their scale factors.
    """
    return load_list_integrate_lp(lines, 2)


def load_divergence_list(lines: list) -> dict:
    """Extracts divergence values from an integration LP file.

    Args:
        lines (list): Lines from an XDS integration LP file.

    Returns:
        dict: Maps image numbers to their divergence values.
    """
    return load_list_integrate_lp(lines, 8)


def load_mosaicity_list(lines: list) -> dict:
    """Extracts mosaicity values from an integration LP file.

    Args:
        lines (list): Lines from an XDS integration LP file.

    Returns:
        dict: Maps image numbers to their mosaicity values.
    """
    return load_list_integrate_lp(lines, 9)


def load_bkg_scale(lines: list) -> dict:
    """Parses background scale factors from a specific section within XDS output files.

    Args:
        lines (list): Lines from an XDS output file.

    Returns:
        dict: Maps image numbers to background scale factors.
    """
    scales = {}
    in_image_block = False
    for line in lines:
        line = line.strip()
        if line.startswith("FRAME #    SCALE     COUNTS"):
            in_image_block = True
        elif not line:
            in_image_block = False
        elif in_image_block:
            parts = line.split()
            image_number = int(parts[0])
            scale_factor = float(parts[1])
            scales[image_number] = scale_factor
    return scales


def load_spot_binned(spot_xds: str) -> pd.DataFrame:
    """Loads and bins spot data from an XDS spot file.

    Args:
        spot_xds (str): Path to the XDS spot file.

    Returns:
        pd.DataFrame: DataFrame containing binned spot data with counts of total and unindexed
        spots per rebinned frame.
    """
    data = pd.read_csv(spot_xds, delim_whitespace=True, header=None)
    headers = ['X', 'Y', 'frame', 'intensity', 'h', 'k', 'l']
    data.columns = headers
    data['rebinned_frame'] = data['frame'].apply(lambda x: int(x + 0.5))

    rebinned_data = data.groupby('rebinned_frame').size().reset_index(name='count')
    unindexed_rebinned_count = data[(data['h'] == 0) & (data['k'] == 0) & (data['l'] == 0)].groupby(
        'rebinned_frame').size().reset_index(name='unindexed_count')

    final_data = pd.merge(rebinned_data, unindexed_rebinned_count, on='rebinned_frame', how='left').fillna(0)
    return final_data


def process_file(file_path: str) -> dict:
    """Processes an XDS file to extract and parse keywords.

    Args:
        file_path (str): Path to the XDS file.

    Returns:
        dict: Extracted keywords from the file.
    """
    try:
        content = get_file_contents(file_path)
        return extract_keywords(content.splitlines())
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {}


def find_xds_files(folder_path: str) -> list:
    """Finds all `XDS.INP` files within a folder path.

    Args:
        folder_path (str): Directory to search for `XDS.INP` files.

    Returns:
        list: List of paths to `XDS.INP` files.
    """
    xds_files = []
    for root, dirs, files in os.walk(folder_path, topdown=True):
        for file in files:
            if file.lower() == "xds.inp":
                xds_files.append(os.path.join(root, "XDS.INP"))
    return xds_files


@lru_cache(maxsize=None)
def get_file_contents(file_path: str) -> str:
    """
    Returns the contents of a file located at the specified path.

    Parameters:
        file_path: str
            The path to the file whose contents are to be retrieved.

    Returns:
        str
            The contents of the specified file as a string.
    """
    with open(file_path, "r", errors="ignore") as f:
        return f.read()


def analysis_folder(folder_path: str) -> tuple:
    """Aggregates parameters from all XDS input files in a directory.

    Args:
        folder_path (str): Directory containing `XDS.INP` files.

    Returns:
        tuple: Contains a dictionary of merged parameters that are consistent across datasets
        and the count of datasets processed.
    """
    showing_parameters = [
        'NX', 'NY', 'QX', 'QY', 'OVERLOAD', 'INCLUDE_RESOLUTION_RANGE',
        'ORGX', 'ORGY', 'DETECTOR_DISTANCE', 'OSCILLATION_RANGE',
        'ROTATION_AXIS', 'X-RAY_WAVELENGTH', "UNTRUSTED_RECTANGLE",
        "UNTRUSTED_ELLIPSE", "UNTRUSTED_QUADRILATERAL", "EXCLUDE_RESOLUTION_RANGE",
        "SIGNAL_PIXEL"
    ]

    input_parameters_path = os.path.join(folder_path, "Input_parameters.txt")
    dataset_number = len(find_folders_with_images(folder_path))  # Assuming optimized

    if os.path.exists(input_parameters_path):
        with open(input_parameters_path, "r") as f:
            extracted_values = extract_keywords(f.readlines())
        if any(extracted_values.values()):
            print(f"Load information from Input_parameters.txt in {folder_path}.")
            return extracted_values, dataset_number

    # Collect all XDS.INP files using optimized scandir
    xds_files = find_xds_files(folder_path)

    if not xds_files:
        print(f"No XDS.INP files found in {folder_path}.")
        return {}, dataset_number

    print(f"Load information from XDS.INP in {folder_path}.")

    parameter_dicts = []

    with ProcessPoolExecutor(max_workers=set_max_worker) as executor:
        futures = {executor.submit(process_file, fp): fp for fp in xds_files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                parameter_dicts.append(result)

    if not parameter_dicts:
        print(f"No valid data extracted from XDS.INP files in {folder_path}.")
        return {}, dataset_number

    # Initialize dictionary to collect values for each parameter
    showing_parameters_values = {key: [] for key in showing_parameters}

    for param_dict in parameter_dicts:
        for key in showing_parameters:
            value = param_dict.get(key)
            if isinstance(value, list):
                value = tuple(value)
            showing_parameters_values[key].append(value)

    # Merge parameters that have the same value across all datasets
    merged_dict = {}
    for key, values in showing_parameters_values.items():
        # Remove None values for uniformity check
        filtered_values = [v for v in values if v is not None]
        if not filtered_values:
            continue
        first_value = filtered_values[0]
        if all(v == first_value for v in filtered_values):
            # Convert back to list if original value was a tuple
            merged_dict[key] = list(first_value) if isinstance(first_value, tuple) else first_value

    return merged_dict, dataset_number


def collect_metadata(input_path: str) -> None:
    """Gathers and organizes metadata from image folders and XDS files into a JSON file.

    Args:
        input_path (str): Directory containing image folders and `XDS.INP` files.

    Returns:
        None: Saves metadata as `metadata.json` in the specified `input_path`.
    """
    paths_dict = {}
    result_dict = {}
    img_folder_paths = sorted(find_folders_with_images(input_path), key=natural_sort_key)
    for path in img_folder_paths:
        if os.path.exists(os.path.join(path, 'XDS.INP')):
            paths_dict[path] = path
        elif os.path.exists(os.path.join(os.path.dirname(path), 'XDS.INP')):
            paths_dict[path] = os.path.join(os.path.dirname(path))
        elif os.path.exists(os.path.join(path, 'xds', 'XDS.INP')):
            paths_dict[path] = os.path.join(path, 'xds')
    for img_path, xds_dir in paths_dict.items():
        info_dict = extract_run_result(xds_dir)
        result_dict[xds_dir] = info_dict
        print(f"Metadata extracts successfully on {xds_dir}.")
    with open(os.path.join(input_path, "metadata.json"), "w") as json_file:
        json.dump(result_dict, json_file, indent=4)
        print(f"Metadata information is extracted and saved in {input_path}.")


def extract_run_result(xds_dir: str, engine: str = engine_hkl_analysis) -> dict:
    """Extracts and processes run results from the specified XDS directory.

    Args:
        xds_dir (str): Directory containing XDS output files.
        engine (str, optional): Analysis engine to use (e.g., 'SU'). Defaults to `'default_engine'`.

    Returns:
        dict: Contains extracted run results, including statistical data, refined parameters,
        and lattice information.
    """

    statistic_json = os.path.join(xds_dir, "STATISTICS.JSON")
    xds_ascii = os.path.join(xds_dir, "XDS_ASCII.HKL")
    xds_inp = os.path.join(xds_dir, "XDS.INP")
    correct_lp = os.path.join(xds_dir, "CORRECT.LP")
    idxref_lp = os.path.join(xds_dir, "IDXREF.LP")
    if not os.path.isfile(xds_ascii) or not analysis_idxref_lp(idxref_lp):
        return {"mtime": os.path.getmtime(os.path.join(xds_dir, "INIT.LP"))} \
            if os.path.isfile(os.path.join(xds_dir, "INIT.LP")) \
            else {"mtime": os.path.getmtime(correct_lp)}
    if os.path.exists(statistic_json):
        try:
            with open(statistic_json, "r") as json_file:
                statistic_dict = json.load(json_file)
            if statistic_dict["mtime"] == os.path.getmtime(xds_ascii) and "volume" in statistic_dict:
                return statistic_dict
        except Exception as e:
            print(f"Json File {statistic_json} read error as {e}.")

    statistic_dict = analysis_correct_lp(correct_lp)

    if engine == "SU":
        statistic_dict.update(analysis_xds_hkl(xds_ascii, merge=False, MM=is_MM))
    else:
        statistic_dict["mtime"] = os.path.getmtime(xds_ascii)

    with open(xds_inp, errors="replace") as f:
        lines = f.readlines()
        statistic_dict["input"] = extract_keywords(lines)

    img_path = os.path.abspath(os.path.dirname(
        os.path.join(xds_dir, statistic_dict["input"]["NAME_TEMPLATE_OF_DATA_FRAMES"][0].split()[0])))
    img_files = sorted(glob.glob(os.path.join(img_path, '*.img')), key=natural_sort_key)
    img_start = fabio.open(img_files[0])
    img_final = fabio.open(img_files[-1])
    statistic_dict["time"] = float(img_start.header.get("TIME", 0.0))
    if abs(float(img_start.header.get("PHI", 0.0)) - statistic_dict["start_angle"]) < 1:
        if float(img_final.header.get("PHI", 0.0)) != 0.0:
            statistic_dict["end_angle"] = float(img_final.header["PHI"])
        else:
            statistic_dict["end_angle"] = float(
                statistic_dict["start_angle"] + statistic_dict["frames"] * statistic_dict["step"])
    else:
        statistic_dict["start_angle"] = float(img_start.header.get("PHI", 0.0))
        statistic_dict["end_angle"] = float(img_final.header.get("PHI", 0.0))
    statistic_dict["detector"] = img_start.header.get("DETECTOR", "")
    statistic_dict["instrument"] = img_start.header.get("BEAMLINE", "")
    statistic_dict["img_path"] = img_path
    statistic_dict["xds_dir"] = xds_dir
    lattice = test_lattice_symmetry_hkl(xds_dir)
    if lattice is None:
        statistic_dict["lattice_choice"] = []
    else:
        statistic_dict["lattice_choice"] = lattice

    statistic_dict.update(analysis_idxref_lp(idxref_lp))
    with open(statistic_json, "w") as json_file:
        json.dump(statistic_dict, json_file, indent=4)
    return statistic_dict


def extract_cluster_result(
        cluster_dir: str, engine: str = engine_hkl_analysis, merge: bool = True, reso: float = None,
        output: bool = False
) -> dict:
    """Extracts and processes clustering results from the specified directory.

    Args:
        cluster_dir (str): Directory containing clustering results.
        engine (str, optional): Analysis engine to use. Defaults to default_engine.
        merge (bool, optional): Indicates whether to merge results. Defaults to `True`.
        reso (float, optional): Resolution limit for merging. Defaults to `None`.
        output (bool, optional): Controls output behavior. Defaults to `False`.

    Returns:
        dict: Contains clustering results, including statistical data and merged parameters.
    """
    cluster_json = os.path.join(cluster_dir, "CLUSTER.JSON")
    all_hkl = os.path.join(cluster_dir, "all.HKL")

    if os.path.exists(cluster_json):
        try:
            with open(cluster_json, "r") as json_file:
                statistic_dict = json.load(json_file)
            if ("mtime" in statistic_dict and statistic_dict["mtime"] == os.path.getmtime(all_hkl) and
                    "merge_resolution" in statistic_dict and statistic_dict["merge_resolution"] == reso and
                    "unit_cell_esd" in statistic_dict):
                return statistic_dict
            elif ("mtime" in statistic_dict and statistic_dict["mtime"] == os.path.getmtime(all_hkl) and
                  reso is None and "unit_cell_esd" in statistic_dict):
                return statistic_dict
        except Exception as e:
            print(f"Cluster Json File {cluster_json} read error as {e}.")

    statistic_dict = analysis_xscale_lp(os.path.join(cluster_dir, "XSCALE.LP"))
    unit_cell = statistic_dict["unit_cell"]
    if reso is None:
        reso = statistic_dict["merge_resolution"] if "merge_resolution" in statistic_dict else 0.84
    statistic_dict["merge_resolution"] = reso
    if engine == "SU":
        statistic_dict.update(analysis_xds_hkl(all_hkl, merge=merge, reso=reso, output=output, MM=is_MM))
        statistic_dict["unit_cell"] = unit_cell
    else:
        statistic_dict["mtime"] = os.path.getmtime(all_hkl)

    statistic_dict["input_statistics"] = {}
    for path in statistic_dict["input"]:
        statistic_dict["input_statistics"][path] = extract_run_result(os.path.dirname(path))

    print(f"Finish reading clustering information in {cluster_dir}")
    with open(cluster_json, "w") as json_file:
        json.dump(statistic_dict, json_file, indent=4)
    return statistic_dict


if __name__ == "__main__":
    print(extract_cluster_result("/mnt/c/experiment_4_155/SMV"))
