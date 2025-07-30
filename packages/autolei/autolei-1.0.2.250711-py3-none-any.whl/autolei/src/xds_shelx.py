"""
XDS to SHELX Conversion Module
==============================

This module provides utilities for converting crystallographic data from XDS format to SHELX format.
It facilitates the generation of necessary input files, executes the conversion process, and updates
related `.ins` and `.pcf` files with accurate metadata.

Overview:
    The XDS to SHELX Conversion Module automates the preparation of conversion inputs, handles the
    execution of `xdsconv`, and ensures metadata consistency in SHELX-related files. The module
    supports batch conversion of datasets and is suitable for large-scale crystallographic projects.

Features:
    - Converts `XDS_ASCII.HKL` files to SHELX-compatible `.HKL` files.
    - Prepares and generates `.P4P` files with unit cell and experimental details.
    - Updates `.ins` and `.pcf` files with metadata such as wavelength, temperature, and unit cell parameters.
    - Handles single and multi-dataset workflows seamlessly.

Dependencies:
    - Standard Libraries:
        - `json`, `math`, `warnings`, `os`, `subprocess`
    - Third-Party Libraries:
        - `pandas` (for data handling)
    - Custom Modules:
        - `.cif_io`: Utilities for handling CIF files.
        - `.util`: Helper functions for file and path operations.
        - `.xds_analysis`: Analysis utilities for XDS output files.

Usage:
    This module is designed to integrate into larger crystallographic workflows or operate as a standalone
    utility for converting datasets.

    Example:
        ```python
        from xds_to_shelx import convert_to_shelx, write_xconv, output_content_P4P

        # Convert XDS datasets to SHELX format
        convert_to_shelx("path/to/xds/directory", xconv_folder="merged_results")

        # Prepare XDSCONV.INP for conversion
        write_xconv("path/to/input", ["path/to/XDS_ASCII.HKL"])

        # Generate .P4P file with unit cell and experimental details
        output_content_P4P("path/to/directory", file_name="example.P4P", multi=False)
        ```

Notes:
    - Ensure `xdsconv` is installed and accessible in the system's PATH.
    - The input directory should contain valid `XDS_ASCII.HKL` files for conversion.
    - Handle exceptions for missing or incomplete metadata during batch processing.

Authors:
    Yinlin Chen and Lei Wang

License:
    BSD 3-Clause
"""

import json
import math
import warnings
from math import asin

import pandas as pd

from .cif_io import load_cif, print_pcf
from .util import *
from .xds_analysis import analysis_correct_lp, analysis_xscale_lp, get_avg_esd_cell, \
    extract_run_result, extract_cluster_result

warnings.simplefilter(action='ignore', category=FutureWarning)


def convert_to_shelx(input_path: str, xconv_folder: str = "merge") -> None:
    """Convert XDS HKL to SHELX format.

    Arguments:
        input_path (str): The path to the directory containing the XDS_ASCII.HKL files for
                          conversion.
        xconv_folder (str): The folder to store the merged output files if multiple HKL files
                            are found. Defaults to "merge".

    Returns:
        None
    """
    if not input_path:
        print("No input path provided.")
        return
    hkl_list = find_files(input_path, "XDS_ASCII.HKL")
    if not hkl_list:
        raise FileNotFoundError("No HKL files found.")
    if len(hkl_list) == 1:
        xprep_dir = write_xconv(input_path, hkl_list, "xds")
        write_cif_od_single(input_path)
    else:
        xprep_dir = write_xconv(input_path, [], xconv_folder)
    subprocess.run(["xdsconv"], cwd=xprep_dir)

    print(f"XDS.HKL has been converted under {xprep_dir}.\n")


def write_xconv(input_path: str, result_list: list, relative_path: str = "merge") -> str:
    """Create the XDSCONV.INP file and prepare data for SHELX conversion.

    Arguments:
        input_path (str): Path to the directory containing XDS datasets.
        result_list (list): List of paths to XDS ASCII files.
        relative_path (str): Folder name for storing conversion results. Defaults to "merge".

    Returns:
        str: Path to the directory where conversion inputs are prepared.
    """
    multi = True
    if result_list:
        multi = False
        hkl_path = result_list[0]
        xprep_dir = os.path.dirname(hkl_path)
    else:
        xprep_dir = os.path.join(input_path, relative_path)
        if not os.path.exists(xprep_dir):
            print(f"xprep directory does not exist at {xprep_dir}\n")
            return ""

        # Search for the all.hkl file in the xprep directory, ignoring case sensitivity
        for file in os.listdir(xprep_dir):
            if file.lower() == "all.hkl":
                hkl_path = os.path.join(xprep_dir, file)
                break
        else:
            print("all.hkl file not found in the xprep directory.\n")
            return ""

    # Read the all.hkl file and search for the unit cell constants
    if multi:
        output_content_P4P(os.path.dirname(hkl_path), file_name="1.P4P")
    else:
        output_content_P4P(os.path.dirname(hkl_path), file_name="1.P4P", multi=False)

    # Create XDSCONV.INP file with specified content
    xdsconv_inp_content = ["OUTPUT_FILE= 1.HKL SHELX",
                           f"INPUT_FILE= {hkl_path}     !format is XDS_ASCII by default",
                           "FRIEDEL'S_LAW= TRUE",
                           "!MERGE= FALSE"]
    with open(os.path.join(os.path.dirname(hkl_path), "XDSCONV.INP"), 'w') as inp_file:
        inp_file.write("\n".join(xdsconv_inp_content))
    return xprep_dir


def output_content_P4P(file_folder: str, file_name: str = "1.P4P", multi: bool = True) -> None:
    """Generate a `.P4P` file with unit cell parameters and experimental details.

    Arguments:
        file_folder (str): Path to the directory containing XDS datasets.
        file_name (str): Name of the `.P4P` file. Defaults to "1.P4P".
        multi (bool): Indicates if multiple datasets are included. Defaults to True.

    Returns:
        None
    """
    if multi:
        try:
            avg_cell, esd_cell, wavelength = get_avg_esd_cell(file_folder, multi=multi, mode="folder")
        except UnboundLocalError:
            info_dict = extract_cluster_result(os.path.join(file_folder))
            avg_cell, esd_cell, wavelength = (info_dict["unit_cell"], info_dict["unit_cell_esd"],
                                              list(info_dict["input_statistics"].values())[0]["wavelength"])
    else:
        info_dict = analysis_correct_lp(os.path.join(file_folder, "CORRECT.LP"))
        avg_cell, esd_cell, wavelength = info_dict["unit_cell"], info_dict["unit_cell_esd"], info_dict["wavelength"]
    line_append = [f"TITLE  AutoLEI P4P export at {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}\n",
                   f"CHEM \n",
                   "CELL  {:.4f}  {:.4f}  {:.4f}  {:.4f}  {:.4f}  {:.4f}\n".format(*avg_cell),
                   "CELLSD  {:.4f}  {:.4f}  {:.4f}  {:.4f}  {:.4f}  {:.4f}\n".format(*esd_cell),
                   "MORPH  nano-crystal\n"]
    p4p_path = os.path.join(file_folder, file_name)
    with open(p4p_path, "w") as f:
        f.writelines(line_append)


def update_after_prep(input_path: str, ins_path: str, pcf_path: str, info_dict: dict) -> None:
    """Update `.ins` and `.pcf` files after SHELX preparation.

    Arguments:
        input_path (str): Path to the directory containing metadata.
        ins_path (str): Path to the `.ins` file.
        pcf_path (str): Path to the `.pcf` file.
        info_dict (dict): Dictionary containing additional information.

    Returns:
        None
    """
    info_dict.update(analysis_xscale_lp(os.path.join(os.path.dirname(ins_path), "XSCALE.LP")))
    wavelength = update_pcf_file(input_path, pcf_path, info_dict)
    if info_dict.get("short_name", "1"):
        if " " in info_dict.get("short_name", "1"):
            short_name = info_dict.get("short_name", "1").split()[0]
        else:
            short_name = info_dict.get("short_name", "1")
    else:
        short_name = "1"
    update_ins(ins_path, wavelength=wavelength, name=short_name, temperature=info_dict.get("temperature", "298"))


def write_cif_od_single(input_path: str) -> float:
    """Generate a CIF_OD file with unit cell and experimental details.

    Arguments:
        input_path (str): Path to the input directory containing metadata.

    Returns:
        float: Wavelength used in the experiment.
    """
    short_name = "1"
    pcf_dict = {}
    pcf_path = os.path.join(input_path, "1.cif_od")
    scan_list = [extract_run_result(input_path)]
    columns = ["#", "Type", "Start", "End", "Step", "t~exp~", "#Frames", "CL", "Reso.", "ISa", "CC1/2"]
    results_df = pd.DataFrame(columns=columns)
    cell_num = 0
    for i, item in enumerate(scan_list):
        cell_num += item["cell_rfl_num"]
        wavelength = item["wavelength"]
        max_res = item.get("max_res", 20)
        min_res = item.get("min_res", 0.8)
        pixel = item["pixel_size"]
        result = [i + 1, "/a", item["start_angle"], item["end_angle"], item["step"], item["time"], item["frames"],
                  item["camera_length"], item.get("resolution", "N/A"),
                  item["ISa_meas"], item["cc12_reso"] if "cc12_reso" in item else item["CC1/2"]]
        new_row = pd.DataFrame([result], columns=columns)
        results_df = pd.concat([results_df, new_row], ignore_index=True)
    headers = columns
    col_widths = [2, 4, 8, 8, 6, 9, 7, 8, 5, 5, 5]
    # Formatting the header
    header_str = "  ".join(f"{header:<{width}}" for header, width in zip(headers, col_widths))
    # Formatting the rows
    row_strs = []
    for index, row in results_df.iterrows():
        row_strs.append("  ".join(f"{str(val):<{width}}" for val, width in zip(row, col_widths)))
    # Combining everything into a formatted table
    table = f" {header_str}\n{'-' * (len(header_str) + 2)}\n " + "\n ".join(row_strs)
    # Adding the title
    title = "List of Samples for Merging (Abbr. = Camera Length, Resolution):\n"
    pcf_dict["cell_measurement_reflns_used"] = cell_num
    pcf_dict["cell_measurement_theta_min"] = "{:.4f}".format(57.2958 * asin(wavelength / (2 * max_res)))
    pcf_dict["cell_measurement_theta_max"] = "{:.4f}".format(57.2958 * asin(wavelength /
                                                                            (2 * min_res)))
    pcf_dict["exptl_crystal_description"] = "nano-crystal"
    pcf_dict["diffrn_ambient_environment"] = "vacuum"
    pcf_dict["diffrn_measurement_device_type"] = "TEM"
    pcf_dict["diffrn_radiation_type"] = "electron"
    pcf_dict["diffrn_radiation_source"] = "electron"
    pcf_dict["diffrn_radiation_probe"] = "electron"
    pcf_dict["diffrn_radiation_wavelength"] = wavelength
    pcf_dict["diffrn_source"] = "electron microscope"
    h, m0, c, e = 6.62607015e-34, 9.10938356e-31, 2.99792458e8, 1.602176634e-19
    voltage = round((math.sqrt((m0 * c ** 2) ** 2 + (h * c / (wavelength * 1e-10)) ** 2) - m0 * c ** 2) / e / 1e4) * 10
    pcf_dict["diffrn_source_voltage"] = voltage
    pcf_dict["diffrn_measurement_device"] = "TEM"
    pcf_dict["diffrn_measurement_method"] = "Continuous Rotation Electron Diffraction"
    pcf_dict["diffrn_detector_area_resol_mean"] = "{:.4f}".format(1 / pixel)
    pcf_dict["diffrn_measurement_details"] = title + table
    pcf_dict["computing_cell_refinement"] = "XDS (Kabsch et al., 2010)"
    pcf_dict["computing_data_reduction"] = "XDS (Kabsch et al., 2010)"
    cred_log = os.path.join(os.path.dirname(input_path), "cRED_log.txt")
    xml_folder = os.path.dirname(input_path)
    if os.path.exists(cred_log):
        pcf_dict["computing_data_collection"] = "Instamatic (Wang et al., 2019)"
    else:
        for file_name in os.listdir(xml_folder):
            if file_name.endswith(".xml"):
                xml_path = os.path.join(xml_folder, file_name)
                with open(xml_path, 'r') as xml_file:
                    xml_content = xml_file.read()
                    if "EpuD" in xml_content:
                        pcf_dict["computing_data_collection"] = "EPU-D (Thermo Scientific, 2024)"
                        break
    if short_name:
        pcf_path = os.path.join(os.path.dirname(pcf_path), short_name + ".cif_od")
    print_pcf(pcf_path, pcf_dict, short_name)
    return wavelength


def update_pcf_file(input_path: str, pcf_path: str, info_dict: dict) -> float:
    """Update a `.pcf` file with new metadata.

    Arguments:
        input_path (str): Path to the directory containing metadata.
        pcf_path (str): Path to the `.pcf` file.
        info_dict (dict): Dictionary containing metadata information.

    Returns:
        float: Wavelength used in the experiment.
    """
    if info_dict.get("short_name", "1"):
        if " " in info_dict.get("short_name", "1"):
            short_name = info_dict.get("short_name", "1").split()[0]
        else:
            short_name = info_dict.get("short_name", "1")
    else:
        short_name = "1"
    with open(os.path.join(input_path, "metadata.json"), "r") as json_file:
        loaded_data = json.load(json_file)
    scan_list = []
    pcf_dict = load_cif(pcf_path)
    pcf_dict = pcf_dict[next(iter(pcf_dict))]
    for path in info_dict["input"]:
        dir_path = os.path.dirname(path)
        scan_list.append(loaded_data.get(dir_path))

    columns = ["#", "Type", "Start", "End", "Step", "t~exp~", "#Frames", "CL", "Reso.", "ISa", "CC1/2"]
    results_df = pd.DataFrame(columns=columns)
    cell_num = 0
    for i, item in enumerate(scan_list):
        cell_num += item["cell_rfl_num"]
        wavelength = item["wavelength"]
        pixel = item["pixel_size"]
        result = [i + 1, "/a", item["start_angle"], item["end_angle"], item["step"], item["time"], item["frames"],
                  item["camera_length"], item["resolution"], item["ISa_meas"], item["CC1/2"]]
        new_row = pd.DataFrame([result], columns=columns)
        results_df = pd.concat([results_df, new_row], ignore_index=True)

    headers = columns
    col_widths = [2, 4, 8, 8, 6, 9, 7, 8, 5, 5, 5]
    # Formatting the header
    header_str = "  ".join(f"{header:<{width}}" for header, width in zip(headers, col_widths))
    # Formatting the rows
    row_strs = []
    for index, row in results_df.iterrows():
        row_strs.append("  ".join(f"{str(val):<{width}}" for val, width in zip(row, col_widths)))
    # Combining everything into a formatted table
    table = f" {header_str}\n{'-' * (len(header_str) + 2)}\n " + "\n ".join(row_strs)
    # Adding the title
    title = "List of Samples for Merging (Abbr. = Camera Length, Resolution):\n"

    if info_dict.get("long_name", "").strip():
        pcf_dict["chemical_name_common"] = info_dict.get("long_name")
    elif short_name != "1":
        pcf_dict["chemical_name_common"] = short_name
    pcf_dict["cell_measurement_temperature"] = info_dict.get("temperature", "298") + "(3)"
    pcf_dict["cell_measurement_reflns_used"] = cell_num
    pcf_dict["cell_measurement_theta_min"] = "{:.4f}".format(57.2958 * asin(wavelength / (2 * 20)))
    pcf_dict["cell_measurement_theta_max"] = "{:.4f}".format(57.2958 * asin(wavelength /
                                                                            (2 * info_dict.get("resolution", 5.0))))
    pcf_dict["exptl_crystal_description"] = "nano-crystal"
    pcf_dict["diffrn_ambient_temperature"] = info_dict.get("temperature", "298") + "(3)"
    pcf_dict["diffrn_ambient_environment"] = "vacuum"
    pcf_dict["diffrn_measurement_device_type"] = "TEM"
    pcf_dict["diffrn_radiation_type"] = "electron"
    pcf_dict["diffrn_radiation_source"] = "electron"
    pcf_dict["diffrn_radiation_probe"] = "electron"
    pcf_dict["diffrn_radiation_wavelength"] = wavelength
    pcf_dict["diffrn_source"] = "electron microscope"
    h, m0, c, e = 6.62607015e-34, 9.10938356e-31, 2.99792458e8, 1.602176634e-19
    voltage = round((math.sqrt((m0 * c ** 2) ** 2 + (h * c / (wavelength * 1e-10)) ** 2) - m0 * c ** 2) / e / 1e4) * 10
    pcf_dict["diffrn_source_voltage"] = voltage
    pcf_dict["diffrn_detector"] = info_dict.get("detector", "?")
    pcf_dict["diffrn_measurement_device"] = "TEM"
    pcf_dict["diffrn_measurement_device_type"] = info_dict.get("instrument", "?")
    pcf_dict["diffrn_measurement_method"] = "Continuous Rotation Electron Diffraction"
    pcf_dict["diffrn_detector_area_resol_mean"] = "{:.4f}".format(1 / pixel)
    pcf_dict["diffrn_measurement_details"] = title + table
    if info_dict.get("instrument", "?") in ["JEOL-2100", "Themis Z"]:
        pcf_dict["computing_data_collection"] = "Instamatic (Wang et al., 2019)"
    else:
        pcf_dict["computing_data_collection"] = "EPU-D (Thermo Scientific, 2024)"
    pcf_dict["computing_cell_refinement"] = "XDS (Kabsch et al., 2010)"
    pcf_dict["computing_data_reduction"] = "XDS (Kabsch et al., 2010)"
    if short_name:
        pcf_path = os.path.join(os.path.dirname(pcf_path), short_name + ".cif_od")
    print_pcf(pcf_path, pcf_dict, short_name)
    return wavelength


def update_ins(
        file_path: str,
        temperature: str = None,
        wavelength: float = None,
        name: str = None,
) -> None:
    """Update a `.ins` file with new metadata and scattering factors.

    Arguments:
        file_path (str): Path to the `.ins` file.
        temperature (str, optional): Sample temperature. Defaults to None.
        wavelength (str, optional): Wavelength of the experiment. Defaults to None.
        name (str, optional): Name of the structure. Defaults to None.

    Returns:
        None
    """
    with open(file_path, "r") as f:
        lines = f.readlines()
    if name:
        file_path = os.path.join(os.path.dirname(file_path), name + ".ins")
    new_line = []
    for line in lines:
        if line.startswith('TITL') and name:
            title = line.split()
            title[1] = f"{name}"
            new_line.append("  ".join(title) + "\n")
        elif line.startswith("CELL") and wavelength:
            cell = line.split()
            cell[1] = f"{wavelength}"
            new_line.append("  ".join(cell) + "\n")
            if temperature:
                new_line.append(f"TEMP {int(temperature) - 273}\n")
        else:
            new_line.append(line)
    with open(file_path, "w") as f:
        f.writelines(new_line)
    print(f"{file_path} is updated. Use this for structure solving.\n")


if __name__ == "__main__":
    pass
