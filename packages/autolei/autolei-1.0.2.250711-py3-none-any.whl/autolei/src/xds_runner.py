"""
XDS Runner Module.

This module provides tools for running XDS in parallel, managing and extracting data from XDS runs,
and refining the results based on specific criteria. It is designed for high-throughput crystallographic
data processing, enabling efficient execution, monitoring, and refinement of XDS processes.

Typical usage example:
    1. Run XDS processes:
        Call `xdsrunner` with the appropriate folder path and list of `XDS.INP` files
        to execute XDS runs in parallel.

    2. Extract results:
        Use `excel_extract` to compile results from XDS output files into an Excel spreadsheet.

    3. Refine runs:
        Apply `refine_run` to improve the quality of XDS results using specific refinement criteria.

    4. Handle failures:
        Use `rerun_failed` to identify and address failed XDS runs, applying suggested refinements
        and re-executing the processes.

Attributes:
    bool_use_short_name (bool): Whether to use short path names for XDS directories.
    engine_hkl_analysis (str): Analysis engine used for HKL analysis.

Dependencies:
    - configparser
    - os
    - sys
    - time
    - warnings
    - subprocess
    - threading
    - pandas

Configuration:
    - Ensure the `setting.ini` file is correctly configured. This file contains settings for path naming
      conventions and analysis engines.

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen and Lei Wang
    - License: BSD 3-clause
"""
import configparser
import os.path
import sys
import time
import warnings

import pandas as pd

from .analysis_hkl import unit_cell_volume
from .util import *
from .xds_analysis import extract_run_result
from .xds_refine import refine_file, refine_failed

warnings.simplefilter(action='ignore', category=FutureWarning)

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, "..", 'setting.ini'))

bool_use_short_name = strtobool(config["XDSRunner"]["use_short_path"])
engine_hkl_analysis = config["XDSRunner"]["engine_hkl_analysis"]


def run_xds_par(xds_dir: str, output_callback: callable) -> int:
    """
    Executes the `xds_par` command in the specified directory and provides real-time output.

    Args:
        xds_dir (str): Directory where the `xds_par` process will be executed.
        output_callback (callable): Callback function to handle real-time output lines.

    Returns:
        int: The return code of the `xds_par` process.
    """

    os.chdir(xds_dir)
    process = subprocess.Popen("xds_par", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open('XDS.LP', 'w') as log_file:
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            if output:
                decoded_output = output.decode().rstrip('\n')
                output_callback(decoded_output)
                log_file.write(decoded_output + '\n')
        rc = process.poll()
    return rc


def xdsrunner(folder_path: str, xds_files: list, use_cell: bool = False,
              update_excel: bool = True, rerun: bool = strtobool(config["XDSRunner"]["rerun_failed"])) -> None:
    """
    Manages and executes XDS processes for a list of input files.

    Args:
        folder_path (str): Directory containing the XDS input files.
        xds_files (list): List of paths to `XDS.INP` files to be processed.
        use_cell (bool, optional): Whether to include cell information in the runs. Defaults to `False`.
        update_excel (bool, optional): Whether to update the results in an Excel file. Defaults to `True`.
        rerun (bool, optional): Whether to rerun failed XDS processes. Defaults to `False`.

    Returns:
        None
    """

    if not xds_files:
        return
    print("********************************************")
    print("*                XDS Runner                *")
    print("********************************************\n")

    def print_output(output):
        # Clear the progress message before printing xds_par output
        sys.stdout.write('\r' + ' ' * (len(progress_message) + 10) + '\r')
        sys.stdout.flush()
        print(output)
        # Restore the progress message
        sys.stdout.write('\r' + progress_message)
        sys.stdout.flush()

    xds_files = sorted(xds_files, key=natural_sort_key)
    total_files = len(xds_files)

    for index, xds_file in enumerate(xds_files):
        xds_dir = os.path.dirname(xds_file)

        files_to_delete = ["xds_ascii.hkl", "integrate.hkl", "correct.lp", "idxref.lp", "statistics.json", "spot.xds",
                           "integrate.lp", "colspot.lp"]

        for file in os.listdir(xds_dir):
            if file.lower() in files_to_delete:
                file_path = os.path.join(xds_dir, file)
                os.remove(file_path)
        print(f"Deleting file in {xds_dir}.")

        rel_path = os.path.relpath(xds_dir, folder_path)
        progress_message = f" XDS is Running in {rel_path}: Progress {index + 1}/{total_files} "
        if len(progress_message) > 98:
            pass
        elif len(progress_message) % 2 == 0:
            progress_message = ("*" + "-" * ((96 - len(progress_message)) // 2) + progress_message +
                                "-" * ((96 - len(progress_message)) // 2) + "*")
        else:
            progress_message = ("*-" + "-" * ((97 - len(progress_message)) // 2) + progress_message +
                                "-" * ((97 - len(progress_message)) // 2) + "*")

        xds_thread = threading.Thread(target=run_xds_par, args=(xds_dir, print_output))
        xds_thread.start()

        while xds_thread.is_alive():
            sys.stdout.write('\r' + progress_message)
            sys.stdout.flush()
            time.sleep(1)  # Update interval

        sys.stdout.write('\r' + ' ' * len(progress_message) + '\r')  # Clear the progress message
        sys.stdout.flush()
        print(progress_message)  # Print the final progress message for this file

        xds_thread.join()
        extract_run_result_thread = threading.Thread(target=extract_run_result, args=(xds_dir, engine_hkl_analysis))
        extract_run_result_thread.start()
        extract_run_result_thread.join()

    sys.stdout.write('\n')
    os.chdir(folder_path)

    if rerun:
        rerun_failed(folder_path, xds_files)

    if update_excel:
        try:
            excel_extract(folder_path, use_cell=use_cell)
        except PermissionError as e:
            print(e)


def format_value_with_esd(value: float, esd: float) -> str:
    """
    Formats a numerical value with its estimated standard deviation (ESD).

    Args:
        value (float): The value to format.
        esd (float): The estimated standard deviation of the value.

    Returns:
        str: A formatted string in the format "value(esd)", rounded appropriately.
    """
    # If the esd is less than 1, retain decimal places for the esd and value
    if esd < 1:
        decimal_places = -int(np.floor(np.log10(esd)))
        esd_rounded = round(esd, decimal_places)
        value_rounded = round(value, decimal_places)
        esd_str = str(int(esd_rounded * 10 ** decimal_places))  # esd shown as integer
        return f"{value_rounded}({esd_str})"
    else:
        # Round the value and esd based on esd magnitude
        esd_rounded = round(esd, -len(str(int(esd))) + 1)  # round esd to appropriate sigfig
        value_rounded = round(value)
        return f"{value_rounded}({int(esd_rounded)})"


def calculate_vol(unit_cell: list, unit_cell_esds: list or None) -> str:
    """
    Calculates the volume of a unit cell along with its uncertainty.

    Args:
        unit_cell (list): List of unit cell parameters [a, b, c, alpha, beta, gamma].
        unit_cell_esds (list): List of uncertainties for the unit cell parameters.

    Returns:
        str: Formatted string of the calculated volume and its uncertainty (e.g., "1234.567(89)").
    """
    if unit_cell_esds:
        a, b, c, alpha, beta, gamma = unit_cell
        delta_a, delta_b, delta_c, delta_alpha, delta_beta, delta_gamma = unit_cell_esds

        # Convert angles to radians
        alpha_rad, beta_rad, gamma_rad = np.deg2rad([alpha, beta, gamma])
        delta_alpha_rad, delta_beta_rad, delta_gamma_rad = np.deg2rad([delta_alpha, delta_beta, delta_gamma])

        # Compute cos and sin of angles
        cos_alpha = np.cos(alpha_rad)
        cos_beta = np.cos(beta_rad)
        cos_gamma = np.cos(gamma_rad)
        sin_alpha = np.sin(alpha_rad)
        sin_beta = np.sin(beta_rad)
        sin_gamma = np.sin(gamma_rad)

        # Compute Q and sqrt(Q)
        Q = 1 - cos_alpha ** 2 - cos_beta ** 2 - cos_gamma ** 2 + 2 * cos_alpha * cos_beta * cos_gamma
        sqrt_Q = np.sqrt(Q)

        # Compute volume
        V = a * b * c * sqrt_Q

        # Compute partial derivatives
        dV_da = b * c * sqrt_Q
        dV_db = a * c * sqrt_Q
        dV_dc = a * b * sqrt_Q

        dQ_dalpha = 2 * sin_alpha * (cos_alpha - cos_beta * cos_gamma)
        dQ_dbeta = 2 * sin_beta * (cos_beta - cos_alpha * cos_gamma)
        dQ_dgamma = 2 * sin_gamma * (cos_gamma - cos_alpha * cos_beta)

        dV_dalpha = a * b * c * dQ_dalpha / (2 * sqrt_Q)
        dV_dbeta = a * b * c * dQ_dbeta / (2 * sqrt_Q)
        dV_dgamma = a * b * c * dQ_dgamma / (2 * sqrt_Q)

        # Compute delta_V
        delta_V = np.sqrt(
            (dV_da * delta_a) ** 2 +
            (dV_db * delta_b) ** 2 +
            (dV_dc * delta_c) ** 2 +
            (dV_dalpha * delta_alpha_rad) ** 2 +
            (dV_dbeta * delta_beta_rad) ** 2 +
            (dV_dgamma * delta_gamma_rad) ** 2
        )

        # Return formatted result
        return format_value_with_esd(V, delta_V)

    else:
        return str(int(unit_cell_volume(*unit_cell)))


def excel_extract(folder_path: str, use_cell: bool = False, engine: str = engine_hkl_analysis) -> None:
    """
    Extracts results from XDS output files and saves them to an Excel file.

    Args:
        folder_path (str): Path to the folder containing XDS output files.
        use_cell (bool, optional): Whether to include unit cell information in the extraction. Defaults to `False`.
        engine (str, optional): The analysis engine used for HKL data processing. Defaults to "default_engine".

    Returns:
        None
    """
    print("Excel extraction is ongoing ... ", end="", flush=True)
    xds_files = []
    for root, dirs, files in os.walk(folder_path):
        if "xds.inp" in [file.lower() for file in files]:
            xds_files.append(os.path.join(root, "xds.inp"))
    xds_files = sorted(xds_files, key=natural_sort_key)
    columns = ["No.", "Path", "Integration Cell", "SG", "Unit cell", "Vol.", "Index%", "ISa", "Rmeas", "CC1/2",
               "Completeness", "Reso."]
    dtypes = {
        'No.': int,
        'Path': str,
        'Integration Cell': str,
        'SG': str,
        'Unit cell': str,
        'Vol.': str,
        "Index%": float,
        'ISa': float,
        'Rmeas': float,
        'CC1/2': float,
        'Completeness': float,
        'Reso.': float
    }
    results_df = pd.DataFrame(columns=columns)
    result_num = 0
    for i, xds_file in enumerate(xds_files):
        print(f"\rExcel extraction is ongoing ... {i + 1}/{len(xds_files)}", end="", flush=True)
        try:
            xds_dir = os.path.dirname(xds_file)
            xds_ascii = os.path.join(xds_dir, "XDS_ASCII.HKL")
            if not os.path.exists(xds_ascii):
                continue
            run_result_dict = extract_run_result(xds_dir, engine)

            relative_path = os.path.join("...", os.path.relpath(xds_dir, folder_path))
            if bool_use_short_name:
                result = [i + 1, relative_path] + [None] * 10
            else:
                result = [i + 1, xds_dir] + [None] * 10

            result[2] = "  ".join([str(item) if item != 90.0 else "90" for item in run_result_dict["unit_cell_index"]])
            result[3] = run_result_dict["space_group_number"] if "space_group_number" in run_result_dict else "1"
            try:
                result[4] = '  '.join(unit_cell_with_esd(run_result_dict["unit_cell"],
                                                         run_result_dict["unit_cell_esd"]))
                result[5] = calculate_vol(run_result_dict["unit_cell"], run_result_dict["unit_cell_esd"])
            except KeyError:
                result[4] = '  '.join([f"{a}" for a in run_result_dict["unit_cell"]])
                result[5] = calculate_vol(run_result_dict["unit_cell"], None)
            result[6] = round(run_result_dict.get("index_number", 0) / run_result_dict.get("spot_number", 1) * 100, 1)
            result[7] = run_result_dict["ISa_model"] if "ISa_model" in run_result_dict else run_result_dict["Isa_model"]
            result[8] = run_result_dict["rmeas"] if "rmeas" in run_result_dict else run_result_dict["R_meas"]
            result[9] = run_result_dict["cc12_reso"] if "cc12_reso" in run_result_dict else run_result_dict["CC1/2"]
            result[10] = run_result_dict["completeness"]
            result[11] = run_result_dict["resolution"]

            result_num += 1
            new_row = pd.DataFrame([result], columns=columns).astype(dtypes)
            results_df = pd.concat([results_df, new_row], ignore_index=True)
        except Exception as e:
            print(f"The result extraction on {os.path.dirname(xds_file)} is fail due to {e}")

    excel_filename = os.path.join(folder_path, f"xdsrunner{'2' if use_cell else ''}.xlsx")
    try:
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            results_df.to_excel(writer, index=False)
    except PermissionError:
        raise PermissionError(
            "Permission Error",
            f"Cannot write to the file '{excel_filename}'.\n"
            "It may be open in another application (e.g., Excel).\n"
            "Please close the Excel file and try again.")
    print(
        f"\n{result_num} of {len(xds_files)} runs has result files.")
    print(
        f"All information extracted{' after adding cell information' if use_cell else ''}."
        f" Note that resolution is ideal.\n")
    return


def refine_run(folder_path: str, xds_files: list, refine_dict: dict) -> None:
    """
    Applies refinement criteria to XDS runs and re-executes them.

    Args:
        folder_path (str): Directory containing XDS input files.
        xds_files (list): List of paths to `XDS.INP` files to refine.
        refine_dict (dict): Dictionary containing refinement criteria to apply.

    Returns:
        None
    """
    print("********************************************")
    print("*                XDS Refine                *")
    print("********************************************\n")

    run_list = []
    if not xds_files:
        print("No input list for XDS refinement.")
        return
    for xds_path in xds_files:
        if refine_file(xds_path, refine_dict):
            run_list.append(xds_path)
    xdsrunner(folder_path, run_list, True)


def rerun_failed(folder_path: str, xds_files: list) -> None:
    """
    Identifies failed XDS runs, applies suggested refinements, and reruns them.

    Args:
        folder_path (str): Base directory containing XDS input files.
        xds_files (list): List of paths to `XDS.INP` files.

    Returns:
        None
    """
    run_list = []
    if not xds_files:
        print("No input list for XDS refinement.")
        return
    suggest_dict = refine_failed(folder_path, xds_list=xds_files)
    for xds_path, strategy in suggest_dict.items():
        parameter_dict = {"axis": False, "divergence": False, "scale": False, "index": False,
                          "resolution": False, "beam_centre": False}
        if strategy and strategy in parameter_dict:
            parameter_dict[strategy] = True
            if refine_file(xds_path, parameter_dict):
                run_list.append(xds_path)
    if run_list:
        xdsrunner(folder_path, run_list, True, rerun=False)


if __name__ == "__main__":
    pass
