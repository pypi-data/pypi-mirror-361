"""
XDS Clustering Module
=====================

Provides tools for clustering X-ray diffraction datasets using correlation coefficients
from `XSCALE.LP` files. Supports dataset filtering, dendrogram computation and plotting,
cluster formation, and Bravais lattice analysis for crystallographic data.

Features:
    - Parse `XSCALE.LP` files to extract filenames, unit cell parameters, space group, and correlation matrices.
    - Compute and visualize dendrograms for dataset clustering.
    - Filter datasets based on specific criteria such as CC1/2, resolution, and ISa.
    - Form and merge clusters based on dendrogram thresholds.
    - Analyze lattice symmetry and aggregate results by Bravais lattice types.

Classes:
    None explicitly defined in this module.

Dependencies:
    - Standard libraries: `logging`, `sys`, `collections`, `threading`, `os`, `re`, `configparser`.
    - Third-party libraries: `pandas`, `matplotlib`, `numpy`, `scipy`, `tqdm`.

Credits:
    - Date: 2024-12-15
    - Authors: Developed by Yinlin Chen and Lei Wang
    - License: BSD 3-clause
"""

import configparser
import logging
import sys
from collections import defaultdict
from threading import Thread
from types import SimpleNamespace

import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QMessageBox, QApplication
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial import distance
from tqdm import tqdm

from .analysis_hkl import unit_cell_distance_procrustes
from .util import *
from .xds_analysis import extract_cluster_result, get_avg_esd_cell, extract_run_result
from .xds_shelx import convert_to_shelx

global cutoff_distance

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, '..', 'setting.ini'))

cell_cluster_distance = float(config['Cluster']['cell_cluster_distance'])
cell_cluster_symmetry = strtobool(config['Cluster']['cell_cluster_symmetry'])
is_wsl = is_wsl()


def get_paths_by_indicator(file_path: str, indicator: str, comparison_operator: str, value: float) -> list:
    """Filters dataset paths based on a specified indicator and comparison operator.

    Args:
        file_path (str): Path to the Excel file containing dataset information.
        indicator (str): The column name in the Excel file to filter on.
        comparison_operator (str): Comparison operator to use ('>' or '<').
        value (float): The threshold value for filtering.

    Returns:
        list: List of dataset paths that meet the filtering criteria.

    Raises:
        ValueError: If the indicator column is not found or an invalid operator is specified.
    """
    # Read the Excel file
    df = pd.read_excel(file_path, engine='openpyxl')

    # Check if the indicator column exists
    if indicator not in df.columns and indicator != "Reso.":
        raise ValueError(f"Indicator '{indicator}' not found in the Excel file.")
    elif indicator not in df.columns and indicator == "Reso." and "Pseudo Resolution" in df.columns:
        indicator = "Pseudo Resolution"

    # Filter based on the comparison operator
    if comparison_operator == '>':
        filtered_df = df[df[indicator] > value]
    elif comparison_operator == '<':
        filtered_df = df[df[indicator] < value]
    else:
        raise ValueError(f"Invalid comparison operator '{comparison_operator}'. Use '>' or '<'.")

    paths = filtered_df['Path'].tolist()

    return paths


def filter_data(directory_path: str, value: float, filter_type: str) -> None:
    """Filters datasets based on a specified filter type and value, then saves the filtered results.

    Args:
        directory_path (str): Path to the directory containing the data and Excel files.
        value (float): Threshold value for filtering.
        filter_type (str): Type of filter to apply ('cc12', 'isa', 'reso', 'rmeas').

    Effect:
        Saves the filtered dataset paths to `xdspicker.xlsx` within the specified directory.
    """
    if filter_type not in ['cc12', 'isa', 'reso', 'rmeas']:
        print("Invalid filter type specified. Use 'cc12', 'reso', 'rmeas' or 'isa'.")
        return

    print("********************************************")
    print("*                 XDS Picker               *")
    print("********************************************\n")

    excel_file_path = os.path.join(directory_path, 'xdsrunner2.xlsx')
    try:
        df = pd.read_excel(excel_file_path, engine='openpyxl')

        # Determine the column name based on the filter type
        column_name = {"cc12": "CC1/2", "isa": "ISa" if "ISa" in df else "Isa", "reso": "Reso.", "rmeas": "Rmeas"}

        # Ensure the column exists and filter the DataFrame
        if filter_type in ['reso', 'rmeas']:
            df_filtered = df[pd.to_numeric(df[column_name[filter_type]], errors='coerce').lt(value)]
        elif column_name[filter_type] in df.columns:
            df_filtered = df[pd.to_numeric(df[column_name[filter_type]], errors='coerce').gt(value)]
        else:
            print(f"Column '{column_name}' not found in the Excel file.")
            return

        output_path = os.path.join(directory_path, 'xdspicker.xlsx')
        if df_filtered.empty:
            QMessageBox.warning(QApplication.activeWindow(),
                                "Warning", "No Entry Satisfied the Criteria")
            print("No data filtered")
            return
        else:
            df_filtered.to_excel(output_path, index=False)
            print(f"{filter_type.upper()} filtering completed and saved to {output_path}")

    except Exception as e:
        QMessageBox.information(QApplication.activeWindow(),
                                "Caution", "The image path is updated successfully.")
        print(f"An error occurred: {e}")


def parse_xscale_lp(fn: str = "XSCALE.LP") -> SimpleNamespace:
    """
    Parses an XSCALE.LP file to extract filenames, unit cell parameters, space group,
    the correlation matrix, and the input parameters from the initial section.

    Only input blocks that contain a 'CRYSTAL_NAME' key are stored.

    Args:
        fn (str): Path to the `XSCALE.LP` file. Defaults to "XSCALE.LP".

    Returns:
        SimpleNamespace: Contains parsed data:
            - filenames (dict): Dataset filenames with corresponding indices.
            - correlation_matrix (np.ndarray): Correlation coefficients between datasets.
            - unit_cell (str): Unit cell parameters.
            - space_group (str): Space group number.
            - input_data (dict): Experiment parameters (only those blocks with CRYSTAL_NAME).
    """
    space_group = None
    unit_cell = None
    filenames = {}
    correlations = []
    input_data = {}
    current_block = {}

    # Precompile regex patterns for efficiency.
    re_digit_line = re.compile(r"^\d+")
    re_corr_line = re.compile(r"^\d+\s+\d+")

    # Section flags.
    reading_input = False
    reading_filenames = False
    reading_correlations = False

    # Helper function to flush the current input block if it contains a CRYSTAL_NAME.
    def flush_current_block():
        nonlocal current_block
        if current_block and "CRYSTAL_NAME" in current_block:
            # Use the value of CRYSTAL_NAME as the key.
            input_data[current_block["CRYSTAL_NAME"]] = current_block
        current_block = {}

    with open(fn, "r") as f:
        for line in f:
            line = line.strip()

            if line.startswith("SPACE_GROUP_NUMBER="):
                space_group = line.split("=", 1)[1].strip()
            elif line.startswith("UNIT_CELL_CONSTANTS="):
                unit_cell = line.split("=", 1)[1].strip()
                # Start reading the input blocks after we know the unit cell.
                reading_input = True
            elif "READING INPUT REFLECTION DATA FILES" in line:
                flush_current_block()
                reading_filenames = True
                reading_input = False
                reading_correlations = False
            elif "CORRELATIONS BETWEEN INPUT DATA SETS AFTER CORRECTIONS" in line:
                if reading_input:
                    flush_current_block()
                reading_filenames = False
                reading_correlations = True
                continue

            elif reading_input:
                # An empty line marks the end of a block.
                if not line:
                    flush_current_block()
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    current_block[key.strip()] = value.strip()

            elif reading_filenames:
                if line.startswith("DATA"):
                    continue
                if re_digit_line.match(line):
                    parts = line.split()
                    try:
                        idx = int(parts[0])
                        filenames[idx] = parts[-1]
                    except ValueError:
                        pass
                elif "OVERALL SCALING AND CRYSTAL DISORDER CORRECTION" in line:
                    reading_filenames = False

            elif reading_correlations:
                if not line or "NUMBER OF COMMON" in line:
                    continue
                if "K*EXP(B*SS)" in line:
                    reading_correlations = False
                    continue
                if re_corr_line.match(line):
                    parts = line.split()
                    try:
                        i = int(parts[0])
                        j = int(parts[1])
                        corr_value = float(parts[3])
                        correlations.append((i, j, corr_value))
                    except (IndexError, ValueError):
                        pass

    # Flush any remaining input block at the end.
    if reading_input and current_block:
        flush_current_block()

    # Build the correlation matrix.
    n = max(filenames.keys()) if filenames else 0
    corr_matrix = np.eye(n)
    for i, j, corr in correlations:
        corr_matrix[i - 1, j - 1] = corr
        corr_matrix[j - 1, i - 1] = corr

    return SimpleNamespace(
        correlation_matrix=corr_matrix,
        unit_cell=unit_cell,
        space_group=space_group,
        input_data=input_data
    )


def calculate_dendrogram(parsed_data: SimpleNamespace) -> np.ndarray:
    """Calculates a linkage matrix for hierarchical clustering.

    Args:
        parsed_data (SimpleNamespace): Parsed XSCALE.LP data containing the correlation matrix.

    Returns:
        np.ndarray: Linkage matrix for dendrogram computation.

    Raises:
        ValueError: If the correlation matrix is empty.
    """
    # Check if the correlation matrix is not empty and contains data
    if parsed_data.correlation_matrix.size == 0:
        raise ValueError("Correlation matrix is empty.")

    corr_mat = parsed_data.correlation_matrix
    # Convert correlation matrix to distance matrix for dendrogram calculation
    d_mat = np.sqrt(1 - corr_mat ** 2)
    # Condense the distance matrix since linkage function expects condensed form
    tri_upper = np.triu_indices_from(d_mat, k=1)
    condensed_dmat = d_mat[tri_upper]
    z = linkage(condensed_dmat, method="average")

    return z


def extract_dendrogram(input_path: str, interactive: bool = True, callback: callable = None,
                       work_folder: str = None) -> float:
    """Extracts and displays a dendrogram based on the input path using a PyQt6 dialog.

    Args:
        input_path (str): Path to the directory containing XSCALE.LP.
        interactive (bool): Enables interactive dendrogram adjustment if True. Defaults to True.
        callback (callable, optional): Function to execute with the selected cutoff distance.
        work_folder (str, optional): Path used when opening xdspicker.xlsx.

    Returns:
        float: The threshold distance at which the dendrogram is cut to form clusters (in interactive mode)
               or 0 if an error occurred.
    """
    print(f"\nDendrogram has received input path: {input_path}")
    xscale_lp_path = os.path.join(input_path, "XSCALE.LP")
    if os.path.exists(xscale_lp_path):
        print(f"Found XSCALE.LP at: {xscale_lp_path}")
        ccs = parse_xscale_lp(xscale_lp_path)
        # Check if correlation coefficients were found
        if ccs is None:
            print("No correlation coefficients found in XSCALE.LP.\n")
            if callback:
                callback(None)
            return 0.0
        z = calculate_dendrogram(ccs)
        plot_dendrogram(z, ccs, input_path, interactive, callback, work_folder)
    else:
        print("XSCALE.LP not found in the input directory.\n")
        if callback:
            callback(None)  # Notify callback of failure
        return 0.0


def plot_dendrogram(z: np.ndarray, ccs, input_path: str, interactive: bool = True,
                    callback: callable = None, work_folder: str = None) -> None:
    """Generates and optionally displays an interactive dendrogram using PyQt6.

    Args:
        z (np.ndarray): Linkage matrix for hierarchical clustering.
        ccs: An object (e.g. SimpleNamespace) that contains the input data (and possibly other metadata).
        input_path (str): Directory path to save the dendrogram image.
        interactive (bool): Enables interactive dendrogram adjustment if True. Defaults to True.
        callback (callable, optional): Function to execute with the selected cutoff distance.
        work_folder (str, optional): Folder path used to locate and open xdspicker.xlsx.
    """
    # Calculate an initial cutoff distance for the dendrogram.
    initial_distance = round(0.7 * max(z[:, 2]), 4)

    # Create the figure and axis for the dendrogram.
    fig = Figure(figsize=(7, 6))
    ax = fig.add_subplot(111)

    # Prepare the labels. If a crystal name starts with 'a', remove its first character.
    labels = np.array([
        a["CRYSTAL_NAME"][1:] if a["CRYSTAL_NAME"].startswith('a') else a["CRYSTAL_NAME"]
        for a in ccs.input_data.values()
    ])

    # Draw the dendrogram with the initial cutoff.
    hline = ax.axhline(y=initial_distance, color='#004c99', label='Current Cut-off')
    dendrogram(z, color_threshold=initial_distance, ax=ax,
               above_threshold_color="lightblue", labels=labels)
    ax.set_xlabel("Index")
    ax.set_ylabel("Distance")
    ax.set_title(f"Dendrogram ($t={initial_distance:.2f}$)")
    latest_cutoff = [initial_distance]  # Mutable holder for the current cutoff

    if interactive:
        # Create a modal QDialog for interactive adjustment.
        dialog = QDialog()
        dialog.setWindowModality(Qt.WindowModality.NonModal)
        dialog.setMinimumSize(750, 700)
        dialog.setWindowTitle("Interactive Dendrogram")
        layout = QVBoxLayout(dialog)

        # Create a FigureCanvas widget to host the matplotlib figure.
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        # Define the mouse-click event handler for adjusting the dendrogram.
        def onclick(event):
            nonlocal hline
            if event.ydata is not None:
                new_distance = round(event.ydata, 4)
                latest_cutoff[0] = new_distance  # Update the cutoff
                ax.set_title(f"Dendrogram ($t={new_distance:.2f}$)")
                hline.remove()
                hline = ax.axhline(y=new_distance, color='#004c99')
                # Remove previous dendrogram lines and redraw.
                for coll in ax.collections:
                    coll.remove()
                dendrogram(z, color_threshold=new_distance, ax=ax,
                           above_threshold_color="lightblue", labels=labels)
                canvas.draw()

        # Connect the matplotlib event to the onclick handler.
        connection_id = canvas.mpl_connect('button_press_event', onclick)

        # Define the handler for the "Open xdspicker.xlsx" button.
        def open_xdspicker():
            xdspicker_excel_path = os.path.join(work_folder, "xdspicker.xlsx")
            if os.path.exists(xdspicker_excel_path):
                try:
                    if is_wsl:
                        # Use explorer.exe to open the file in WSL.
                        subprocess.call(
                            ["wsl.exe", "cmd.exe", "/C",
                             f"start explorer.exe {linux_to_windows_path(xdspicker_excel_path)}"])
                        return
                    libreoffice_path = subprocess.run(["which", "libreoffice"],
                                                      capture_output=True, text=True).stdout.strip()
                    if libreoffice_path:
                        subprocess.call(["libreoffice", "--calc", xdspicker_excel_path])
                        return
                except Exception as e:
                    QMessageBox.critical(dialog, "Caution", f"Error opening the form due to {e}.")
                    return
                QMessageBox.critical(dialog, "Caution", "Neither LibreOffice nor Explorer is available.")
            else:
                QMessageBox.critical(dialog, "File Not Found",
                                     "Cannot find xdspicker.xlsx at the specified input path.")

        # Create and add the Open button.
        open_button = QPushButton("Open xdspicker.xlsx")
        open_button.clicked.connect(open_xdspicker)
        layout.addWidget(open_button)

        # Define what happens when the dialog is closed.
        def on_close():
            # Disconnect the event handler to avoid calling canvas.draw() on a deleted canvas.
            canvas.mpl_disconnect(connection_id)
            cutoff_distance = latest_cutoff[0]
            filepath = os.path.join(input_path, "dendrogram.png")
            fig.savefig(filepath)
            plt.close(fig)
            if callback:
                callback(cutoff_distance)

        dialog.finished.connect(on_close)
        dialog.exec()

    else:
        # Non-interactive: Generate the dendrogram and save it immediately.
        dendrogram(z, color_threshold=1, ax=ax,
                   above_threshold_color="lightblue", labels=labels)
        hline.remove()
        ax.set_xlabel("Index")
        ax.set_ylabel("Distance")
        ax.set_title("Dendrogram")
        filepath = os.path.join(input_path, "dendrogram.png")
        fig.savefig(filepath)
        plt.close(fig)
        print(f"Dendrogram saved to {filepath}")
        if callback:
            callback(None)


def make_cluster(input_path: str, distance: float, cover: bool = True) -> None:
    """Forms clusters from XDS datasets based on a specified dendrogram distance and optionally merges them.

    Args:
        input_path (str): Directory containing the `xdspicker.xlsx` file and `XSCALE.LP`.
        distance (float): Distance threshold for defining clusters.
        cover (bool): If True, overwrites existing clusters. Defaults to True.

    Effect:
        Clusters data and merges results into new datasets within the specified directory.
    """
    print(f"Clusters will be made based on {distance}")
    # Read Excel
    xlsx_file_path = os.path.join(input_path, "xdspicker.xlsx")
    df = pd.read_excel(xlsx_file_path, engine="openpyxl")
    df = df.dropna(how='all').reset_index(drop=True)
    # Calculate Dendrogram
    xscale_lp_path = os.path.join(input_path, "merge", "XSCALE.LP")
    ccs = parse_xscale_lp(xscale_lp_path)
    z = calculate_dendrogram(ccs)
    clusters = fcluster(z, distance, criterion='distance')
    value_to_indices = defaultdict(list)
    # Populate the dictionary with indices
    for index, value in enumerate(clusters):
        value_to_indices[value].append(index)
    # Extract indices for values that are not unique
    result = [indices for indices in value_to_indices.values() if len(indices) > 1]

    if not result:
        print("The cut-off distance may be too small to form cluster.")
        return

    # Whether cover the previous result or not
    if cover:
        for item in os.listdir(os.path.join(input_path, "merge")):
            item_path = os.path.join(os.path.join(input_path, "merge"), item)
            # Check if the item is a directory, then remove it
            if os.path.isdir(item_path) and ("cls" in item_path or "cluster" in item_path):
                shutil.rmtree(item_path)
        start_num = 1
    else:
        pattern = re.compile(r'dis(\d+)')
        # Initialize a list to store all matched numbers
        numbers = []
        # Loop through the subfolders in the parent directory
        for item in os.listdir(os.path.join(input_path, "merge")):
            # Check if the item is a directory and matches the pattern
            if os.path.isdir(os.path.join(input_path, "merge", item)):
                match = pattern.match(item)
                if match:
                    numbers.append(int(match.group(1)))

        # Find the maximum number if any matches were found
        if numbers:
            start_num = max(numbers) + 1
        else:
            start_num = 1

    print("Cluster will based on below settings:")
    with open(os.path.join(input_path, "merge", "Cluster-info.txt"), "w" if cover else "a") as file:
        for i, indices in enumerate(result):
            print("Distance{} - Cluster {}: [{}]".format(start_num, i + 1,
                                                         " ".join([str(index + 1) for index in indices])))
            file.write("Distance{} - Cluster {}: [{}]\n".format(
                start_num, i + 1, ", ".join([df["Path"][df.index[index]][2:]
                                             if df["Path"][df.index[index]].startswith(".")
                                             else df["Path"][df.index[index]]
                                             for index in indices])))

    # Start merging
    for i, indices in enumerate(result):
        merge(input_path, _filter=indices,
              folder="merge/dis{}-cls{}".format(start_num, i + 1), exclude_mode=False, alert=False)
        try:
            convert_to_shelx(input_path, xconv_folder="merge/dis{}-cls{}".format(start_num, i + 1))
        except Exception as e:
            print(f"Error occurred during converting to shelx: {e}")


# --- Modified merge function ---
def merge(input_path: str,
          _filter: list = None,
          folder: str = "merge",
          exclude_mode: bool = True,
          reso: float = None,
          alert: bool = True) -> None:
    """
    Combines multiple datasets into a single dataset based on specified criteria.

    Args:
        alert (bool): Raise alert when volume deviate a lot.
        input_path (str): Directory containing the `xdspicker.xlsx` file.
        _filter (list, optional): List of dataset indices to include or exclude.
        folder (str): Subdirectory to store the merged dataset and new `XSCALE.INP` file. Defaults to "merge".
        exclude_mode (bool): If True, excludes datasets specified in _filter. Defaults to True.
        reso (float, optional): Resolution limit for merging. Defaults to module resolution or 0.84 Å.

    Effect:
        Creates or updates an `XSCALE.INP` file in the specified directory and runs the XSCALE process.
    """
    print("********************************************")
    print("*                 XDS-Scale                *")
    print("********************************************\n")

    if not input_path:
        print("No input path provided.\n")
        return
    _filter = _filter or []

    # Create the merge directory inside the input path
    merge_dir = os.path.join(input_path, folder)
    os.makedirs(merge_dir, exist_ok=True)

    # Path to the xdspicker.xlsx file
    xlsx_file_path = os.path.join(input_path, "xdspicker.xlsx")

    try:
        df = pd.read_excel(xlsx_file_path, engine="openpyxl").dropna(how="all").reset_index(drop=True)
    except FileNotFoundError:
        print("The file specified does not exist.\n")
        return

    if df.empty or len(df) < 2:
        print("The xdspicker is empty or does not have enough datasets. Please check your xdspicker.xlsx\n")
        return

    # Determine resolution if not provided.
    if reso is None:
        if "Pseudo Resolution" in df.columns:
            reso = max(df["Pseudo Resolution"].dropna().min(), 0.84)
        elif "Reso." in df.columns:
            reso = max(df["Reso."].dropna().min(), 0.84)

    # Check consistency of the space-group column if available.
    if "SG" in df.columns:
        unique_sg = df["SG"].dropna().unique()
        if len(unique_sg) > 1 and alert:
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Inconsistent Space Groups",
                "Inconsistent values in SG column: {unique_sg}. Do you wish to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

    def parse_volume(vol):
        """Extracts a float from a volume string (e.g. '123.4(abc)')."""
        if pd.isna(vol):
            return None
        if isinstance(vol, (float, int)):
            return vol
        try:
            return float(vol.split("(")[0])
        except Exception:
            return None

    def get_xds_path(path: str) -> str:
        """Converts a relative path (starting with '...') to an absolute path."""
        path = str(path)
        if "..." in path:
            return os.path.join(input_path, path[4:])
        return path

    def get_hkl_path(row1: pd.Series) -> str:
        """Constructs the full path to the XDS_ASCII.HKL file."""
        path = str(row1["Path"])
        if "..." in path:
            return os.path.join(input_path, path[4:], "XDS_ASCII.HKL")
        return os.path.join(path, "XDS_ASCII.HKL")

    def get_resolution(row1: pd.Series) -> float:
        """Returns the resolution from the row using 'Pseudo Resolution' if available, otherwise 'Reso.'."""
        for col in ["Pseudo Resolution", "Reso."]:
            if col in row1 and pd.notna(row1[col]):
                try:
                    return float(row1[col])
                except ValueError:
                    continue
        return 0.8

    # === Filter the DataFrame ===
    df_valid = df[df["Path"].notna()]
    df_valid = df_valid[~df_valid["Path"].astype(str).str.contains(" ", na=False)]
    if _filter:
        if exclude_mode:
            df_valid = df_valid[~df_valid.index.isin(_filter)]
        else:
            df_valid = df_valid[df_valid.index.isin(_filter)]

    # === Prepare volume and folder lists ===
    vol_list = df_valid["Vol."].apply(parse_volume).dropna().tolist()
    path_folders = df_valid["Path"].apply(get_xds_path).tolist()

    # === Volume Outlier Detection ===
    if vol_list:
        mean_vol = np.mean(vol_list)
        std_vol = np.std(vol_list)
        max_sigma = 3
        filtered_vol_list = [v for v in vol_list if abs(v - mean_vol) <= max_sigma * std_vol]
        mean_filtered = np.mean(filtered_vol_list)
        std_filtered = np.std(filtered_vol_list)
        outliers = [v for v in vol_list if abs(v - mean_filtered) > max_sigma * std_filtered]
        if outliers and alert:
            max_deviation_sigma = max(abs(v - mean_filtered) / std_filtered for v in outliers)
            message = (f"{len(outliers)} of volumes deviate by more than {max_sigma} sigma.\n"
                       f"The mean volume is {mean_filtered:.1f} ± {std_filtered:.1f} "
                       f"({mean_filtered - 3 * std_filtered:.1f} – {mean_filtered + 3 * std_filtered:.1f})\n"
                       f"The maximum deviation is {max_deviation_sigma:.2f} sigma. Do you wish to continue?")
            reply = QMessageBox.question(
                QApplication.activeWindow(),
                "Outlier Warning",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                print("Process aborted by the user.")
                return

    # === Get Average Unit Cell Parameters ===
    avg_cell, esd_cell, wavelength = get_avg_esd_cell(
        "", multi=True, mode="list", folder_list=path_folders
    )
    ave_unitcell_str = " ".join(f"{x:.4f}" for x in avg_cell)

    # === Write XSCALE.INP file ===
    inp_file_path = os.path.join(merge_dir, "XSCALE.INP")
    with open(inp_file_path, "w") as inp_file:
        space_group_number = (df_valid["Space group"].iloc[0]
                              if "Space group" in df_valid.columns
                              else df_valid["SG"].iloc[0])
        inp_file.write(f"SPACE_GROUP_NUMBER= {int(space_group_number)}\n")
        inp_file.write(f"UNIT_CELL_CONSTANTS= {ave_unitcell_str}\n\n")
        inp_file.write("OUTPUT_FILE=all.HKL\n")
        inp_file.write("SAVE_CORRECTION_IMAGES=FALSE\n")
        inp_file.write("FRIEDEL'S_LAW=TRUE MERGE=FALSE\n")
        inp_file.write("STRICT_ABSORPTION_CORRECTION=FALSE\n")
        for _, row in df_valid.iterrows():
            resolution = get_resolution(row)
            ascii_hkl_path = get_hkl_path(row)
            inp_file.write("\n")
            inp_file.write(f"!{int(row['No.'])}\n")
            inp_file.write(f"INPUT_FILE={ascii_hkl_path}\n")
            inp_file.write(f"INCLUDE_RESOLUTION_RANGE=200 {resolution}\n")
            inp_file.write("CORRECTIONS= DECAY MODULATION ABSORPTION\n")
            inp_file.write(f"CRYSTAL_NAME=a{int(row['No.'])}\n")

    print("XSCALE.INP created successfully!\n")

    # === Run XSCALE and extract_cluster_result in Threads ===
    def run_xscale(directory: str):
        subprocess.run(["xscale"], cwd=directory)
        print("\nAll data from xdspicker has been merged.\n")

    xscale_thread = Thread(target=run_xscale, args=(merge_dir,))
    xscale_thread.start()
    xscale_thread.join()

    extract_thread = Thread(target=extract_cluster_result, args=(merge_dir, "SU", True, reso, True))
    extract_thread.start()
    extract_thread.join()


# Define this function at module level to make it picklable
def _process_distance_matrix_row(row_idx, matrices, distance_function, num_matrices):
    """Process a single row of the distance matrix.

    Args:
        row_idx (int): Index of the row to process
        matrices (list): List of matrices to calculate distances between
        distance_function (callable): Function to compute distances
        num_matrices (int): Total number of matrices

    Returns:
        list: List of tuples (i, j, distance) for the calculated distances
    """
    results = []
    for j in range(row_idx + 1, num_matrices):
        _distance = distance_function(matrices[row_idx], matrices[j])
        results.append((row_idx, j, _distance))
    return results


def calculate_distance_matrix(matrices: list, distance_function: callable,
                              parallel: bool = True, n_jobs: int = None,
                              use_threads: bool = False) -> np.ndarray:
    """Calculates the distance matrix for a set of matrices using a specified distance function.

    Args:
        matrices (list): List of matrices to calculate distances between.
        distance_function (callable): Function to compute the distance between two matrices.
        parallel (bool): Whether to use parallel processing. Defaults to True.
        n_jobs (int, optional): Number of processes to use. If None, uses all available processors.
        use_threads (bool): Use ThreadPoolExecutor instead of ProcessPoolExecutor for potentially
                           better performance with I/O-bound functions. Defaults to False.

    Returns:
        np.ndarray: Distance matrix as a NumPy array representing pairwise distances.
    """
    import concurrent.futures
    import os

    num_matrices = len(matrices)
    distances = np.zeros((num_matrices, num_matrices))

    # If there's only one matrix or none, or if parallel is False, use the sequential approach
    if num_matrices <= 20 or not parallel:
        for i in range(num_matrices):
            for j in range(i + 1, num_matrices):
                _distance = distance_function(matrices[i], matrices[j])
                distances[i, j] = distances[j, i] = _distance
        return distances

    # Determine optimal parameters
    if n_jobs is None:
        n_jobs = os.cpu_count() or 1

    # Choose the executor based on the use_threads parameter
    executor_class = concurrent.futures.ThreadPoolExecutor if use_threads else concurrent.futures.ProcessPoolExecutor

    # Process matrix rows in parallel
    with executor_class(max_workers=n_jobs) as executor:
        # Submit all rows at once
        futures = [executor.submit(_process_distance_matrix_row, i, matrices, distance_function, num_matrices)
                   for i in range(num_matrices - 1)]

        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            for i, j, _distance in future.result():
                distances[i, j] = distances[j, i] = _distance

    return distances


def calculate_stats(data: list) -> tuple:
    """Calculates the mean and standard error of the mean (SEM) for given data.

    Args:
        data (list): Data array to calculate statistics for.

    Returns:
        tuple: Contains the mean and SEM as lists of rounded values.
    """
    mean = np.round(np.mean(data, axis=0), 3).tolist()
    sem = np.round((np.std(data, axis=0) / np.sqrt(len(data))), 3).tolist()
    return mean, sem


def sort_cell_bravais_lattice(bravais_lattice: str, cell: list) -> list:
    """
    Sort the cell parameters based on the Bravais lattice type.

    Parameters:
        bravais_lattice (str): The type of Bravais lattice.
        cell (list or tuple): The cell parameters [a, b, c, ...].

    Returns:
        list: Sorted cell parameters.
    """
    if isinstance(cell, tuple):
        cell = list(cell)
    sorted_cell = cell.copy()
    if bravais_lattice in {"oP", "oI", "oF"}:
        sorted_cell[:3] = sorted(sorted_cell[:3])
    elif bravais_lattice == "oC":
        sorted_cell[:2] = sorted(sorted_cell[:2])
    return sorted_cell


def group_similar_entries(entries: list, tolerance: float = 0.05) -> list:
    """
    Group entries where the differences in a, b, c do not exceed the tolerance.

    Parameters:
        entries (list of dict): List of entries to group.
        tolerance (float): Maximum allowed difference in a, b, c.

    Returns:
        list of list: Grouped entries.
    """
    groups = []
    for entry in entries:
        a, b, c = entry['cell_bravais_lattice'][:3]
        placed = False
        for group in groups:
            ga, gb, gc = group[0]['cell_bravais_lattice'][:3]
            if (abs(a - ga) / ga <= tolerance and
                    abs(b - gb) / gb <= tolerance and
                    abs(c - gc) / gc <= tolerance):
                group.append(entry)
                placed = True
                break
        if not placed:
            groups.append([entry])
    return groups


def aggregate_by_bravais_lattice(cluster_data: dict) -> dict:
    """Aggregates unit cell information by Bravais lattice type.

    Args:
        cluster_data (dict): Cluster data containing unit cell and symmetry information.

    Returns:
        dict: Aggregated data categorized by Bravais lattice type, with mean and SEM of parameters.
    """
    bravais_lattice_groups = defaultdict(list)

    # Initial grouping by Bravais lattice with sorted cell parameters
    for path, cell_info in cluster_data.items():
        for bravais_lattice, entries in cell_info.items():
            for entry in entries:
                # Sort cell parameters based on Bravais lattice
                sorted_cell = sort_cell_bravais_lattice(bravais_lattice, entry['cell_bravais_lattice'])
                entry['cell_bravais_lattice'] = sorted_cell
                bravais_lattice_groups[bravais_lattice].append(entry)

    aggregated_data = {}

    for bravais_lattice, entries in bravais_lattice_groups.items():
        # For "mP" and "mC", perform secondary grouping
        if bravais_lattice in {"mP", "mC"}:
            grouped_entries = group_similar_entries(entries, tolerance=0.10)
            for idx, group in enumerate(grouped_entries, start=1):
                subgroup_name = f"{bravais_lattice} (setting {idx})"

                # Aggregate statistics for the subgroup
                cell_bravais_lattices = [entry['cell_bravais_lattice'] for entry in group]
                diffs = [entry['diff'] for entry in group]
                qof_values = [entry['qof'] for entry in group]

                mean_cell, stdev_cell = calculate_stats(cell_bravais_lattices)
                mean_diff = round(np.mean(diffs), 4)
                mean_qof = round(np.mean(qof_values), 1)

                sg_r_meas_ratios = defaultdict(list)
                sg_cc12 = defaultdict(list)
                for entry in group:
                    sg_r_meas_ratios[entry['sg_no']].append(entry['r_meas_ratio'])
                    sg_cc12[entry['sg_no']].append(entry['cc12_ratio'])

                mean_r_meas_ratios = {sg_no: round(np.mean(r_meas), 3)
                                      for sg_no, r_meas in sg_r_meas_ratios.items()}
                mean_cc12 = {sg_no: round(np.mean(cc12), 3)
                             for sg_no, cc12 in sg_cc12.items()}
                sg_counts = {sg_no: len(r_meas)
                             for sg_no, r_meas in sg_r_meas_ratios.items()}

                aggregated_data[subgroup_name] = {
                    'mean_cell_bravais_lattice': mean_cell,
                    'stdev_cell_bravais_lattice': stdev_cell,
                    'mean_diff': mean_diff,
                    'mean_qof': mean_qof,
                    'mean_r_meas_ratios': mean_r_meas_ratios,
                    'mean_cc12': mean_cc12,
                    'sg_counts': sg_counts
                }
        else:
            cell_bravais_lattices = [entry['cell_bravais_lattice'] for entry in entries]
            diffs = [entry['diff'] for entry in entries]
            qof_values = [entry['qof'] for entry in entries]

            mean_cell, stdev_cell = calculate_stats(cell_bravais_lattices)
            mean_diff = round(np.mean(diffs), 4)
            mean_qof = round(np.mean(qof_values), 1)

            sg_r_meas_ratios = defaultdict(list)
            sg_cc12 = defaultdict(list)
            for entry in entries:
                sg_r_meas_ratios[entry['sg_no']].append(entry['r_meas_ratio'])
                sg_cc12[entry['sg_no']].append(entry['cc12_ratio'])

            mean_r_meas_ratios = {sg_no: round(np.mean(r_meas), 3)
                                  for sg_no, r_meas in sg_r_meas_ratios.items()}
            mean_cc12 = {sg_no: round(np.mean(cc12), 3)
                         for sg_no, cc12 in sg_cc12.items()}
            sg_counts = {sg_no: len(r_meas)
                         for sg_no, r_meas in sg_r_meas_ratios.items()}

            aggregated_data[bravais_lattice] = {
                'mean_cell_bravais_lattice': mean_cell,
                'stdev_cell_bravais_lattice': stdev_cell,
                'mean_diff': mean_diff,
                'mean_qof': mean_qof,
                'mean_r_meas_ratios': mean_r_meas_ratios,
                'mean_cc12': mean_cc12,
                'sg_counts': sg_counts
            }
    return aggregated_data


def setup_logging(folder_path: str) -> None:
    """Sets up logging configuration for the module, directing logs to both a file and the console.

    Args:
        folder_path (str): Path to the folder where log files will be saved.

    Effect:
        Initializes logging to `lattice_cluster.txt` in the specified directory and configures console output.
    """
    log_file_path = os.path.join(folder_path, 'lattice_cluster.txt')

    with open(log_file_path, 'w') as file:
        file.write('\n')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Create a file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(logging.Formatter('%(message)s'))

    # Create a stream handler for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(message)s'))

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def log_info(logger: logging.Logger, message: str) -> None:
    """Logs an informational message to both the console and the log file.

    Args:
        logger (logging.Logger): The logger instance to use.
        message (str): The message to log.

    Effect:
        Outputs the message to the configured logging handlers.
    """
    logger.info(message)


def log_file_only(folder_path: str, message: str) -> None:
    """Logs a message exclusively to the log file.

    Args:
        folder_path (str): Path to the folder containing the log file.
        message (str): The message to log.

    Effect:
        Appends the message to `lattice_cluster.txt` in the specified directory.
    """
    with open(os.path.join(folder_path, 'lattice_cluster.txt'), 'a') as file:
        file.write(message + '\n')


def log_header(logger: logging.Logger) -> None:
    """Logs the header information for the lattice symmetry analysis.

    Args:
        logger (logging.Logger): The logger instance to use.

    Effect:
        Outputs predefined header information to the log.
    """
    log_info(logger, "\n********************************************")
    log_info(logger, "*         Lattice Symmetry Explorer        *")
    log_info(logger, "********************************************\n")
    log_info(logger, (
        "A script using to estimate lattice symmetry based on reflection data statistics. \n"
        "The recommended lattice difference should be < 2.5, and the Figure of Merit (FOM) should be < 200.\n"
        "For a given Bravais lattice, multiple space groups may be available. The R_meas ratio of each space\n"
        "group to P1 will be provided following the space group name, with a recommended value of < 1.8\n\n"
        "                    R_meas ratio = R_meas(Space Group) / R_meas(P1)                          \n"
        "                CC1/2 ratio = [1 - CC1/2(Space Group)] / [1 - CC1/2(P1)]                     \n"))


def log_lattice_symmetry_info(logger: logging.Logger, aggregated_data: dict, sg_name_dict: dict) -> None:
    """Logs detailed lattice symmetry information based on aggregated data.

    Args:
        logger (logging.Logger): The logger instance to use.
        aggregated_data (dict): Aggregated data categorized by Bravais lattice types.
        sg_name_dict (dict): Dictionary mapping space group numbers to their names.

    Effect:
        Outputs structured lattice symmetry information to the log.
    """
    lattice_choice_info = "**  Lattice Choice:"
    log_info(logger, lattice_choice_info)

    for bravais_lattice, data in aggregated_data.items():
        lattice_info = (
            f"--  Bravais Lattice: {bravais_lattice}\n"
            f"    Averaged Cell: {tuple(data['mean_cell_bravais_lattice'])},"
            f" Lattice Difference: {data['mean_diff']}, FOM: {data['mean_qof']}\n"
            f"    SEM of Cell: {tuple(data['stdev_cell_bravais_lattice'])}"
        )
        log_info(logger, lattice_info)

        sg_stat = []
        for sg_no, r_meas in data['mean_r_meas_ratios'].items():
            sg_stat.append(f"{sg_name_dict[sg_no]} (No. {sg_no}) : {r_meas}(R), {data['mean_cc12'][sg_no]}(C)")
        if len(sg_stat) > 4:
            sg_stat[3] = "\n    Suggested Space Group: " + sg_stat[3]
        suggested_sg = f"    Suggested Space Group: {' / '.join(sg_stat)}\n"
        log_info(logger, suggested_sg)


def process_single_run(logger: logging.Logger, analysis_dict: dict, sg_name_dict: dict) -> None:
    """Processes and logs lattice symmetry information for a single dataset run.

    Args:
        logger (logging.Logger): The logger instance to use.
        analysis_dict (dict): Dictionary containing analysis results for the dataset.
        sg_name_dict (dict): Dictionary mapping space group numbers to their names.

    Effect:
        Logs detailed symmetry information for the single dataset.
    """
    cluster_info = f"\n*****************"
    data_path_info = "**  Data Path: 1 datasets, (100%) \n{}\n".format(
        '\n'.join(list(analysis_dict.keys()))
    )

    log_info(logger, cluster_info)
    log_info(logger, data_path_info)

    aggregated_data = aggregate_by_bravais_lattice(analysis_dict)
    log_lattice_symmetry_info(logger, aggregated_data, sg_name_dict)


def process_multiple_runs(logger: logging.Logger, analysis_dict: dict, sg_name_dict: dict, folder_path: str) -> None:
    """Processes and logs lattice symmetry information for multiple dataset runs.

    Args:
        logger (logging.Logger): The logger instance to use.
        analysis_dict (dict): Dictionary containing analysis results for all datasets.
        sg_name_dict (dict): Dictionary mapping space group numbers to their names.
        folder_path (str): Path to the folder where logs and results will be saved.

    Effect:
        Logs detailed symmetry information for each cluster of datasets.
    """
    unit_cell_matrices = [list(cell.values())[0][0]["cell_parameters"] for cell in analysis_dict.values()]
    Z = linkage(distance.squareform(calculate_distance_matrix(unit_cell_matrices, unit_cell_distance_procrustes)),
                method='average')
    labels = fcluster(Z, t=cell_cluster_distance, criterion='distance')

    # import matplotlib.pyplot as plt
    # from scipy.cluster.hierarchy import dendrogram
    #
    # # Plot the dendrogram
    # plt.figure(figsize=(10, 7))
    # dendrogram(Z, color_threshold=0.2)
    # plt.title('Dendrogram')
    # plt.xlabel('Sample')
    # plt.ylabel('Distance')
    # plt.show()

    clustered_dicts = {}
    for label, path in zip(labels, analysis_dict.keys()):
        if label not in clustered_dicts:
            clustered_dicts[label] = {}
        clustered_dicts[label][path] = analysis_dict[path]

    new_clusters = defaultdict(dict)
    if cell_cluster_symmetry:
        for cluster_id, cluster_data in clustered_dicts.items():
            sub_clusters = defaultdict(dict)
            for path, cell in cluster_data.items():
                bravais_lattice = list(cell.values())[0][0]['bravais_lattice']
                sub_clusters[bravais_lattice][path] = cell
            for sub_cluster_id, sub_cluster_data in sub_clusters.items():
                new_cluster_id = f"{cluster_id}-{sub_cluster_id}"
                new_clusters[new_cluster_id] = sub_cluster_data
        sorted_clusters = sorted(new_clusters.items(), key=lambda item: len(item[1]), reverse=True)
    else:
        sorted_clusters = sorted(clustered_dicts.items(), key=lambda item: len(item[1]), reverse=True)

    ranked_clusters = {f"Cluster-{rank + 1}": cluster_data for rank, (cluster_id, cluster_data) in
                       enumerate(sorted_clusters)}

    for cluster_id, cluster_data in ranked_clusters.items():
        cluster_info = f"\n******* {cluster_id}: *******"
        data_path_info = "**  Data Path: {} datasets, ({}%) \n{}\n".format(
            len(cluster_data), round(len(cluster_data) / len(analysis_dict) * 100, 1),
            '\n'.join(list(cluster_data.keys()))
        )

        # Log to console and file
        log_info(logger, cluster_info)
        log_info(logger, data_path_info)

        aggregated_data = aggregate_by_bravais_lattice(cluster_data)

        # Log lattice symmetry info to console
        log_lattice_symmetry_info(logger, aggregated_data, sg_name_dict)

        log_file_only(folder_path, "\n***********************************************")
        log_file_only(folder_path, "***********************************************")
        log_file_only(folder_path, "*       Information for Single Dataset        *\n")

        # Log individual dataset information to file only
        for path, sets in cluster_data.items():
            individual_info = f"\nDetailed Info for Dataset: {path}"
            log_file_only(folder_path, individual_info)
            aggregated_data = aggregate_by_bravais_lattice({path: sets})

            for bravais_lattice, data in aggregated_data.items():
                lattice_info = (
                    f"--  Bravais Lattice: {bravais_lattice}\n"
                    f"    Averaged Cell: {tuple(data['mean_cell_bravais_lattice'])},"
                    f" Lattice Difference: {data['mean_diff']}, FOM: {data['mean_qof']}\n"
                    f"    SEM of Cell: {tuple(data['stdev_cell_bravais_lattice'])}"
                )
                log_file_only(folder_path, lattice_info)

                sg_stat = []
                for sg_no, r_meas in data['mean_r_meas_ratios'].items():
                    sg_stat.append(
                        f"{sg_name_dict[sg_no]} (No. {sg_no}) : {r_meas}(R), {data['mean_cc12'][sg_no]}(C)")
                suggested_sg = f"    Suggested Space Group: {' / '.join(sg_stat)}\n"
                log_file_only(folder_path, suggested_sg)


def analysis_lattice_symmetry(folder_path: str, path_filter: bool = None) -> None:
    """Analyzes lattice symmetry for datasets within a specified folder, logging detailed results.

    Args:
        folder_path (str): Path to the folder containing datasets and `XDS_ASCII.HKL` files.
        path_filter (bool): Filter path starting with "!" or ".".

    Effect:
        Generates a comprehensive lattice symmetry analysis, logs the results, and saves them
        to `lattice_cluster.txt` within the folder.
    """
    setup_logging(folder_path)
    logger = logging.getLogger()

    sg_name_dict = {
        1: "P1", 3: "P121", 5: "C121", 16: "P222", 21: "C222", 22: "F222", 23: "I222", 75: "P4", 79: "I4", 89: "P422",
        97: "I422", 143: "P3", 146: "R3", 149: "P321", 150: "P312", 155: "R32", 168: "P6", 177: "P622", 195: "P23",
        196: "F23", 197: "I23", 207: "P432", 209: "F432", 211: "I432"
    }

    log_header(logger)

    dir_list = [os.path.dirname(path) for path in find_files(folder_path, "XDS_ASCII.HKL", path_filter=path_filter)]
    analysis_dict = {}
    for path in tqdm(dir_list, ascii=True, desc="Testing Lattice Symmetry"):
        try:
            temp_results = extract_run_result(path)
            if temp_results["lattice_choice"]:
                analysis_dict[path] = temp_results["lattice_choice"]
        except Exception as e:
            pass

    if len(analysis_dict) == 0:
        log_info(logger, "Either XDS are running under cell mode or Insufficient Runs.")
        return
    elif len(analysis_dict) == 1:
        process_single_run(logger, analysis_dict, sg_name_dict)
        return

    process_multiple_runs(logger, analysis_dict, sg_name_dict, folder_path)


if __name__ == "__main__":
    pass
