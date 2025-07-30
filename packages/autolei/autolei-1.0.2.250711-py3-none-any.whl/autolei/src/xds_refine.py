"""
XDS Refinement Module
=====================

This module provides a comprehensive suite of functions to refine XDS processing parameters and improve the quality
and accuracy of crystallographic data. The refinements include optimization of indexing parameters, scaling,
beam divergence, rotation axis, resolution range, and beam center coordinates.

Modules
-------
- Index Refinement
- Scale Refinement
- Beam Divergence and Mosaicity Correction
- Rotation Axis Adjustment
- Resolution Range Modification
- Beam Center Optimization

Classes:
    None

Functions:
    index_refine(xds_dir: str, threshold: float = 80) -> None
        Refines indexing parameters based on the specified threshold.

    scale_refine(xds_dir: str, outlier_scale_ratio: float = 2) -> None
        Removes scaling outliers based on the specified scale ratio.

    dev_moscaicity_refine(xds_dir: str) -> None
        Adds divergence and mosaicity corrections.

    change_resolution_range(xds_dir: str, resolution: str) -> None
        Modifies the resolution range in the XDS.INP file.

    change_axis(xds_dir: str, axis_angle: float) -> None
        Updates the rotation axis in the XDS.INP file.

    refine_axis(xds_dir: str) -> bool
        Refines the rotation axis by optimizing the omega angle.

    optimise_beam_centre(fp: str, ...) -> tuple
        Optimizes beam center coordinates using an intensity penalty approach.

    refine_beam_centre(path: str) -> None
        Refines beam center parameters and updates the XDS.INP file.

    refine_file(xds_path: str, parameter_dict: dict) -> bool
        Executes multiple refinement steps based on provided parameters.

    check_xds_progress(directory: str) -> str or None
        Checks the progress of XDS processing.

    read_error_message(lp_file: str) -> list
        Extracts error messages from an XDS log file.

    check_status(xds_list: list) -> dict
        Analyzes the status of XDS processing for multiple runs.

    refine_failed(base_directory: str, ...) -> dict
        Provides refinement strategies for failed XDS runs.

Dependencies:
    - configparser
    - os
    - shutil
    - subprocess
    - concurrent.futures
    - functools
    - numpy
    - scipy
    - numba

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen
    - License: BSD 3-clause
"""

import configparser
import os
import shutil
import subprocess

import numpy as np

from .util import outliers_iqr_dict, strtobool
from .xds_analysis import load_scale_list, analysis_idxref_lp, load_mosaicity_list, load_divergence_list, find_xds_files
from .xds_input import generate_exclude_data_ranges, load_XDS_excluded_range, replace_value
from .xds_refiner.rotation_axis import refine_axis
from .xds_refiner.beam_centre import refine_beam_centre

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])

if not strtobool(config["General"]["multi-process"]):
    set_max_worker = 1


def index_refine(xds_dir: str, threshold: float = 80) -> None:
    """
    Refines the indexing parameters based on the specified threshold.

    Args:
        xds_dir (str): Directory containing the XDS files.
        threshold (float, optional): Threshold for the index ratio to trigger refinement. Defaults to 80.

    Returns:
        None
    """
    os.chdir(xds_dir)
    idxref_lp = os.path.join(xds_dir, "IDXREF.LP")
    xds_inp = os.path.join(xds_dir, "XDS.INP")
    if not os.path.isfile(idxref_lp):
        subprocess.call("xds_par")
    index_result = analysis_idxref_lp(idxref_lp)
    if index_result:
        index_number = index_result.get("index_number")
        if index_number is None:
            index_number = 0  # Default to 0 if None

        spot_number = index_result.get("spot_number")
        if spot_number is None:
            spot_number = 1  # Default to 1 if None
        initial_index_ratio = round(index_number / spot_number * 100, 1)
    else:
        initial_index_ratio = 0.0
    if initial_index_ratio > threshold:
        return

    index_dict = {}
    error_value = [0.05, 0.08, 0.10, 0.12, 0.14, 0.16]
    print("Testing suitable index error ...", end="", flush=True)
    for i, value in enumerate(error_value):
        progress_status = f"({i + 1}/{len(error_value)})"
        with open(xds_inp, "r+", errors="replace") as f:
            lines = f.readlines()
            lines = replace_value(lines, "JOB", ["IDXREF"], comment=False)
            lines = replace_value(lines, "INDEX_ERROR", [f"{value}"], comment=False)
            f.seek(0)
            f.writelines(lines)
            f.truncate()
        print(f"\rTesting suitable index error ... {progress_status}")
        subprocess.call("xds_par", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        index_result = analysis_idxref_lp(idxref_lp)
        if index_result:
            index_number = index_result.get("index_number")
            if index_number is None:
                index_number = 0  # Default to 0 if None
            spot_number = index_result.get("spot_number")
            if spot_number is None:
                spot_number = 1  # Default to 1 if None
            index_ratio = round(index_number / spot_number * 100, 1)
        else:
            index_ratio = 0.0
        index_dict[value] = index_ratio
    print("\rTesting best index error ... OK")
    with open(xds_inp, "r+") as f:
        lines = f.readlines()
        lines = replace_value(lines, "JOB", ["XYCORR INIT COLSPOT IDXREF",
                                             "DEFPIX INTEGRATE CORRECT", "CORRECT"], comment=True)
        lines = replace_value(lines, "INDEX_ERROR",
                              [f"{max(index_dict, key=index_dict.get)}"], comment=False)
        f.seek(0)
        f.writelines(lines)
        f.truncate()
        print(f"Correct index error ... {max(index_dict, key=index_dict.get)}/OK")


def scale_refine(xds_dir: str, outlier_scale_ratio: float = 2) -> None:
    """
    Refines scaling parameters by identifying and excluding outliers.

    Args:
        xds_dir (str): Directory containing the XDS files.
        outlier_scale_ratio (float, optional): Ratio used to identify scaling outliers. Defaults to 2.

    Returns:
        None
    """
    xds_path = os.path.join(xds_dir, "XDS.INP")
    integrate_path = os.path.join(xds_dir, "INTEGRATE.LP")
    correct_path = os.path.join(xds_dir, "CORRECT.LP")
    if not os.path.isfile(integrate_path) or not os.path.isfile(correct_path):
        return
    with open(integrate_path, "r") as f:
        lines = f.readlines()
        init_scales = load_scale_list(lines)
    with open(xds_path, "r") as f:
        first_occurrence = None
        xds_lines = f.readlines()
        output_lines = []
        for j, line in enumerate(xds_lines):
            if "EXCLUDE_DATA_RANGE=" in line:
                if first_occurrence is None:
                    first_occurrence = j
            else:
                output_lines.append(line)
    filter_list = outliers_iqr_dict(init_scales, outlier_scale_ratio)
    exclude_list = load_XDS_excluded_range(xds_lines)
    exclude_list = sorted(list(set(exclude_list + filter_list)))
    add_lines = generate_exclude_data_ranges(exclude_list)
    if first_occurrence is not None:
        for new_line in reversed(add_lines):  # Reverse to maintain order after insert
            output_lines.insert(first_occurrence, new_line)
    else:
        output_lines += add_lines
    with open(xds_path, 'w') as file:
        file.writelines(output_lines)


def dev_moscaicity_refine(xds_dir: str) -> None:
    """
    Refines divergence and mosaicity parameters based on previous runs.

    Args:
        xds_dir (str): Directory containing the XDS files.

    Returns:
        None
    """
    xds_path = os.path.join(xds_dir, "XDS.INP")
    integrate_path = os.path.join(xds_dir, "INTEGRATE.LP")
    with open(integrate_path, "r") as f:
        lines = f.readlines()
        mosaicity_list = list(load_mosaicity_list(lines).values())
        divergence_list = list(load_divergence_list(lines).values())
    divergence = np.average([item for item in divergence_list if item])
    mosaicity = np.average([item for item in mosaicity_list if item])
    with open(xds_path, 'r+') as file:
        lines = file.readlines()
        lines = replace_value(lines, "BEAM_DIVERGENCE_E.S.D.", [f"{divergence:.3f}"], comment=False)
        lines = replace_value(lines, "REFLECTING_RANGE_E.S.D.", [f"{mosaicity:.3f}"], comment=False)
        file.seek(0)
        file.writelines(lines)
        file.truncate()


def change_resolution_range(xds_dir: str, resolution: str) -> None:
    """
    Changes the resolution range in the XDS.INP file.

    Args:
        xds_dir (str): Directory containing the XDS files.
        resolution (str): New resolution range to set, e.g., "30 1.5".

    Returns:
        None
    """
    xds_path = os.path.join(xds_dir, "XDS.INP")
    with open(xds_path, "r+") as f:
        lines = f.readlines()
        lines = replace_value(lines, "INCLUDE_RESOLUTION_RANGE", [resolution], comment=False)
        f.seek(0)
        f.writelines(lines)
        f.truncate()


def refine_file(xds_path: str, parameter_dict: dict) -> bool:
    """
    Executes the refinement process based on specified parameters.

    Args:
        xds_path (str): Path to the XDS.INP file.
        parameter_dict (dict): Parameters for refinement steps. Includes:
            - "divergence" (bool): Refine divergence.
            - "scale" (float): Scale outlier ratio.
            - "axis" (bool): Refine rotation axis.
            - "index" (float): Index refinement threshold.
            - "beam_centre" (bool): Refine beam center.
            - "resolution" (str): Resolution range.

    Returns:
        bool: True if refinement was successful, False otherwise.
    """
    print(f"\nEntering XDS path {xds_path}")
    xds_dir = os.path.dirname(xds_path)

    if not os.path.exists(os.path.join(xds_dir, "BACKUP-CELL")):
        shutil.copy(os.path.join(xds_dir, "XDS.INP"), os.path.join(xds_dir, "BACKUP-CELL"))
    else:
        shutil.copy(os.path.join(xds_dir, "XDS.INP"), os.path.join(xds_dir, "BACKUP-REFINE"))

    if ((parameter_dict["divergence"]) and
            (not os.path.exists(os.path.join(xds_dir, "INTEGRATE.LP")) or not os.path.exists(
                os.path.join(xds_dir, "IDXREF.LP")))):
        print(f"{xds_dir} need to be run at first.")
        return False

    if ((parameter_dict["scale"]) and
            (not os.path.exists(os.path.join(xds_dir, "CORRECT.LP")) or not os.path.exists(
                os.path.join(xds_dir, "IDXREF.LP")))):
        print(f"{xds_dir} need to be run at first.")
        return False

    try:
        if parameter_dict["axis"]:
            print("Correct Rotation Axis with refined result ...")
            result = refine_axis(xds_dir)
            if result:
                print("\rCorrect Rotation Axis with refined result ... OK")
            else:
                print("\rCorrect Rotation Axis with refined result ... Failed")

        if parameter_dict["divergence"]:
            print("Add Divergence from Previous Run ... ... ", end="", flush=True)
            dev_moscaicity_refine(xds_dir)
            print("\rAdd Divergence from Previous Run ... ... OK")

        if parameter_dict["scale"]:
            print("Remove Scale Outliers from Previous Run ...", end="", flush=True)
            scale_refine(xds_dir, parameter_dict["scale"])
            print("\rRemove Scale Outliers from Previous Run ... OK")

        if parameter_dict["index"]:
            index_refine(xds_dir, parameter_dict["index"])

        if parameter_dict["beam_centre"]:
            refine_beam_centre(xds_dir)
            print("Finding Beam Centre ... ... ... OK")

        if parameter_dict["resolution"]:
            print("Change resolution to {} ... ... ... ".format(parameter_dict["resolution"]), end="", flush=True)
            change_resolution_range(xds_dir, parameter_dict["resolution"])
            print("\rChange resolution to {} ... ... ... OK".format(parameter_dict["resolution"]))

    except Exception as e:
        print(f"Refine error because of {e}")
        return False

    return True


def check_xds_progress(directory: str) -> str or None:
    """
    Checks the progress of XDS processing by identifying the most recent log file.

    Args:
        directory (str): Directory containing the XDS files.

    Returns:
        str or None: Path of the last generated LP file, or None if processing is complete.
    """

    # Define the sequence of LP files and the final output file
    lp_files = [
        "INIT.LP", "COLSPOT.LP", "IDXREF.LP",
        "DEXREF.LP", "INTEGRATE.LP", "CORRECT.LP"
    ]
    final_file = "XDS_ASCII.HKL"

    # Check if the final output file exists
    final_path = os.path.join(directory, final_file)
    if os.path.exists(final_path):
        return None

    # Track the most recent LP file in the sequence
    last_lp_file = None
    latest_time = None

    # Iterate over the LP files to find the most recent one
    for lp_file in lp_files:
        lp_path = os.path.join(directory, lp_file)
        if os.path.exists(lp_path):
            lp_time = os.path.getmtime(lp_path)
            if last_lp_file is None or lp_time > latest_time:
                last_lp_file = lp_path
                latest_time = lp_time

    # Return the path of the last generated LP file if XDS_ASCII.HKL is not present
    return last_lp_file


def read_error_message(lp_file: str) -> list:
    """
    Extracts error messages from a given LP file.

    Args:
        lp_file (str): Path to the LP file.

    Returns:
        list: List of error messages found in the LP file.
    """
    error_messages = []
    if lp_file and os.path.exists(lp_file):
        with open(lp_file, 'r') as file:
            for line in file:
                if "!!! ERROR" in line and "CANNOT READ IMAGE" not in line:
                    error_messages.append(line.strip())
    return error_messages


def check_status(xds_list: list) -> dict:
    """
    Checks the status of multiple XDS runs and collects error messages.

    Args:
        xds_list (list): List of paths to XDS.INP files.

    Returns:
        dict: A dictionary mapping file paths to their error messages and stop files.
    """
    error_dict = {}
    for xds_file in xds_list:
        root = os.path.dirname(xds_file)
        last_lp_file = check_xds_progress(root)
        if last_lp_file is None:
            pass
        else:
            error_messages = read_error_message(last_lp_file)
            if error_messages:
                error_dict[xds_file] = {
                    "stop_file": os.path.basename(last_lp_file),
                    "error_messages": error_messages
                }
    return error_dict


def failed_refine_strategy_basic(xds_file: str, error_message: dict) -> str or None:
    """
    Suggests basic refinement strategies based on error messages.

    Args:
        xds_file (str): Path to the XDS file.
        error_message (dict): Dictionary containing error messages.

    Returns:
        str or None: Suggested refinement step, or None if no strategy is applicable.
    """
    if error_message["stop_file"] == "INTEGRATE.LP":
        if ("!!! ERROR !!! AUTOMATIC DETERMINATION OF SPOT SIZE PARAMETERS HAS FAILED."
                in error_message["error_messages"]):
            return "divergence"
    return None


def failed_refine_strategy_advanced(xds_file: str, error_message: dict) -> str or None:
    """
    Provides advanced strategies for handling failed refinements.

    Args:
        xds_file (str): Path to the XDS file.
        error_message (dict): Dictionary containing error messages.

    Returns:
        None
    """
    if error_message["stop_file"] == "INTEGRATE.LP":
        if ("!!! ERROR !!! AUTOMATIC DETERMINATION OF SPOT SIZE PARAMETERS HAS FAILED."
                in error_message["error_messages"]):
            return "divergence"
    return None


def refine_failed(base_directory: str, xds_list: list = None, mode: str = "basic") -> dict:
    """
    Provides refinement strategies for failed XDS runs.

    Args:
        base_directory (str): Base directory containing XDS files.
        xds_list (list, optional): List of paths to XDS.INP files. Defaults to None.
        mode (str, optional): Refinement mode, either "basic" or "advanced". Defaults to "basic".

    Returns:
        dict: A dictionary mapping failed XDS files to suggested refinement strategies.
    """
    suggestion_dict = {}
    if xds_list is None:
        xds_list = find_xds_files(base_directory)
    error_dict = check_status(xds_list)
    for xds_file, error_message in error_dict.items():
        if mode == "basic":
            suggestion_dict[xds_file] = failed_refine_strategy_basic(xds_file, error_message)
        elif mode == "advanced":
            suggestion_dict[xds_file] = failed_refine_strategy_advanced(xds_file, error_message)
    return suggestion_dict


if __name__ == "__main__":
    import cProfile

    cProfile.run(
        "refine_axis(\"/mnt/d/ED/Work/MFM300/Al_5/xds\")",
        sort="tottime")
