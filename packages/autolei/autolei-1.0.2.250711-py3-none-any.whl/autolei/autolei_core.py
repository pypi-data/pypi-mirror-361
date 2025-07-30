"""
AutoLEI Core Module

This module is a core component of the AutoLEI application, designed to facilitate the processing
and analysis of electron diffraction data using XDS and related tools. It provides a comprehensive
graphical user interface (GUI) built with Tkinter, enabling users to configure experiment parameters,
manage data processing workflows, perform data merging, handle clustering based on correlation
coefficients, refine unit cell parameters, and generate detailed reports. The module ensures
efficient and user-friendly interaction by leveraging multithreading to maintain GUI responsiveness
during long-running tasks.

Key Functionalities:
    1. **Input Configuration (`Input` Class):**
        - Browse and select working directories.
        - Load and manage instrument profiles.
        - Input and save experiment parameters necessary for XDS input file generation.

    2. **Batch Data Processing (`XDSRunner` Class):**
        - Convert various image formats (MRC, NXS, TIFF) to SMV format.
        - Generate and update XDS.INP files based on user-defined parameters.
        - Execute XDS processing in batch mode across multiple datasets.
        - Estimate symmetry and perform unit cell clustering.
        - Display and manage processing results through Excel integration.

    3. **Unit Cell Correction (`UnitCellCorr` Class):**
        - Input and manage space group numbers and unit cell parameters.
        - Save and apply unit cell information to all relevant XDS.INP files.
        - Rerun XDS processing with updated cell parameters for refined data reduction.

    4. **Data Merging (`MergeData` Class): **
        - Filter datasets based on statistical criteria such as I/Sigma, CC1/2, R_meas, and Resolution.
        - Merge selected datasets using XDS's XScale tool.
        - Display and manage merging results, including the generation of SHELX input files.

    5. **Cluster Management (`Cluster_Output` Class):**
        - Cluster datasets based on correlation coefficients extracted from XSCALE.LP files.
        - Set clustering distances either from dendrogram analysis or manual input.
        - Run XPREP for generating SHELX .ins files for crystallographic refinement.
        - Generate and view web-based reports summarising cluster analyses.

    6. **Unit Cell Refinement (`XDSRefine` Class): **
        - Refine input parameters in XDS.INP files based on user-provided space group and unit cell information.
        - Manage and apply unit cell corrections across multiple datasets.
        - Facilitate the generation of updated XDS.INP files for accurate data reduction.
        - Integrate with clustering results to ensure consistency in refined parameters.

Dependencies:
    - **Standard Libraries:**
        - `os`, `sys`, `shutil`, `glob`, `json`, `subprocess`, `threading`
    - **Third-Party Libraries:**
        - `tkinter`: For building the graphical user interface.
        - `PIL (Pillow)`: For image processing and display.
        - `pandas`: For data manipulation and Excel file handling.
        - `openpyxl`: For reading and writing Excel files.
    - **Custom Modules (Within AutoLEI Core):**
        - `xds_input`: Handling XDS.INP file generation and modification.
        - `image_io`: Managing image format conversions and beam centre calculations.
        - `xds_runner`: Orchestrating XDS batch processing workflows.
        - `xds_cluster`: Performing clustering based on data correlations.
        - `xds_shelx`: Converting merged data to SHELX format.
        - `html_report`: Generating visual and web-based reports.
        - `util`: Providing utility functions and classes (e.g. tooltips, path handling).

Configuration:
    The module reads configuration settings from a `setting.ini` file located in the same directory.
    These settings include parameters for input filtering, paths to external applications like XPREP,
    and other general configurations that influence the module's behaviour.

Usage:
    The module is structured as a series of Tkinter `Page` classes, each representing a different
    section of the AutoLEI GUI. Users interact with these pages to perform various tasks related
    to data processing, parameter configuration, and result analysis. The application ensures
    that all operations are executed in separate threads to maintain a responsive user interface.

Contact:
    - Lei Wang: lei.wang@su.se
    - Yinlin Chen: yinlin.chen@su.se

License:
    BSD 3-Clause Licence
"""

import configparser

from PyQt5.QtGui import QFont, QPixmap

try:
    from .src import xds_input, image_io, xds_analysis, xds_runner, xds_cluster, xds_shelx
    from .src.visualisation import html_report
    from .src.util import *
    from .src.symm_shelx.space_group_finder import DEFAULT_SGC
    from .src.file_io.folder_move_manager import FileMover
except ImportError:
    from src import xds_input, image_io, xds_analysis, xds_runner, xds_cluster, xds_shelx
    from src.visualisation import html_report
    from src.util import *
    from src.symm_shelx.space_group_finder import DEFAULT_SGC
    from src.file_io.folder_move_manager import FileMover

from functools import partial
import glob
import pandas as pd
from numpy import cos, radians, arccos
import os
import json
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QButtonGroup, QRadioButton, QCheckBox, QTreeWidget,
    QAbstractItemView, QSizePolicy, QSpacerItem, QDialog, QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QSize, QProcess, QPoint

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'setting.ini'))

analysis_engine = config["XDSRunner"]["engine_hkl_analysis"]
path_filter = strtobool(config["General"]["path_filter"])

is_wsl = is_wsl()
spgfinder = DEFAULT_SGC


class Input(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_fields = {}
        self.path_dict = {}

        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(18)
        main_layout.addSpacing(12)

        # Instruction label
        instruction_label = QLabel(
            "Browse and load the work path where the program will load the measurement settings.\n"
            "For XDS input generation, supply basic parameters and click the 'Save Parameter' button.", self)
        instruction_label.setWordWrap(True)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(instruction_label)

        # ---------------- Row 1 layout (pack at left) ----------------
        row1_layout = QHBoxLayout()
        # Force everything in row1_layout to the left
        row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row1_layout)

        # Label
        label_input_path = QLabel("Input path:", self)
        row1_layout.addWidget(label_input_path)

        # Entry
        self.path_entry = QLineEdit(self)
        self.path_entry.setFixedWidth(400)
        self.path_entry.setToolTip("The working directory in Linux / WSL.")
        row1_layout.addWidget(self.path_entry)

        # Browse button
        browse_button = QPushButton("Browse", self)
        browse_button.setToolTip("Select the working directory.")
        browse_button.clicked.connect(self.select_path)
        row1_layout.addWidget(browse_button)

        # Load Path button
        load_path_button = QPushButton("Load Path", self)
        load_path_button.setToolTip("Load and analyse the chosen path.")
        load_path_button.clicked.connect(self.load_path)
        row1_layout.addWidget(load_path_button)

        # Instrument label + combo + load button
        instrument_label = QLabel("Instrument:", self)
        row1_layout.addWidget(instrument_label)

        self.instrument_combo = ComboBox(self)
        self.instrument_combo.setMaxVisibleItems(10)
        # example items
        self.path_dict = self.load_instrument_profile()
        options = ["Custom"] + list(self.path_dict.keys()) + ["Browse..."]
        self.instrument_combo.addItems(options)
        self.instrument_combo.setFixedWidth(250)
        self.instrument_combo.currentIndexChanged.connect(self.handle_option_select)
        self.instrument_combo.setToolTip("Select an instrument profile.")
        row1_layout.addWidget(self.instrument_combo)

        load_instrument_button = QPushButton("Load", self)
        load_instrument_button.setToolTip("Load the selected instrument parameters.")
        load_instrument_button.clicked.connect(self.load_instrument_parameter)
        row1_layout.addWidget(load_instrument_button)
        row1_layout.addStretch()

        # ------------- Instrument Parameters (Section Heading) -------------
        label_instrument_section = QLabel("I. Instrument Parameters", self)
        label_instrument_section.setStyleSheet("font-weight: bold;")
        label_instrument_section.setFixedHeight(30)
        main_layout.addWidget(label_instrument_section)

        # ------------- Row 3 (NX, NY, QX, QY) -------------
        row3_layout = QHBoxLayout()
        main_layout.addLayout(row3_layout)
        row3_layout.addSpacing(12)

        detector_label = QLabel("1. Detector parameters:", self)
        row3_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row3_layout.addWidget(detector_label)

        def add_param(grid, text):
            lbl = QLabel(text, self)
            grid.addWidget(lbl)
            line_edit = QLineEdit(self)
            line_edit.setFixedWidth(80)
            grid.addWidget(line_edit)
            line_edit.setToolTip(text)
            self.input_fields[text] = line_edit

        add_param(row3_layout, "NX=")
        add_param(row3_layout, "NY=")
        add_param(row3_layout, "QX=")
        add_param(row3_layout, "QY=")
        row3_layout.addStretch()

        # ------------- Row 4 (Overload, Wavelength) -------------
        row4_layout = QHBoxLayout()
        main_layout.addLayout(row4_layout)
        row4_layout.addSpacing(12)

        overload_label = QLabel("2. Overloading: OVERLOAD=", self)
        row4_layout.addWidget(overload_label)

        self.input_fields["OVERLOAD="] = QLineEdit(self)
        self.input_fields["OVERLOAD="].setFixedWidth(100)
        self.input_fields["OVERLOAD="].setToolTip("SMV image will have a highest intensity of 65535.")
        row4_layout.addWidget(self.input_fields["OVERLOAD="])

        wavelength_label = QLabel("   3. Wavelength: WAVELENGTH=", self)
        row4_layout.addSpacing(200)
        row4_layout.addWidget(wavelength_label)

        self.input_fields["X-RAY_WAVELENGTH="] = QLineEdit(self)
        self.input_fields["X-RAY_WAVELENGTH="].setFixedWidth(100)
        self.input_fields["X-RAY_WAVELENGTH="].setToolTip(
            "120 kV, 0.03349 Å; \n200 kV, 0.02508 Å; \n300 kV, 0.01969 Å."
        )
        row4_layout.addWidget(self.input_fields["X-RAY_WAVELENGTH="])

        ang_label = QLabel(" Å", self)
        row4_layout.addWidget(ang_label)
        row4_layout.addStretch()

        # ------------- Row 5 (Rotation Axis, Rotation Angle) -------------
        row5_layout = QHBoxLayout()
        main_layout.addLayout(row5_layout)
        row5_layout.addSpacing(12)

        rotation_axis_label = QLabel("4. Rotation axis:  ROTATION_AXIS=", self)
        row5_layout.addWidget(rotation_axis_label)

        self.input_fields["ROTATION_AXIS="] = QLineEdit(self)
        self.input_fields["ROTATION_AXIS="].setFixedWidth(250)
        self.input_fields["ROTATION_AXIS="].setToolTip("Should leave blank if entering rotation angle.")
        row5_layout.addWidget(self.input_fields["ROTATION_AXIS="])

        angle_label = QLabel(" or   Angle in Degree=", self)
        row5_layout.addWidget(angle_label)

        self.input_fields["ROTATION_ANGLE"] = QLineEdit(self)
        self.input_fields["ROTATION_ANGLE"].setFixedWidth(100)
        self.input_fields["ROTATION_ANGLE"].setToolTip("Rotation angle in degrees from x+.")
        row5_layout.addWidget(self.input_fields["ROTATION_ANGLE"])
        row5_layout.addStretch()

        # ------------- Row 6 (Additional Info) -------------
        additional_layout1 = QHBoxLayout()
        main_layout.addLayout(additional_layout1)
        main_layout.addSpacing(8)
        additional_layout1.addSpacing(12)

        additional_label = QLabel(
            "5. Additional information \n  (Please copy from XDS):",
            self
        )
        additional_layout1.addWidget(additional_label)

        self.input_fields["Additional_Info"] = QTextEdit(self)
        self.input_fields["Additional_Info"].setFixedHeight(180)
        self.input_fields["Additional_Info"].setToolTip(
            "Information on untrusted area and keywords for data reduction.\n"
            "Caution! Please ensure the keywords are valid in XDS."
        )
        additional_layout1.addWidget(self.input_fields["Additional_Info"])

        # ------------- Measurement Parameters (Section Heading) -------------
        label_measurement_section = QLabel("II. Measurement Parameters", self)
        label_measurement_section.setStyleSheet("font-weight: bold;")
        label_measurement_section.setFixedHeight(30)
        main_layout.addWidget(label_measurement_section)

        # ------------- Row 8 (ORGX, ORGY) -------------
        row8_layout = QHBoxLayout()
        main_layout.addLayout(row8_layout)
        row8_layout.addSpacing(12)

        org_label = QLabel("6. Direct beam position: ORGX=", self)
        row8_layout.addWidget(org_label)

        self.input_fields["ORGX="] = QLineEdit(self)
        self.input_fields["ORGX="].setFixedWidth(150)
        self.input_fields["ORGX="].setToolTip("X of the origin point, can be calculated later.")
        row8_layout.addWidget(self.input_fields["ORGX="])

        orgy_label = QLabel("ORGY=", self)
        row8_layout.addWidget(orgy_label)

        self.input_fields["ORGY="] = QLineEdit(self)
        self.input_fields["ORGY="].setFixedWidth(150)
        self.input_fields["ORGY="].setToolTip("Y of the origin point, can be calculated later.")
        row8_layout.addWidget(self.input_fields["ORGY="])
        row8_layout.addStretch()

        # ------------- Row 9 (Resolution Range) -------------
        row9_layout = QHBoxLayout()
        main_layout.addLayout(row9_layout)
        row9_layout.addSpacing(12)

        include_label = QLabel("7. Resolution range:  INCLUDE_RESOLUTION_RANGE=", self)
        row9_layout.addWidget(include_label)

        self.input_fields["INCLUDE_RESOLUTION_RANGE="] = QLineEdit(self)
        self.input_fields["INCLUDE_RESOLUTION_RANGE="].setFixedWidth(120)
        self.input_fields["INCLUDE_RESOLUTION_RANGE="].setToolTip("The resolution range of the data reduction.")
        row9_layout.addWidget(self.input_fields["INCLUDE_RESOLUTION_RANGE="])

        hint_label = QLabel(">>> Use space to segment", self)
        row9_layout.addWidget(hint_label)
        row9_layout.addStretch()

        # ------------- Row 10 (Detector Distance, Oscillation Range) -------------
        row10_layout = QHBoxLayout()
        main_layout.addLayout(row10_layout)
        row10_layout.addSpacing(12)

        distance_label = QLabel("8. Camera Length: DETECTOR_DISTANCE=", self)
        row10_layout.addWidget(distance_label)

        self.input_fields["DETECTOR_DISTANCE="] = QLineEdit(self)
        self.input_fields["DETECTOR_DISTANCE="].setFixedWidth(100)
        self.input_fields["DETECTOR_DISTANCE="].setToolTip(
            "Camera length in TEM, can be corrected later by image header."
        )
        row10_layout.addWidget(self.input_fields["DETECTOR_DISTANCE="])

        oscillation_label = QLabel("   9. Rotation step: OSCILLATION_RANGE=", self)
        row10_layout.addWidget(oscillation_label)

        self.input_fields["OSCILLATION_RANGE="] = QLineEdit(self)
        self.input_fields["OSCILLATION_RANGE="].setFixedWidth(100)
        self.input_fields["OSCILLATION_RANGE="].setToolTip(
            "Angle between frames,\ncan be corrected later by image header."
        )
        row10_layout.addWidget(self.input_fields["OSCILLATION_RANGE="])
        row10_layout.addStretch()

        # ------------- Row 12 (Save Parameters Button) -------------
        row12_layout = QHBoxLayout()
        main_layout.addLayout(row12_layout)

        save_input_button = QPushButton("Save Parameters", self)
        save_input_button.setToolTip(
            'All parameters will be saved in "Input_parameters.txt".'
        )
        save_input_button.clicked.connect(self.save_and_run)
        row12_layout.addWidget(save_input_button)
        row12_layout.addStretch()

        # Add a stretch at the end if you want to push everything up
        main_layout.addStretch()

    def select_path(self) -> None:
        """
        Open a directory browser for selecting the working directory and update the path_entry widget.
        """
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_entry.setText(path)

    def load_path(self) -> None:
        """
        Load and analyse the chosen path, updates parameters and dataset counts.
        Displays a message box on success or if paths contain spaces.
        """
        input_path = self.path_entry.text()
        if input_path:
            if not os.path.exists(input_path):
                QMessageBox.critical(
                    self.window(),
                    "Error",
                    "The Path does not exist. Please check the path."
                )
                return
            if " " in input_path:
                QMessageBox.information(
                    self.window(),
                    "Info",
                    "Path contains space inside. Some functionality may not work."
                )
            if ("!" in input_path or "/." in input_path) and path_filter:
                QMessageBox.information(
                    self.window(),
                    "Info",
                    "The Path contains '!' or hidden dirs. Some functionality may not work."
                )
            parameter_dict, datasets_number = xds_analysis.analysis_folder(input_path)
            self.update_parameter(parameter_dict)

            parent_window = self.window()
            if hasattr(parent_window, 'dataset_counts'):
                parent_window.dataset_counts = datasets_number
            if hasattr(parent_window, 'set_input_path'):
                parent_window.set_input_path(input_path)

            print(f"The Path is set to {input_path}\n")
            QMessageBox.information(self.window(), "Info", f"The Path is set to {input_path}")

    @classmethod
    def load_instrument_profile(cls) -> dict:
        """
        Load available instrument profiles from a predefined directory.
        Returns:
            dict: A dictionary mapping profile names to their file paths.
        """
        _path_dict = {}
        _file_path = os.path.join(script_dir, "instrument_profile")
        if not os.path.isdir(_file_path):
            return {}
        _files_list = sorted([
            f for f in os.listdir(_file_path) if os.path.isfile(os.path.join(_file_path, f))
        ])
        for f in _files_list:
            if f != "__init__.py":
                _path_dict[f] = os.path.join(_file_path, f)
        return _path_dict

    def handle_option_select(self):
        """
        Handle the selection of instrument profile option.
        If 'Browse...' is chosen, prompt the user to select a custom profile file.
        """
        selected_text = self.instrument_combo.currentText()
        if selected_text == 'Browse...':
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select XDS.INP as model",
                "",
                "XDS INP (*.INP);;All Files (*)"
            )
            if file_path:
                file_name = os.path.basename(file_path)
                self.path_dict[file_name] = file_path
                index_custom = self.instrument_combo.findText("Custom")
                self.instrument_combo.setCurrentIndex(index_custom)
                self.instrument_combo.setCurrentText(file_name)
        else:
            # user picked an existing or default profile
            pass

    def load_instrument_parameter(self) -> None:
        """
        Load parameters from the selected instrument file into the GUI fields.
        """
        selected_option = self.instrument_combo.currentText()
        if selected_option in ["Custom", "Browse..."]:
            return
        print(f"Reading Instrument Parameter: {selected_option}\n")
        file_path = self.path_dict.get(selected_option)
        if not file_path:
            QMessageBox.warning(self.window(), "Warning", "No file path found for that option.")
            return

        if (selected_option.endswith(".INP") or selected_option.endswith(".txt") or
                selected_option.startswith("BACKUP")):
            try:
                with open(file_path, "r", errors="ignore") as file:
                    lines = file.readlines()
                    param_dict = xds_input.extract_keywords(lines)
                    self.update_parameter(param_dict)
            except FileNotFoundError:
                QMessageBox.critical(self.window(), "Error", "The instrument file does not exist.")
        else:
            # Possibly a JSON file or another format.
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    parameters = json.load(file)
                    # We'll do the same approach as the original.
                    replace_entry(self.input_fields["NX="], parameters.get("NX", ""))
                    replace_entry(self.input_fields["NY="], parameters.get("NY", ""))
                    replace_entry(self.input_fields["QX="], parameters.get("QX", ""))
                    replace_entry(self.input_fields["QY="], parameters.get("QY", ""))
                    replace_entry(self.input_fields["OVERLOAD="], parameters.get("overload", ""))

                    rot = parameters.get("rotation_axis", 0.0)
                    replace_entry(self.input_fields["ROTATION_ANGLE"], str(rot))
                    # Let's just do a naive approach for ROTATION_AXIS=.
                    ra_val = "{:.4f} {:.4f} 0".format(
                        cos(radians(rot)), cos(radians(rot + 90))
                    )
                    replace_entry(self.input_fields["ROTATION_AXIS="], ra_val)

                    wave_edit = self.input_fields["X-RAY_WAVELENGTH="]
                    wave_edit.clear()
                    if "wavelength" in parameters:
                        wave_edit.setText(str(parameters["wavelength"]))
                    else:
                        energy = parameters.get("energy", 200)  # default
                        if energy == 200:
                            wave_edit.setText("0.02508")
                        elif energy == 300:
                            wave_edit.setText("0.01968")

                    replace_entry(self.input_fields['ORGX='], str(int(parameters.get("NX", 0)) // 2))
                    replace_entry(self.input_fields['ORGY='], str(int(parameters.get("NY", 0)) // 2))

                    add_info = parameters.get("addition information", [])
                    replace_text(self.input_fields["Additional_Info"], "\n".join(add_info))

                    replace_entry(self.input_fields["INCLUDE_RESOLUTION_RANGE="], "30 0.8")
            except (FileNotFoundError, json.JSONDecodeError):
                QMessageBox.critical(self.window(), "Error", "Could not open or parse the instrument file.")

    def update_parameter(self, parameter_dict: dict) -> None:
        """
        Update GUI fields based on extracted parameters from a dictionary.
        """
        showing_parameters = [
            'NX=', 'NY=', 'QX=', 'QY=', 'OVERLOAD=', 'INCLUDE_RESOLUTION_RANGE=',
            'ORGX=', 'ORGY=', 'DETECTOR_DISTANCE=', 'OSCILLATION_RANGE=', 'ROTATION_AXIS=', 'X-RAY_WAVELENGTH='
        ]
        for key in showing_parameters:
            # Remove trailing '=' when checking param_dict, e.g. NX= => NX
            stripped_key = key[:-1]
            if stripped_key in parameter_dict and parameter_dict[stripped_key]:
                replace_entry(self.input_fields[key], parameter_dict[stripped_key][0])
            else:
                replace_entry(self.input_fields[key], " ")

        if 'ROTATION_AXIS' in parameter_dict and parameter_dict["ROTATION_AXIS"]:
            try:
                cos_rot_str = parameter_dict["ROTATION_AXIS"][0].split()[0]
                cos_rot = float(cos_rot_str)
                deg_val = arccos(cos_rot) * 57.296
                replace_entry(
                    self.input_fields["ROTATION_ANGLE"],
                    "{:.2f}".format(deg_val)
                )
            except Exception as e:
                print("Error calculating rotation angle:", e)

        additional_parameters = [
            "UNTRUSTED_RECTANGLE", "UNTRUSTED_ELLIPSE", "UNTRUSTED_QUADRILATERAL",
            "EXCLUDE_RESOLUTION_RANGE", "DELPHI", "SIGNAL_PIXEL"
        ]
        additional_lines = []
        for key in additional_parameters:
            if key in parameter_dict:
                val = parameter_dict[key]
                if isinstance(val, list):
                    for item in val:
                        additional_lines.append(f"{key}= {item}")
                else:
                    additional_lines.append(f"{key}= {val}")
        replace_text(self.input_fields["Additional_Info"], "\n".join(additional_lines))

    def save_and_run(self) -> None:
        """
        Save all input parameters into 'Input_parameters.txt' and set them as active parameters.
        Displays message boxes on success or warnings if values are missing.
        """
        input_values = {}

        # If a user has a rotation angle but no ROTATION_AXIS, compute a default.
        angle_str = self.input_fields["ROTATION_ANGLE"].text().strip()
        axis_str = self.input_fields["ROTATION_AXIS="].text().strip()
        if angle_str and not axis_str:
            try:
                rot_angle = float(angle_str)
                ra_val = "{:.4f} {:.4f} 0".format(
                    cos(radians(rot_angle)),
                    cos(radians(rot_angle + 90))
                )
                self.input_fields["ROTATION_AXIS="].setText(ra_val)
            except ValueError:
                pass

        for label, field in self.input_fields.items():
            if isinstance(field, QTextEdit):
                input_values[label] = field.toPlainText()
            elif isinstance(field, QLineEdit):
                input_values[label] = field.text()
            else:
                input_values[label] = ""  # fallback

        input_path = self.path_entry.text()
        if not input_path:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set. Please set the input path first.")
            return

        empty_list = []
        for entry, value in input_values.items():
            # if it's an XDS keyword (contains '=') and blank, let's consider it missing.
            if '=' in entry:
                if not value.strip():
                    empty_list.append(entry)

        if empty_list:
            QMessageBox.information(
                self.window(),
                "Caution",
                f"Input File Saved. However, {', '.join(empty_list)} is missing."
            )

        output_file_path = os.path.join(input_path, "Input_parameters.txt")

        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write("###Uniform Experiment Settings###\n")

            file.write(
                f"1. Pixel information for your camera:\n "
                f"NX= {input_values.get('NX=')}   NY= {input_values.get('NY=')}  "
                f"QX= {input_values.get('QX=')}  QY= {input_values.get('QY=')}  "
                f"!Number and Size (mm) of pixel\n\n"
            )
            file.write(
                f"2. Overload range for your camera:\n "
                f"OVERLOAD= {input_values.get('OVERLOAD=')}   "
                f"!default value dependent on the detector used\n\n"
            )
            file.write(
                f"3. Resolution range for the 1st round:\n "
                f"INCLUDE_RESOLUTION_RANGE=   {input_values.get('INCLUDE_RESOLUTION_RANGE=')}\n\n"
            )
            file.write(
                f"4. Direct beam position\n "
                f"ORGX= {input_values.get('ORGX=')}  ORGY=  {input_values.get('ORGY=')}\n\n"
            )
            file.write(
                f"5. Camera length\n "
                f"DETECTOR_DISTANCE=  {input_values.get('DETECTOR_DISTANCE=')}\n\n"
            )
            file.write(
                f"6. Oscillation range, degree per frame:\n "
                f"OSCILLATION_RANGE={input_values.get('OSCILLATION_RANGE=')}\n\n"
            )
            file.write(
                f"7. Rotation axis, depending on microscope:\n "
                f"ROTATION_AXIS= {input_values.get('ROTATION_AXIS=')}  "
                f"!cos(rotation_axis) cos(axis-90)  !in XDS.INP\n\n"
            )
            file.write(
                f"8. Wavelength, Å (200 keV 0.02508, 300 keV 0.01968):\n "
                f"X-RAY_WAVELENGTH=  {input_values.get('X-RAY_WAVELENGTH=')}     "
                f"!used by IDXREF\n\n"
            )

            beamstop_info = input_values.get("Additional_Info", "").strip()
            if beamstop_info:
                file.write("###Additional Keywords###\n")
                file.write(beamstop_info + "\n")
                file.write("###Additional Keywords###\n")

        # If we have a parent main window with set_input_path, call it.
        parent_window = self.window()
        if hasattr(parent_window, 'set_input_path'):
            parent_window.set_input_path(input_path)

        QMessageBox.information(
            self.window(),
            "Info",
            f"Parameters written to {output_file_path}\n"
        )


class ProcessWidget(QWidget):
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.xdsrunner_animation = None
        self._excel_container = None
        self.thread = {}
        self.input_path = ""
        self.P1 = False

    def _bus_to_shelx(self, items) -> None:
        """Prompt user and (placeholder) export SHELX files."""
        num = len(items)
        reply = QMessageBox.question(
            self,
            "Bus to SHELX",
            f"Are you sure you’d like to generate SHELX HKL and INS files for {num} dataset{'s' if num != 1 else ''}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._do_shelx(items)
            QMessageBox.information(
                self,
                "Bus to SHELX",
                f"SHELX files have been generated for {num} dataset{'s' if num != 1 else ''}.",
            )

    def _edit_sg_unit_cell(self, items) -> None:
        """Open the dialogue to edit SG & Unit Cell and confirm changes."""
        dlg = xds_input.SgUnitCellDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return  # User cancelled or validation failed
        sg = str(dlg.space_group_num)
        sg_name = dlg.sg_name
        cell = dlg.cell_edit.text().strip()
        num = len(items)
        msg = (
            f"You’re about to update the spacegroup and unit cell for {num} dataset{'s' if num != 1 else ''}.\n"
            f"The new lattice will be '{cell}' under '{sg_name}'. Does that look correct?"
        )
        reply = QMessageBox.question(
            self,
            "Confirm changes",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            xds_list = [os.path.join(item, "XDS.INP") for item in items]
            xds_input.cell_correct_batch(xds_list, cell, sg)
            QMessageBox.information(
                self,
                "Edit SG and Unit Cell",
                f"All set! Updated spacegroup and unit cell for {num} dataset{'s' if num != 1 else ''}.",
            )
            reply_run_xds = QMessageBox.question(
                self,
                "Run XDS",
                "Do you want to run XDS with the new spacegroup and unit cell?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply_run_xds == QMessageBox.StandardButton.Yes:
                self._run_xds_with_paths(xds_list)
            else:
                return

    def _move_to_folder(self, items) -> None:
        # Build list of XDS.INP files we want to move
        move_list = [os.path.join(item, "XDS.INP") for item in items]
        xds_list = find_files(self.input_path, "XDS.INP")

        # ── Ask destination folder ──
        folder_name, ok = QInputDialog.getText(
            self,
            "Destination folder",
            "Enter destination folder name (letters, digits, _, -, .),\n"
            "single dot (\'.\') will move to the work folder:",
        )
        if not ok:  # Cancel
            return
        folder_name = folder_name.strip()
        VALID_DIRNAME = re.compile(
            r'^(?!\.{1,2}$)[A-Za-z0-9](?:[A-Za-z0-9._/\-]{0,127}[A-Za-z0-9])?$'
        )
        # ── Validate ──
        if folder_name != "." and not VALID_DIRNAME.fullmatch(folder_name):
            QMessageBox.critical(
                self.window(),
                "Invalid name",
                f"‘{folder_name}’ is not a valid Linux folder name.\n"
                "Allowed: letters, digits, _, -, . (no spaces).",
            )
            return
        if folder_name == ".":
            # If the user entered a single dot, we will move to the input path
            dest_root = self.input_path
        else:
            dest_root = os.path.join(self.input_path, folder_name)
        if os.path.exists(dest_root):
            # folder already present – ask user whether to reuse it
            reuse = QMessageBox.question(
                self.window(),
                "Folder exists",
                f"The folder ‘{folder_name}’ already exists.\n"
                "Files moved there may overwrite existing content.\n\n"
                "Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reuse != QMessageBox.StandardButton.Yes:
                return

        # ── Plan the move ──
        fm = FileMover(paths=xds_list, work_folder=self.input_path)
        plan, errs = fm.plan(move_list, dest_root)
        if errs:
            QMessageBox.critical(
                self.window(), "Error",
                "Errors occurred while planning the move:\n" + "\n".join(errs),
            )
            return

        # ── Show wider confirmation dialog ──
        plan_preview = "\n".join(plan)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Move to Folder")
        msg_box.setText(
            f"Move {len(plan)} XDS.INP files to ‘{folder_name}’?\n"
            "They will overwrite files of the same name.\n\n"
            "Plan:\n" + plan_preview
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        msg_box.setStyleSheet("QLabel{min-width:800px;}")  # wider

        # ── Execute ──
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            moved, errs = fm.execute(move_list, dest_root)
            if errs:
                QMessageBox.critical(self.window(), "Error", "\n".join(errs))
            else:
                QMessageBox.information(
                    self.window(), "Success", "Files moved successfully."
                )

    @staticmethod
    def _open_folder(item) -> None:
        if is_wsl:
            subprocess.Popen(["explorer.exe", "."], cwd=item)
        else:
            open_folder_linux(item)

    def _run_xds_with_paths(self, paths, direct=False):
        """
        Run XDS with the provided paths.
        This is a helper function to run XDS on a list of paths.
        """
        if not paths:
            QMessageBox.warning(self.window(), "Warning", "No paths provided to run XDS.")
            return
        if direct:
            paths = [os.path.join(item, "XDS.INP") for item in paths]
            reply_run_xds = QMessageBox.question(
                self,
                "Run XDS",
                "Do you want to run XDS with the new spacegroup and unit cell?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply_run_xds == QMessageBox.StandardButton.No:
                return
        t = KillableThread(target=xds_runner.xdsrunner, args=(self.input_path, paths, False))
        self.thread["xds_runner"] = t
        t.start()
        self.xdsrunner_animation.startAnimation()
        QTimer.singleShot(100, self.check_xds_thread)

    def check_xds_thread(self):
        t = self.thread.get("xds_runner")
        if t and t.is_alive():
            QTimer.singleShot(100, self.check_xds_thread)
        else:
            self.xdsrunner_animation.stopAnimation()

    def stop_xdsrunner(self) -> None:
        if "xds_runner" in self.thread:
            t = self.thread["xds_runner"]
            if hasattr(t, 'terminate'):
                t.terminate()
            QMessageBox.information(self.window(), "Info", "XDSrunner is terminated as required.")
            self.xdsrunner_animation.stopAnimation()

    def _do_shelx(self, p):
        for path in p:
            try:
                xds_shelx.convert_to_shelx(path)
                html_report.create_html_file(path, "single")
            except Exception as e:
                self.errorOccurred.emit(f"Error occurred while converting to SHELX: {e}")

    def _open_html(self, _path):
        try:
            html_report.open_html_file(_path, "single")
        except Exception as e:
            err_msg = f"Error occurred while opening HTML file: {e}"
            self.errorOccurred.emit(err_msg)
            return

    def display_excel_data(self, file_path: str, display_columns: dict) -> None:
        """Load the Excel sheet and render it as a sortable, multi-select tree."""
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self.window(), "Error", f"Could not read the Excel file:\n{exc}")
            return

        # Keep the DataFrame accessible for potential future use
        self._df_current = df.copy()
        available_columns = [c for c in display_columns.keys() if c in df.columns]
        df_display = df[available_columns]

        tree = QTreeWidget()
        tree.setColumnCount(len(available_columns))
        tree.setHeaderLabels([display_columns[c] for c in available_columns])
        tree.setAlternatingRowColors(True)
        tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        tree.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tree.setSortingEnabled(True)

        # Fonts / style
        content_font = QFont("Liberation Sans", 13)
        header_font = QFont("Liberation Sans", 13)
        header_font.setBold(True)
        tree.setFont(content_font)
        for col in range(tree.columnCount()):
            tree.headerItem().setFont(col, header_font)
            tree.headerItem().setTextAlignment(col, Qt.AlignmentFlag.AlignCenter)
        tree.setStyleSheet("QTreeView::item { padding: 5px; }")

        # Rows: store row-index in UserRole for potential full-row retrieval
        for idx, row in df_display.iterrows():
            texts = [str(x) for x in row.tolist()]
            item = NaturalSortTreeWidgetItem(texts)
            item.setData(0, Qt.ItemDataRole.UserRole, idx)
            for col in range(len(texts)):
                item.setTextAlignment(col, Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(0, QSize(0, 30))
            tree.addTopLevelItem(item)

        auto_adjust_columns(tree, df_display)
        tree.sortItems(0, Qt.SortOrder.AscendingOrder)

        # Context menu
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self._on_tree_context_menu)

        # Replace previous container
        if self._excel_container is not None:
            self.layout().removeWidget(self._excel_container)
            self._excel_container.deleteLater()
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(tree)
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._excel_container = container
        self._tree = tree
        self.layout().addWidget(container)

    def _on_tree_context_menu(self, pos: QPoint):
        pass


class XDSRunner(ProcessWidget):
    """
    PyQt5 version of the XDSRunner class.
    Manages batch processing of XDS from the GUI.

    Methods:
        - set_ui
        - on_select
        - run_mrc_to_img
        - run_nxs_to_img
        - run_tiff_to_img
        - run_xds_writer
        - self_beam_center
        - self_beam_stop
        - run_xdsrunner
        - stop_xdsrunner
        - show_results
        - update_excel
        - open_xdsrunner_excel
        - display_excel_data
        - instamatic_inp_update
        - conversion_animation
        - stop_mrc_to_img_animation
        - xdsrunner_animate
        - stop_xdsrunner_animation
        - correct_input
        - on_beam_stop_checkbox_change
        - estimate_symmetry
    """
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Our main data
        self.selected_format_option = None
        self.input_path = ""
        self.thread = {}  # keep references to worker threads
        self.P1 = True
        self.errorOccurred.connect(self.showError)

        # Keep a reference to the container for Excel results
        self._excel_container = None
        # We'll also keep a reference to a QSpacerItem we dynamically add/remove
        self._excel_stretch_item = None

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(16)  # Use a bit more spacing between rows
        main_layout.addSpacing(12)

        # ================ Row 1: Description text ================
        description_label = QLabel("XDSrunner aims to perform batch data processing with XDS.", self)
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        # ================ Row 2: Format transfer label ================
        format_label = QLabel("1. Select Format and Convert to SMV")
        main_layout.addWidget(format_label)

        # ================ Row 3: Format transfer frame ================
        # Create a single row layout to hold both the radio buttons and the conversion widget.
        row_layout = QHBoxLayout()
        row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row_layout)
        row_layout.addSpacing(20)
        row_layout.setSpacing(20)

        # ----------------- Left: Radio Buttons -----------------
        self.format_options = ["SMV", "MRC", "TIFF", "NXS"]
        self.format_group = QButtonGroup(self)
        self.format_group.idClicked.connect(self.on_select)

        # Create a layout for the radio buttons.
        radio_layout = QHBoxLayout()
        for idx, fmt in enumerate(self.format_options, start=1):
            rb = QRadioButton(fmt)
            self.format_group.addButton(rb, idx)
            if idx == 1:
                rb.setChecked(True)
            radio_layout.addWidget(rb)
        row_layout.addLayout(radio_layout)

        # ----------------- Right: Conversion Button Container -----------------
        # This container will hold the conversion button(s) and the Beam Stop checkbox.
        self.conversion_container = QWidget()
        self.conversion_layout = QHBoxLayout()
        self.conversion_layout.setContentsMargins(0, 0, 0, 0)
        self.conversion_container.setLayout(self.conversion_layout)
        row_layout.addWidget(self.conversion_container)

        # Create the conversion buttons (and beam stop checkbox) for different formats.
        self.instamatic_button = QPushButton("Update Instamatic XDS.INP")
        self.instamatic_button.setToolTip("Add/remove keywords on XDS.INP from Instamatic.")
        self.instamatic_button.clicked.connect(self.instamatic_inp_update)

        self.mrc_button = QPushButton("MRC to IMG")
        self.mrc_button.setToolTip("Convert FEI non-stack MRC to SMV .IMG")
        self.mrc_button.clicked.connect(self.run_mrc_to_img)

        self.tiff_button = QPushButton("TIFF to IMG")
        self.tiff_button.setToolTip("Convert TIFF to SMV .IMG. Metadata might be needed.")
        self.tiff_button.clicked.connect(self.run_tiff_to_img)

        self.nxs_button = QPushButton("NXS to IMG")
        self.nxs_button.setToolTip("Convert DLS NXS H5 to SMV .IMG")
        self.nxs_button.clicked.connect(self.run_nxs_to_img)

        self.conversion_animation = AnimationWidget(word="Converting...")

        self.is_beam_stop = QCheckBox("Beam Stop Used")
        self.is_beam_stop.setChecked(False)
        self.is_beam_stop.stateChanged.connect(self.on_beam_stop_checkbox_change)

        # Initialize with the SMV conversion widgets (i.e. radio button 1 selected).
        self.conversion_layout.addWidget(self.instamatic_button)
        self.conversion_layout.addSpacing(20)
        self.conversion_layout.addWidget(self.is_beam_stop)

        # ================ Row 4: XDSINP batch writing label ================
        xdsinp_label = QLabel("2. Create and Update XDS.INP")
        main_layout.addWidget(xdsinp_label)

        # ================ Row 5: XDSINP batch writing buttons ================
        row5_layout = QHBoxLayout()
        row5_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row5_layout)
        row5_layout.setSpacing(30)
        row5_layout.addSpacing(20)

        generate_xds_button = QPushButton("Generate XDS.INP")
        generate_xds_button.setToolTip("Generate XDS.INP for converted images.")
        generate_xds_button.clicked.connect(self.run_xds_writer)
        row5_layout.addWidget(generate_xds_button)

        self.beam_centre_button = QPushButton("Find Beam Center")
        self.beam_centre_button.clicked.connect(self.self_beam_center)
        row5_layout.addWidget(self.beam_centre_button)

        self.beam_stop_button = QPushButton("Find Beam Stop")
        self.beam_stop_button.clicked.connect(self.self_beam_stop)
        row5_layout.addWidget(self.beam_stop_button)
        self.beam_stop_button.setVisible(False)

        correct_metadata_button = QPushButton("Correct Input with Metadata")
        correct_metadata_button.setToolTip("Correct input with image header (distance, angle, pixel).")
        correct_metadata_button.clicked.connect(self.correct_input)
        row5_layout.addWidget(correct_metadata_button)

        # ================ Row 6: Run XDS in all folders label ================
        run_xds_label = QLabel("3. Process Data under P1 mode and Estimate Symmetry.")
        main_layout.addWidget(run_xds_label)

        # ================ Row 7: Run XDS in all folders buttons ================
        row7_layout = QHBoxLayout()
        row7_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row7_layout)
        row7_layout.addSpacing(20)
        row7_layout.setSpacing(30)

        run_xds_button = QPushButton("Run XDS")
        run_xds_button.setToolTip("Run XDS batchly under work directory.")
        run_xds_button.clicked.connect(self.run_xdsrunner)
        row7_layout.addWidget(run_xds_button)

        stop_run_xds_button = QPushButton("Stop Run")
        stop_run_xds_button.setToolTip("Stop the processing after current XDS run.")
        stop_run_xds_button.clicked.connect(self.stop_xdsrunner)
        row7_layout.addWidget(stop_run_xds_button)

        self.xdsrunner_animation = AnimationWidget()
        row7_layout.addWidget(self.xdsrunner_animation)

        estimate_symmetry_button = QPushButton("Est. Symm. && Cell-Cluster")
        estimate_symmetry_button.setToolTip("Estimate symmetry and do the unit cell clustering.")
        estimate_symmetry_button.clicked.connect(self.estimate_symmetry)
        row7_layout.addWidget(estimate_symmetry_button)

        # ================ Row 8: Show all information label ================
        show_result_label = QLabel("4. View Running Result")
        main_layout.addWidget(show_result_label)

        # ================ Row 9: Show all info buttons ================
        row9_layout = QHBoxLayout()
        row9_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row9_layout)
        row9_layout.addSpacing(20)
        row9_layout.setSpacing(30)

        show_result_button = QPushButton("Show Results")
        show_result_button.setToolTip("Display running result below. The result is stored in xdsrunner.xlsx")
        show_result_button.clicked.connect(self.show_results)
        row9_layout.addWidget(show_result_button)

        update_result_button = QPushButton("Update Results File")
        update_result_button.setToolTip("Update result file with latest results.")
        update_result_button.clicked.connect(self.update_excel)
        row9_layout.addWidget(update_result_button)

        open_result_button = QPushButton("Open Results File")
        open_result_button.setToolTip("Open the result file with Excel or Libreoffice.")
        open_result_button.clicked.connect(self.open_xdsrunner_excel)
        row9_layout.addWidget(open_result_button)

        label_xdsrunner_xlsx = QLabel(">>> xdsrunner.xlsx")
        row9_layout.addWidget(label_xdsrunner_xlsx)

        self._excel_stretch_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self._excel_stretch_item)
        self.beam_stop_button.setToolTip("Find the origin point of the beam w/ beam stop.")
        self.beam_centre_button.setToolTip("Find the origin point of the beam w/o beam stop.")

    def on_select(self, button_id: int) -> None:
        """
        Handle format selection changes for image conversion and update the conversion widget area.
        """
        self.selected_format_option = button_id
        # Clear the conversion layout.
        while self.conversion_layout.count() > 0:
            item = self.conversion_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        # Add the appropriate conversion button (and the beam stop checkbox) based on selection.
        if button_id == 1:  # SMV
            self.conversion_layout.addWidget(self.instamatic_button)
        elif button_id == 2:  # MRC
            self.conversion_layout.addWidget(self.mrc_button)
            self.conversion_layout.addWidget(self.conversion_animation)
        elif button_id == 3:  # TIFF
            self.conversion_layout.addWidget(self.tiff_button)
            self.conversion_layout.addWidget(self.conversion_animation)
        elif button_id == 4:  # NXS
            self.conversion_layout.addWidget(self.nxs_button)
            self.conversion_layout.addWidget(self.conversion_animation)

        self.conversion_layout.addSpacing(20)
        # Add the beam stop checkbox for all formats.
        self.conversion_layout.addWidget(self.is_beam_stop)

    def run_mrc_to_img(self) -> None:
        """
        Start MRC-to-IMG conversion in a separate thread.
        """
        if self.input_path:
            print(f"Convert MRC Image in {self.input_path} to SMV format.\n")
            self.mrc_to_img_animation_active = True
            t = threading.Thread(target=image_io.convert_mrc2img, args=(self.input_path, path_filter))
            self.thread["conversion"] = t
            t.start()
            QTimer.singleShot(100, self.check_conversion_thread)
        else:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set. Please set the input path first.")

    def run_nxs_to_img(self) -> None:
        if self.input_path:
            print(f"Convert NXS Image in {self.input_path} to SMV format.\n")
            self.mrc_to_img_animation_active = True
            t = threading.Thread(target=image_io.convert_nxs2img, args=(self.input_path, path_filter))
            self.thread["conversion"] = t
            t.start()
            QTimer.singleShot(100, self.check_conversion_thread)
        else:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set. Please set the input path first.")

    def run_tiff_to_img(self) -> None:
        if self.input_path:
            print(f"Convert TIFF Image in {self.input_path} to SMV format.\n")
            feedback, wl, px_size = image_io.grab_info_tiff2img(self.input_path, path_filter)
            if not feedback:
                print("Conversion Terminated.\n")
                return
            self.mrc_to_img_animation_active = True
            t = threading.Thread(target=image_io.convert_tiff2img, args=(feedback, wl, px_size))
            self.thread["conversion"] = t
            t.start()
            QTimer.singleShot(100, self.check_conversion_thread)
        else:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set. Please set the input path first.")

    def check_conversion_thread(self):
        t = self.thread.get("conversion")
        if t and t.is_alive():
            QTimer.singleShot(100, self.check_conversion_thread)
        else:
            self.conversion_animation.stopAnimation()

    def run_xds_writer(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        t = threading.Thread(target=xds_input.write_xds_file, args=(self.input_path, None, path_filter))
        self.thread["xds_writer"] = t
        t.start()

    def self_beam_center(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        t = threading.Thread(target=image_io.centre_calculate, args=(self.input_path,))
        self.thread["beam_center"] = t
        t.start()

    def self_beam_stop(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        reply = QMessageBox.question(
            self.window(),
            "Warning",
            "Are you sure you HAVE used Beam Stop?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            t = threading.Thread(target=image_io.beam_stop_calculate, args=(self.input_path,))
            self.thread["beam_center"] = t
            t.start()

    def run_xdsrunner(self) -> None:
        if not self.input_path:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set. Please set the input path first.")
            return
        xds_list = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
        t = KillableThread(target=xds_runner.xdsrunner, args=(self.input_path, xds_list, False))
        self.thread["xds_runner"] = t
        t.start()
        self.xdsrunner_animation.startAnimation()
        QTimer.singleShot(100, self.check_xds_thread)

    def show_results(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        xdsrunner_excel_path = os.path.join(self.input_path, "xdsrunner.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            # Before displaying, remove any existing container
            if self._excel_container is not None:
                self.layout().removeWidget(self._excel_container)
                self._excel_container.deleteLater()
                self._excel_container = None

            # Also remove the old stretch if it exists
            if self._excel_stretch_item is not None:
                self.layout().removeItem(self._excel_stretch_item)
                self._excel_stretch_item = None

            self.display_excel_data(xdsrunner_excel_path, display_columns={
                "No.": "No.",
                "Path": "Path",
                "Integration Cell": "P1 Cell",
                "SG": "SG",
                "Unit cell": "Unit Cell",
                "Vol.": "Vol.",
                "Index%": "Index%",
                "ISa": "ISa",
                "CC1/2": "CC1/2",
                "Completeness": "Complete.",
                "Reso.": "Reso.",
            })
        else:
            QMessageBox.information(self.window(), "Error", "Cannot find xdsrunner.xlsx. Check or update it.")

    def update_excel(self):
        input_path = getattr(self, "input_path", None)
        if not input_path:
            # This warning is in the main thread, so it should display immediately.
            QMessageBox.warning(self, "Warning", "Input path is not set.")
            return

        def run_extraction():
            try:
                xds_runner.excel_extract(input_path, False)
            except PermissionError:
                self.errorOccurred.emit("Permission Error: Cannot write to xdsrunner.xlsx,"
                                        "It may be open in another application (e.g., Excel). "
                                        "Please close the Excel file and try again.")
                return
            QTimer.singleShot(0, self.show_results)

        t = threading.Thread(target=run_extraction)
        self.thread["update_excel"] = t
        t.start()

    def showError(self, err_msg):
        # Debug print to verify the slot is called
        print("showError called with:", err_msg)
        # This will run in the main thread and should display a QMessageBox.
        QMessageBox.critical(self, "Error", err_msg)

    def open_xdsrunner_excel(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        xdsrunner_excel_path = os.path.join(self.input_path, "xdsrunner.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            try:
                if is_wsl:
                    subprocess.call([
                        "wsl.exe", "cmd.exe", "/C",
                        f"start explorer.exe {linux_to_windows_path(xdsrunner_excel_path)}"
                    ])
                    return

                # Try to open with LibreOffice
                libreoffice_path = subprocess.run(["which", "libreoffice"], capture_output=True,
                                                  text=True).stdout.strip()
                if libreoffice_path:
                    subprocess.call(["libreoffice", "--calc", xdsrunner_excel_path])
                    return
                else:
                    QMessageBox.warning(self.window(), "Caution", "LibreOffice not found.")
            except Exception as e:
                QMessageBox.critical(self.window(), "Caution", f"Error opening the file due to {e}.")
        else:
            QMessageBox.critical(self.window(), "Error", "Cannot find xdsrunner.xlsx at the specified input path.")

    # ------------------------------------------------------------------
    # Context-menu dispatch
    # ------------------------------------------------------------------

    # noinspection PyUnboundLocalVariable
    def _on_tree_context_menu(self, pos: QPoint) -> None:
        if self._tree is None:
            return
        selected_items = self._tree.selectedItems()
        if not selected_items:
            return

        # Find which column index corresponds to "Path"
        path_col = None
        for col in range(self._tree.columnCount()):
            if self._tree.headerItem().text(col) == "Path":
                path_col = col
                break
        if path_col is None:
            # If "Path" isn't visible, do nothing
            return

        # Build a list of path strings
        path_list: list[str] = [
            os.path.join(self.input_path, item.text(path_col)[4:]) if item.text(path_col).startswith(
                "...") else item.text(path_col) for item in selected_items]

        for path in path_list:
            if not os.path.exists(path):
                QMessageBox.warning(self.window(), "Warning", f"Path does not exist: {path}. "
                                                              f"Please update the excel.")
                return

        menu_pos = self._tree.viewport().mapToGlobal(pos)
        menu = QMenu(self)
        single = (len(path_list) == 1)
        if single:
            act_open_folder = QAction("Open folder", self)
            act_open_html = QAction("Open HTML report", self)
            menu.addAction(act_open_folder)
            menu.addAction(act_open_html)
            menu.addSeparator()
        act_run = QAction("Run XDS", self)
        act_edit = QAction("Edit SG and Unit Cell", self)
        act_move = QAction("Move to folder", self)
        menu.addAction(act_run)
        menu.addAction(act_edit)
        menu.addAction(act_move)

        triggered = menu.exec(menu_pos)
        if single and triggered is act_open_folder:
            self._open_folder(path_list[0])
        elif single and triggered is act_open_html:
            self._open_html(path_list[0])
        elif triggered is act_run:
            self._run_xds_with_paths(path_list, direct=True)
        elif triggered is act_edit:
            self._edit_sg_unit_cell(path_list)
        elif triggered is act_move:
            self._move_to_folder(path_list)

    def instamatic_inp_update(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        reply = QMessageBox.question(
            self.window(),
            "For instamatic user",
            "Do you really want to update ALL xds.inp generated by instamatic to the newest version?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            t = threading.Thread(target=xds_input.instamatic_update, args=(self.input_path, path_filter))
            self.thread["instamatic_xds"] = t
            t.start()

    def correct_input(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        t = threading.Thread(target=xds_input.correct_inputs, args=(self.input_path,))
        self.thread["correct_input"] = t
        t.start()

    def on_beam_stop_checkbox_change(self) -> None:
        """
        Update the UI when beam stop usage is toggled,
        changing the beam centre button text and callback.
        """
        if self.is_beam_stop.isChecked():
            self.beam_centre_button.setVisible(False)
            self.beam_stop_button.setVisible(True)
        else:
            self.beam_centre_button.setVisible(True)
            self.beam_stop_button.setVisible(False)

    def estimate_symmetry(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        t = threading.Thread(
            target=xds_cluster.analysis_lattice_symmetry,
            args=(self.input_path, path_filter)
        )
        self.thread["estimate_symmetry"] = t
        t.start()


class UnitCellCorr(ProcessWidget):
    """
    Class UnitCellCorr (PyQt5 Version)

    Updates and apply unit cell parameters to all XDS.INP files.
    Methods:
        - save_cell_info(): Saves space group and cell params into 'Cell_information.txt'
        - run_xdsrunner2(): Runs XDS again with updated cell parameters
        - stop_xdsrunner2(): Stops the ongoing XDS batch run
        - show_results(): Shows updated results from xdsrunner2.xlsx
        - open_xdsrunner_excel(): Opens xdsrunner2.xlsx for inspection
        - update_excel(): Updates results based on the latest processed data
        - display_excel_data(file_path): Displays content of an Excel file in a QTreeWidget
        - xdsrunner_animate(): Animates the runner process
        - stop_xdsrunner_animation(): Stops the runner animation
    """
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialize the UnitCellCorr page with PyQt5 widgets and layout.

        Args:
            parent (QWidget): The parent widget or window
        """
        super().__init__(parent)
        self.errorOccurred.connect(self.showError)
        self.thread = {}
        self.input_path = ""  # Typically set from the parent window
        self.P1 = False

        # Animation states
        self.xdsrunner_animation_active = False

        # GUI elements
        self.space_group_entry = None
        self.unit_cell_entry = None
        self.xdsrunner_label = None
        self._excel_container = None

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(16)
        main_layout.addSpacing(12)

        # Row 1: Instruction message
        instruction_msg = "Input Space group and unit cell parameters."
        label_instruction = QLabel(instruction_msg, self)
        label_instruction.setWordWrap(True)
        main_layout.addWidget(label_instruction)

        # Row 2: Additional info
        additional_info = (
            "Providing unit cell and space group keywords for all datasets is suggested "
            "for later data merging. \nFetch results from xdsrunner.xlsx / estimate_symmetry. "
            "XDS will refine unit cells individually."
        )
        label_additional = QLabel(additional_info, self)
        font_info = label_additional.font()
        font_info.setPointSize(13)
        font_info.setItalic(True)
        label_additional.setFont(font_info)
        label_additional.setWordWrap(True)
        main_layout.addWidget(label_additional)

        # Row 4: Cell info entry
        row4_layout = QHBoxLayout()
        row4_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(row4_layout)

        label_sg = QLabel("Space group:", self)
        row4_layout.addWidget(label_sg)

        self.space_group_entry = QLineEdit(self)
        self.space_group_entry.setFixedWidth(80)
        self.space_group_entry.setToolTip("Space group name(C2/c), number (1-230)")
        row4_layout.addWidget(self.space_group_entry)

        label_cell = QLabel("Unit cell:", self)
        row4_layout.addWidget(label_cell)

        self.unit_cell_entry = QLineEdit(self)
        self.unit_cell_entry.setFixedWidth(400)
        self.unit_cell_entry.setToolTip(
            "Unit cell parameters, separate by space or comma + space (a b c alpha beta gamma)."
        )
        row4_layout.addWidget(self.unit_cell_entry)
        row4_layout.addStretch()

        # Row 5: Buttons to update cell
        row5_layout = QHBoxLayout()
        main_layout.addLayout(row5_layout)
        row5_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row5_layout.addSpacing(20)
        row5_layout.setSpacing(20)

        update_cell_button = QPushButton("Update Cell Parameters", self)
        update_cell_button.setToolTip(
            "Copy the sg and cell to all XDS.INP under work directory.\n"
            'Info is stored in "Cell_information.txt"'
        )
        update_cell_button.clicked.connect(self.save_cell_info)
        row5_layout.addWidget(update_cell_button)
        row5_layout.addStretch()

        # Row 6: "Run XDS again" label
        run_xds_again_msg = "* Run XDS with updated .inp files."
        label_run_again = QLabel(run_xds_again_msg, self)
        main_layout.addWidget(label_run_again)

        # Row 7: Buttons to run or stop XDS
        row7_layout = QHBoxLayout()
        main_layout.addLayout(row7_layout)
        row7_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row7_layout.addSpacing(20)
        row7_layout.setSpacing(30)

        run_xds_button = QPushButton("Run XDS with Cell", self)
        run_xds_button.setToolTip("Run XDS batch with the new cell.")
        run_xds_button.clicked.connect(self.run_xdsrunner2)
        row7_layout.addWidget(run_xds_button)

        self.xdsrunner_animation = AnimationWidget()
        row7_layout.addWidget(self.xdsrunner_animation)

        stop_xds_button = QPushButton("Stop Run", self)
        stop_xds_button.setToolTip("Stop the processing after the current XDS run.")
        stop_xds_button.clicked.connect(self.stop_xdsrunner)
        row7_layout.addWidget(stop_xds_button)

        # We'll animate with a label that updates text with a spinner
        self.xdsrunner_label = QLabel("", self)
        self.xdsrunner_label.setFixedWidth(120)
        row7_layout.addWidget(self.xdsrunner_label)
        row7_layout.addStretch()

        # Row 8: "Show running result" label
        label_show_result = QLabel("* Show running result", self)
        main_layout.addWidget(label_show_result)

        # Row 9: Show result / update / open
        row9_layout = QHBoxLayout()
        main_layout.addLayout(row9_layout)
        row9_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row9_layout.setSpacing(20)
        row9_layout.addSpacing(20)

        show_result_button = QPushButton("Show Results", self)
        show_result_button.setToolTip("Display running result from xdsrunner2.xlsx below.")
        show_result_button.clicked.connect(self.show_results)
        row9_layout.addWidget(show_result_button)

        update_result_button = QPushButton("Update Results File", self)
        update_result_button.setToolTip("Update the result file with the newest data.")
        update_result_button.clicked.connect(self.update_excel)
        row9_layout.addWidget(update_result_button)

        open_result_button = QPushButton("Open Result File", self)
        open_result_button.setToolTip("Open xdsrunner2.xlsx in Excel or LibreOffice.")
        open_result_button.clicked.connect(self.open_xdsrunner_excel)
        row9_layout.addWidget(open_result_button)

        label_xdsrunner2 = QLabel(">>> xdsrunner2.xlsx", self)
        row9_layout.addWidget(label_xdsrunner2)
        row9_layout.addStretch()

        # Allow the layout to expand
        self._excel_stretch_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self._excel_stretch_item)

    def save_cell_info(self):
        """
        Save space group and unit cell parameters into 'Cell_information.txt'
        and apply them to all XDS.INP files.
        """
        space_group = self.space_group_entry.text().strip()
        unit_cell = self.unit_cell_entry.text().strip()

        try:
            space_group_num = spgfinder.get_int_number(space_group)
        except Exception as e:
            QMessageBox.critical(self.window(), "Error", f"Invalid space group: {e}")
            return

        parent_window = self.window()  # or pass in a reference if needed
        input_path = getattr(parent_window, "input_path", None)
        if not input_path:
            QMessageBox.information(self.window(), "Info", "Please select an input path first.")
            return

        # Check the basic validity
        # We expect 6 parts for the unit cell
        cell_parts = unit_cell.replace(",", " ").split()
        if not space_group or not unit_cell or len(cell_parts) != 6:
            QMessageBox.information(self.window(), "Caution",
                                    "You need to fill both entries properly (sg + 6 cell params).")
            return

        # Write to file
        output_file_path = os.path.join(input_path, "Cell_information.txt")
        try:
            with open(output_file_path, "w") as f:
                f.write("#####Crystal Information#####\n\n")
                f.write(f"SPACE_GROUP_NUMBER= {space_group_num}\n\n")
                f.write(f"UNIT_CELL_CONSTANTS= {' '.join(cell_parts)}\n")
            QMessageBox.information(
                self.window(),
                "Info",
                f"Cell information saved to {output_file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.window(),
                "Error",
                f"Could not write to {output_file_path}\nError: {e}"
            )
            return

        # Start a thread to apply the new cell to XDS.INP
        t = threading.Thread(
            target=xds_input.cell_correct_folder,
            args=(input_path, path_filter)
        )
        self.thread["cell_correct"] = t
        t.start()

    def run_xdsrunner2(self):
        """
        Run XDS again with updated cell parameters. Animate while running.
        """
        parent_window = self.window()
        input_path = getattr(parent_window, "input_path", None)
        if not input_path:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set.")
            return
        xds_list = find_files(input_path, "XDS.INP", path_filter=path_filter)
        t = KillableThread(target=xds_runner.xdsrunner, args=(input_path, xds_list, True))
        self.thread["xds_runner"] = t
        t.start()
        self.xdsrunner_animation.startAnimation()
        QTimer.singleShot(100, self.check_xds_thread)

    def show_results(self):
        """
        Show updated results from xdsrunner2.xlsx in a QTreeWidget.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        xdsrunner_excel_path = os.path.join(self.input_path, "xdsrunner2.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            # Before displaying, remove any existing container
            if self._excel_container is not None:
                self.layout().removeWidget(self._excel_container)
                self._excel_container.deleteLater()
                self._excel_container = None

            # Also remove the old stretch if it exists
            if self._excel_stretch_item is not None:
                self.layout().removeItem(self._excel_stretch_item)
                self._excel_stretch_item = None

            self.display_excel_data(xdsrunner_excel_path, display_columns={
                "No.": "No.",
                "Path": "Path",
                "SG": "SG",
                "Unit cell": "Unit Cell",
                "Vol.": "Vol.",
                "Index%": "Index%",
                "ISa": "ISa",
                "Rmeas": "Rmeas",
                "CC1/2": "CC1/2",
                "Completeness": "Complete.",
                "Reso.": "Reso.",
            })
        else:
            QMessageBox.information(self.window(), "Error", "Cannot find xdsrunner2.xlsx. Check or update it.")

    def open_xdsrunner_excel(self):
        """
        Open xdsrunner2.xlsx in LibreOffice or Windows Explorer for inspection.
        """
        parent_window = self.window()
        input_path = getattr(parent_window, "input_path", None)
        if not input_path:
            QMessageBox.warning(self.window(), "Warning", "Input path is not set.")
            return

        xdsrunner_excel_path = os.path.join(input_path, "xdsrunner2.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            try:
                if is_wsl:
                    subprocess.call([
                        "wsl.exe", "cmd.exe", "/C",
                        f"start explorer.exe {linux_to_windows_path(xdsrunner_excel_path)}"
                    ])
                    return

                # Try LibreOffice
                libreoffice_path = subprocess.run(["which", "libreoffice"], capture_output=True,
                                                  text=True).stdout.strip()
                if libreoffice_path:
                    subprocess.call(["libreoffice", "--calc", xdsrunner_excel_path])
                    return
                else:
                    QMessageBox.warning(self.window(), "Caution",
                                        "No LibreOffice found. Explorer might not be available.")
            except Exception as e:
                QMessageBox.critical(self.window(), "Caution", f"Error opening the file: {e}")
        else:
            QMessageBox.critical(self.window(), "Caution",
                                 "Cannot find xdsrunner2.xlsx at the specified input path.")

    def update_excel(self):
        input_path = getattr(self, "input_path", None)
        if not input_path:
            # This warning is in the main thread, so it should display immediately.
            QMessageBox.warning(self, "Warning", "Input path is not set.")
            return

        def run_extraction():
            try:
                xds_runner.excel_extract(input_path, True)
            except PermissionError:
                self.errorOccurred.emit("Permission Error: Cannot write to xdsrunner2.xlsx,"
                                        "It may be open in another application (e.g., Excel). "
                                        "Please close the Excel file and try again.")
                return
            QTimer.singleShot(0, self.show_results)

        t = threading.Thread(target=run_extraction)
        self.thread["update_excel"] = t
        t.start()

    def showError(self, err_msg):
        # Debug print to verify the slot is called
        print("showError called with:", err_msg)
        # This will run in the main thread and should display a QMessageBox.
        QMessageBox.critical(self, "Error", err_msg)

    # ------------------------------------------------------------------
    # Context-menu dispatch
    # ------------------------------------------------------------------

    # noinspection PyUnboundLocalVariable
    def _on_tree_context_menu(self, pos: QPoint) -> None:  # noqa: N802
        if self._tree is None:
            return
        selected_items = self._tree.selectedItems()
        if not selected_items:
            return

        # Find which column index corresponds to "Path"
        path_col = None
        for col in range(self._tree.columnCount()):
            if self._tree.headerItem().text(col) == "Path":
                path_col = col
                break
        if path_col is None:
            # If "Path" isn't visible, do nothing
            return

        # Build a list of path strings
        path_list: list[str] = [
            os.path.join(self.input_path, item.text(path_col)[4:]) if item.text(path_col).startswith(
                "...") else item.text(path_col) for item in selected_items]

        for path in path_list:
            if not os.path.exists(path):
                QMessageBox.warning(self.window(), "Warning", f"Path does not exist: {path}. "
                                                              f"Please update the excel.")
                return

        menu_pos = self._tree.viewport().mapToGlobal(pos)
        menu = QMenu(self)
        if len(path_list) == 1:
            act_open_folder = QAction("Open folder", self)
            act_open_html = QAction("Open HTML report", self)
            menu.addAction(act_open_folder)
            menu.addAction(act_open_html)
            menu.addSeparator()
        act_run = QAction("Run XDS", self)
        act_edit = QAction("Edit SG and Unit Cell", self)
        act_shelx = QAction("Bus to SHELX", self)
        act_move = QAction("Move to folder", self)
        menu.addAction(act_run)
        menu.addAction(act_edit)
        menu.addAction(act_shelx)
        menu.addAction(act_move)

        triggered = menu.exec(menu_pos)
        if len(path_list) == 1 and triggered is act_open_folder:
            self._open_folder(path_list[0])
        elif len(path_list) == 1 and triggered is act_open_html:
            self._open_html(path_list[0])
        elif triggered is act_edit:
            self._edit_sg_unit_cell(path_list)
        elif triggered is act_run:
            self._run_xds_with_paths(path_list, direct=True)
        elif triggered is act_shelx:
            self._bus_to_shelx(path_list)
        elif triggered is act_move:
            self._move_to_folder(path_list)


class XDSRefine(ProcessWidget):
    """Class XDSRefine
    Refines XDS.INP files based on chosen subsets and criteria.

    Methods:
        __init__(parent): Initializes the refinement page and GUI elements.
        handle_range_option_select(event): Changes the UI depending on selected range mode
        (All, Selected, Ranged, Single).
        hide_all_widgets(): Hides all range selection widgets.
        show_selected_widgets(): Shows widgets for filtering data by a certain statistic.
        show_ranged_widgets(): Shows widgets for specifying a range of datasets by index.
        show_single_widgets(): Shows widgets for selecting a single dataset.
        show_failed_widgets(): Shows widgets for selecting failed datasets to retry.
        view_lattice(): Displays reciprocal lattice visualisation for a chosen dataset.
        run_xdsgui(): Launches XDSGUI on the selected dataset.
        open_html_report(): Opens the HTML report for the selected single dataset.
        run_xdsconv_shelx(): Converts data to SHELX format (.hkl and .p4p).
        handle_filter_option_select(event): Adjusts default threshold values when a filter option is selected.
        refresh_list(): Updates the single dataset list from xdsrunner2.xlsx.
        refresh_failed_list(): Updates the failed dataset list from results.
        get_xds_list(): Retrieves a list of XDS.INP files based on the selected criteria.
        run_xds(): Runs XDS refinements based on chosen criteria and parameters.
        open_keyword_manager(): Opens a Keyword Manager app for adding/deleting/calibrating keywords.
        stop_xds(): Stops the ongoing refinement process.
        show_results(): Displays updated results in a Treeview.
        open_xdsrunner_excel(): Opens xdsrunner2.xlsx in an external viewer.
        update_excel(): Updates the result file.
        display_excel_data(file_path): Displays Excel data in a Treeview widget.
        xdsrunner_animate(): Animates the XDS refinement process.
        stop_xdsrunner_animation(): Stops the refinement animation.
        open_folder(): Opens the folder of the selected dataset.
    """
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.thread = {}
        self.input_path = ""
        self.P1 = False
        self._excel_container = None
        self.errorOccurred.connect(self.showError)
        self.process = QProcess(self)

        # Read config booleans for the checkboxes
        outlier_scale_ratio = float(config["Inp_Refine"]["outlier_scale_ratio"])
        bool_update_index_ratio = strtobool(config["Inp_Refine"]["update_index_ratio"])
        bool_update_axis = strtobool(config["Inp_Refine"]["update_rotation_axis"])
        bool_outlier_remove = strtobool(config["Inp_Refine"]["remove_scale_outlier"])
        bool_divergence = strtobool(config["Inp_Refine"]["add_divergence"])
        bool_update_resolution = strtobool(config["Inp_Refine"]["update_resolution"])
        bool_correct_centre = strtobool(config["Inp_Refine"]["correct_centre"])

        # For rotating spinner
        self.xdsrunner_animation_active = False
        self.xdsrunner_animation_angle = 0

        self.relative_paths = {}
        self.failed_relative_paths = {}

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(16)
        main_layout.addSpacing(12)

        # Row 1 + 2: Instruction messages
        note_label1 = QLabel("Refine Input Parameters in XDS.INP. Get data reduction result from single dataset.")
        note_label2 = QLabel("Use AutoLEI to refine XDS.INP files in the target folder.")
        font_italic = note_label2.font()
        font_italic.setPointSize(13)
        font_italic.setItalic(True)
        note_label2.setFont(font_italic)

        main_layout.addWidget(note_label1)
        main_layout.addWidget(note_label2)

        # Create one horizontal layout for all range-related widgets
        range_options_layout = QHBoxLayout()
        range_label = QLabel("Refine on data as ")
        range_options_layout.addWidget(range_label)

        # Range selection widget (combo box)
        self.range_combo = ComboBox()
        self.range_options = ["All", "Selected", "Ranged", "Single", "Failed"]
        self.range_combo.addItems(self.range_options)
        self.range_combo.setCurrentIndex(0)
        self.range_combo.currentIndexChanged.connect(self.handle_range_option_select)
        range_options_layout.addWidget(self.range_combo)

        # For 'Selected' mode widgets
        self.select_label = QLabel("with ")
        range_options_layout.addWidget(self.select_label)

        self.filter_option_menu = ComboBox()
        self.filter_option_menu.addItems(["--", "Index%", "I/Sigma", "CC1/2", "Resolution"])
        self.filter_option_menu.currentIndexChanged.connect(self.handle_filter_option_select)
        range_options_layout.addWidget(self.filter_option_menu)

        self.sign_option_menu = ComboBox()
        self.sign_option_menu.addItems([">", "<"])
        self.sign_option_menu.setCurrentIndex(1)
        range_options_layout.addWidget(self.sign_option_menu)

        self.statistic_threshold = QLineEdit()
        self.statistic_threshold.setFixedWidth(100)
        range_options_layout.addWidget(self.statistic_threshold)

        # For 'Ranged' mode widgets
        self.range_input = QLineEdit()
        range_options_layout.addWidget(self.range_input)

        self.range_label_info = QLabel(">> Example: 1, 2-4")
        range_options_layout.addWidget(self.range_label_info)

        # For 'Single' mode widgets
        self.single_label = QLabel("on ")
        range_options_layout.addWidget(self.single_label)

        self.single_file_option_menu = ComboBox()
        self.single_file_option_menu.setMaxVisibleItems(10)
        self.single_file_option_menu.addItem("--")
        self.single_file_option_menu.setFixedWidth(500)
        self.single_file_options = []
        range_options_layout.addWidget(self.single_file_option_menu)

        # For 'Failed' mode widgets
        self.failed_label = QLabel("on ")
        range_options_layout.addWidget(self.failed_label)

        self.failed_file_option_menu = ComboBox()
        self.failed_file_option_menu.setMaxVisibleItems(10)
        self.failed_file_option_menu.addItem("--")
        self.failed_file_option_menu.setFixedWidth(500)
        self.failed_file_options = []
        range_options_layout.addWidget(self.failed_file_option_menu)

        # Always add a stretch at the end of the line
        range_options_layout.addStretch()

        # Finally, add the combined layout to your main layout
        main_layout.addLayout(range_options_layout)

        # Next row: refine checkboxes
        # We'll do them in a separate grid
        refine_grid1 = QHBoxLayout()
        main_layout.addLayout(refine_grid1)
        refine_grid1.setSpacing(30)
        refine_grid1.addSpacing(20)

        # update_axis
        self.update_axis = QCheckBox("Rotation Axis")
        self.update_axis.setChecked(bool_update_axis)
        refine_grid1.addWidget(self.update_axis)

        # add_divergence
        self.add_divergence = QCheckBox("Divergence && Mosaicity")
        self.add_divergence.setChecked(bool_divergence)
        refine_grid1.addWidget(self.add_divergence)

        # remove_scale_outlier
        self.remove_scale_outlier = QCheckBox("Remove Scale Outlier >")
        self.remove_scale_outlier.setChecked(bool_outlier_remove)
        refine_grid1.addWidget(self.remove_scale_outlier)

        self.scale_outlier_ratio = QLineEdit()
        self.scale_outlier_ratio.setFixedWidth(60)
        self.scale_outlier_ratio.setText(f"{outlier_scale_ratio:.1f}")
        refine_grid1.addWidget(self.scale_outlier_ratio)

        label_iqr = QLabel("IQR")
        refine_grid1.addWidget(label_iqr)

        # correct_centre
        self.correct_centre = QCheckBox("Beam Centre")
        self.correct_centre.setChecked(bool_correct_centre)
        refine_grid1.addWidget(self.correct_centre)
        refine_grid1.addStretch()

        # second row of refined checkboxes
        refine_grid2 = QHBoxLayout()
        main_layout.addLayout(refine_grid2)
        refine_grid2.setSpacing(20)
        refine_grid2.addSpacing(20)

        self.update_index_ratio = QCheckBox("Refine Index Ratio on datasets with index% <")
        self.update_index_ratio.setChecked(bool_update_index_ratio)
        refine_grid2.addWidget(self.update_index_ratio)

        self.index_ratio_threshold = QLineEdit()
        self.index_ratio_threshold.setFixedWidth(80)
        self.index_ratio_threshold.setText("85.0")
        refine_grid2.addWidget(self.index_ratio_threshold)

        label_percent = QLabel("%  ")
        refine_grid2.addWidget(label_percent)

        self.update_resolution = QCheckBox("Change Resolution to")
        self.update_resolution.setChecked(bool_update_resolution)
        refine_grid2.addWidget(self.update_resolution)

        self.resolution_range = QLineEdit()
        self.resolution_range.setFixedWidth(100)
        self.resolution_range.setText("30 0.8")
        refine_grid2.addWidget(self.resolution_range)
        refine_grid2.addStretch()

        # row: run xds
        row_run = QHBoxLayout()
        main_layout.addLayout(row_run)
        row_run.setSpacing(30)

        run_xds_button = QPushButton("Run XDS with Cell")
        run_xds_button.setToolTip("Refine the input parameter and Run XDS batchly under work directory.")
        run_xds_button.clicked.connect(self.run_xds)
        row_run.addWidget(run_xds_button)

        stop_xds_button = QPushButton("Stop Run")
        stop_xds_button.setToolTip("Stop the processing after current XDS run.")
        stop_xds_button.clicked.connect(self.stop_xdsrunner)
        row_run.addWidget(stop_xds_button)

        # We'll do a label for spinner animation
        self.xdsrunner_animation = AnimationWidget()
        row_run.addWidget(self.xdsrunner_animation)
        row_run.addWidget(QLabel("|"))

        self.change_parameter_button = QPushButton("Change Input Parameters")
        self.change_parameter_button.setToolTip("Change / Delete Keywords, Calibrate Camera Length by Ratio.")
        self.change_parameter_button.clicked.connect(self.open_keyword_manager)
        row_run.addWidget(self.change_parameter_button)
        row_run.addWidget(QLabel("|"))

        # Extra buttons
        self.xdsgui_button = QPushButton("Run XDSGUI")
        self.xdsgui_button.setToolTip("Open XDSGUI on current working data.")
        self.xdsgui_button.clicked.connect(self.run_xdsgui)
        row_run.addWidget(self.xdsgui_button)
        self.view_lattice_button = QPushButton("View Reciprocal Space")
        self.view_lattice_button.setToolTip("View the reciprocal space on current working data.")
        self.view_lattice_button.clicked.connect(self.view_lattice)
        row_run.addWidget(self.view_lattice_button)
        row_run.addStretch()
        main_layout.addSpacing(12)

        # row: show results
        row_show = QHBoxLayout()
        main_layout.addLayout(row_show)
        row_show.setSpacing(30)

        show_result_button = QPushButton("Show Results")
        show_result_button.setToolTip("Display running result below. The result is stored in xdsrunner2.xlsx")
        show_result_button.clicked.connect(self.show_results)
        row_show.addWidget(show_result_button)

        update_result_button = QPushButton("Update Results File")
        update_result_button.setToolTip("Update result file with latest results.")
        update_result_button.clicked.connect(self.update_excel)
        row_show.addWidget(update_result_button)

        self.excel_open_button = QPushButton("Open Results File")
        self.excel_open_button.setToolTip("Open the result file with Excel or Libreoffice.")
        self.excel_open_button.clicked.connect(self.open_xdsrunner_excel)
        row_show.addWidget(self.excel_open_button)

        row_show.addWidget(QLabel("|"))

        self.bus2shelx_button = QPushButton("Bus to SHELX")
        self.bus2shelx_button.setToolTip("Generate hkl, p4p and cif_od file on current working data.")
        self.bus2shelx_button.clicked.connect(self.run_xdsconv_shelx)
        row_show.addWidget(self.bus2shelx_button)

        self.html_button = QPushButton("Web Report")
        self.html_button.setToolTip("Open the web report on current working data.")
        self.html_button.clicked.connect(self.open_html_report)
        row_show.addWidget(self.html_button)

        self.folder_button = QPushButton("Open Folder")
        self.folder_button.setToolTip("Open the folder of current working data.")
        self.folder_button.clicked.connect(self.open_folder_gui)
        row_show.addWidget(self.folder_button)

        row_show.addStretch()

        # Add a stretch at the bottom
        self._excel_stretch_item = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addItem(self._excel_stretch_item)

        # Hide all extra widgets initially
        self.hide_all_widgets()

    def handle_range_option_select(self):
        """
        Switch UI based on the selected mode (All, Selected, Ranged, Single, Failed).
        This is called automatically when the user changes the combobox selection.
        With the new layout, all range-related widgets share one horizontal line.
        """
        selected_option = self.range_combo.currentText()
        self.hide_all_widgets()

        if selected_option == "Selected":
            self.show_selected_widgets()
        elif selected_option == "Ranged":
            self.show_ranged_widgets()
        elif selected_option == "Single":
            self.show_single_widgets()
            self.refresh_list()
        elif selected_option == "Failed":
            self.show_failed_widgets()
            self.refresh_failed_list()
        # For "All", no additional widgets are shown.

    def handle_filter_option_select(self):
        """
        Adjust default threshold values upon selecting a statistic to filter data by.
        """
        selected_option = self.filter_option_menu.currentText()
        if selected_option == "Resolution":
            self.sign_option_menu.setCurrentText(">")
            self.statistic_threshold.setText("1.10")
        elif selected_option == "Index%":
            self.sign_option_menu.setCurrentText("<")
            self.statistic_threshold.setText("65.0")
        elif selected_option == "CC1/2":
            self.sign_option_menu.setCurrentText("<")
            self.statistic_threshold.setText("95.0")
        elif selected_option == "I/Sigma":
            self.sign_option_menu.setCurrentText("<")
            self.statistic_threshold.setText("4.50")

    def hide_all_widgets(self):
        """
        Hide all optional sub-widgets by making them invisible.
        They remain in the layout but do not appear on-screen.
        """
        # Widgets for 'Selected' mode
        self.select_label.setVisible(False)
        self.filter_option_menu.setVisible(False)
        self.sign_option_menu.setVisible(False)
        self.statistic_threshold.setVisible(False)

        # Widgets for 'Ranged' mode
        self.range_input.setVisible(False)
        self.range_label_info.setVisible(False)

        # Widgets for 'Single' mode
        self.single_label.setVisible(False)
        self.single_file_option_menu.setVisible(False)

        # Widgets for 'Failed' mode
        self.failed_label.setVisible(False)
        self.failed_file_option_menu.setVisible(False)

        # Additional action buttons
        self.xdsgui_button.setVisible(False)
        self.view_lattice_button.setVisible(False)
        self.bus2shelx_button.setVisible(False)
        self.html_button.setVisible(False)
        self.folder_button.setVisible(False)

    def show_selected_widgets(self):
        """
        Show the widgets needed for 'Selected' mode.
        """
        self.select_label.setVisible(True)
        self.filter_option_menu.setVisible(True)
        self.sign_option_menu.setVisible(True)
        self.statistic_threshold.setVisible(True)

    def show_ranged_widgets(self):
        """
        Show the widgets needed for 'Ranged' mode.
        """
        self.range_input.setVisible(True)
        self.range_label_info.setVisible(True)

    def show_single_widgets(self):
        """
        Show the widgets needed for 'Single' mode (choose one dataset).
        """
        # Make sure the label appears along with the file selection combo box.
        self.single_label.setVisible(True)
        self.single_file_option_menu.setVisible(True)

        # Show the associated action buttons.
        self.xdsgui_button.setVisible(True)
        self.view_lattice_button.setVisible(True)
        self.bus2shelx_button.setVisible(True)
        self.html_button.setVisible(True)
        self.folder_button.setVisible(True)

    def show_failed_widgets(self):
        """
        Show the widgets needed for 'Failed' mode (choose a failed dataset).
        """
        self.failed_label.setVisible(True)
        self.failed_file_option_menu.setVisible(True)

        # Show the associated action buttons.
        self.xdsgui_button.setVisible(True)
        self.view_lattice_button.setVisible(True)
        self.folder_button.setVisible(True)

    def refresh_list(self):
        """
        Update the single dataset list from xdsrunner2.xlsx for single mode.
        """
        if self.input_path:
            xds_list = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
            self.relative_paths = {}
            for i, xds_path in enumerate(xds_list):
                short = f"{i + 1}:" + os.path.relpath(os.path.dirname(xds_path), self.input_path)
                self.relative_paths[short] = os.path.dirname(xds_path)

            items = ["--"] + list(self.relative_paths.keys())
            self.single_file_option_menu.clear()
            self.single_file_option_menu.addItems(items)
            self.single_file_option_menu.setCurrentIndex(0)
        else:
            print("No input path set for Single list.")

    def refresh_failed_list(self):
        """
        Update the failed dataset list from results for failed mode.
        """
        if not self.input_path:
            print("No input path set for Failed list.")
            return

        xdsrunner2 = os.path.join(self.input_path, "xdsrunner2.xlsx")
        xdsrunner = os.path.join(self.input_path, "xdsrunner.xlsx")
        success_list = []
        try:
            if os.path.exists(xdsrunner2):
                df = pd.read_excel(xdsrunner2, engine="openpyxl")
            elif os.path.exists(xdsrunner):
                df = pd.read_excel(xdsrunner, engine="openpyxl")
            else:
                QMessageBox.warning(self.window(), "Caution",
                                    "No xdsrunner2.xlsx or xdsrunner.xlsx found. Please run XDS.")
                return
            # suppose df has a column 'Path'
            for p in df["Path"]:
                if isinstance(p, str):
                    if p.startswith("..."):
                        success_list.append(os.path.join(self.input_path, p[4:]))
                    else:
                        success_list.append(p)
        except Exception as e:
            QMessageBox.warning(self.window(), "Caution",
                                f"No results found sut to {e}. Please update excel or run xds first.")
            return

        xds_list = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
        self.relative_paths = {}
        for i, xds_path in enumerate(xds_list):
            short = f"{i + 1}:" + os.path.relpath(os.path.dirname(xds_path), self.input_path)
            self.relative_paths[short] = os.path.dirname(xds_path)

        self.failed_relative_paths = {}
        for short, fullp in self.relative_paths.items():
            if fullp not in success_list:
                self.failed_relative_paths[short] = fullp

        items = ["--", "all"] + list(self.failed_relative_paths.keys())
        self.failed_file_option_menu.clear()
        self.failed_file_option_menu.addItems(items)
        self.failed_file_option_menu.setCurrentIndex(0)

    def get_xds_list(self):
        """
        Retrieve a list of XDS.INP files based on the selected criteria in the UI.
        """
        if not self.input_path:
            print("No input path set for get_xds_list().")
            return []
        all_xds_list = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
        selected_mode = self.range_combo.currentText()
        if selected_mode == "All":
            return all_xds_list
        elif selected_mode == "Ranged":
            return get_elements_by_indices(all_xds_list, self.range_input.text())
        elif selected_mode == "Selected":
            # e.g. check filter for resolution, etc.
            selected_indicator = self.filter_option_menu.currentText()
            if selected_indicator == "--":
                return []
            sign = self.sign_option_menu.currentText()
            threshold = float(self.statistic_threshold.text())
            # e.g. use xds_cluster's method
            indicator_map = {"Resolution": "Reso.", "Index%": "Index%", "I/Sigma": "ISa", "CC1/2": "CC1/2"}
            xds_list = xds_cluster.get_paths_by_indicator(
                os.path.join(self.input_path, "xdsrunner2.xlsx"),
                indicator_map[selected_indicator],
                sign,
                threshold
            )
            # if a path starts with "...", strip it
            for i, path in enumerate(xds_list):
                if path.startswith("..."):
                    xds_list[i] = os.path.join(self.input_path, path[4:], "XDS.INP")
            return xds_list
        elif selected_mode == "Single":
            chosen = self.single_file_option_menu.currentText()
            if chosen == "--":
                print("Please select data.")
                return []
            path_ = os.path.join(self.relative_paths[chosen], "XDS.INP")
            return [path_]
        elif selected_mode == "Failed":
            chosen = self.failed_file_option_menu.currentText()
            if chosen == "all":
                # add all from self.failed_relative_paths
                return [os.path.join(val, "XDS.INP") for val in self.failed_relative_paths.values()]
            elif chosen == "--":
                print("Please select data.")
                return []
            else:
                path_ = os.path.join(self.failed_relative_paths[chosen], "XDS.INP")
                return [path_]
        return []

    def run_xds(self):
        """
        Run XDS refinements based on chosen criteria and parameters. Animate the process until done.
        """
        if not self.input_path:
            QMessageBox.warning(self.window(), "Warning", "You need to set input_path first.")
            return
        xds_list = self.get_xds_list()
        if not xds_list:
            QMessageBox.warning(self.window(), "Warning", "No data selected to refine.")
            return

        # gather checkboxes
        parameter_dict = {
            "axis": self.update_axis.isChecked(),
            "divergence": self.add_divergence.isChecked(),
            "scale": float(self.scale_outlier_ratio.text()) if self.remove_scale_outlier.isChecked() else False,
            "index": float(self.index_ratio_threshold.text()) if self.update_index_ratio.isChecked() else False,
            "resolution": self.resolution_range.text() if self.update_resolution.isChecked() else False,
            "beam_centre": self.correct_centre.isChecked()
        }
        if self.range_combo.currentText() == "Failed":
            parameter_dict["scale"] = False

        self.xdsrunner_animation_active = True
        self.xdsrunner_animation_angle = 0

        t = KillableThread(target=xds_runner.refine_run, args=(self.input_path, xds_list, parameter_dict))
        self.thread["xds_runner"] = t
        t.start()
        self.xdsrunner_animation.startAnimation()
        QTimer.singleShot(100, self.check_xds_thread)

    def open_keyword_manager(self):
        if not self.input_path:
            QMessageBox.warning(self.window(), "Warning", "No input path set.")
            return
        xds_list = self.get_xds_list()
        if not xds_list:
            QMessageBox.warning(self.window(), "Warning", "No data selected.")
            return
        xds_input.create_keyword_manager_app(xds_list)

    def show_results(self):
        """
        Show updated results from xdsrunner2.xlsx in a QTreeWidget.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        xdsrunner_excel_path = os.path.join(self.input_path, "xdsrunner2.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            # Before displaying, remove any existing container
            if self._excel_container is not None:
                self.layout().removeWidget(self._excel_container)
                self._excel_container.deleteLater()
                self._excel_container = None

            # Also remove the old stretch if it exists
            if self._excel_stretch_item is not None:
                self.layout().removeItem(self._excel_stretch_item)
                self._excel_stretch_item = None

            self.display_excel_data(xdsrunner_excel_path, display_columns={
                "No.": "No.",
                "Path": "Path",
                "SG": "SG",
                "Unit cell": "Unit Cell",
                "Vol.": "Vol.",
                "Index%": "Index%",
                "ISa": "ISa",
                "Rmeas": "Rmeas",
                "CC1/2": "CC1/2",
                "Completeness": "Complete.",
                "Reso.": "Reso.",
            })
        else:
            QMessageBox.information(self.window(), "Error", "Cannot find xdsrunner.xlsx. Check or update it.")

    def open_xdsrunner_excel(self):
        if not self.input_path:
            QMessageBox.warning(self.window(), "Warning", "No input path set.")
            return
        xdsrunner_excel_path = os.path.join(self.input_path, "xdsrunner2.xlsx")
        if os.path.exists(xdsrunner_excel_path):
            try:
                if is_wsl:
                    subprocess.call([
                        "wsl.exe", "cmd.exe", "/C",
                        f"start explorer.exe {linux_to_windows_path(xdsrunner_excel_path)}"
                    ])
                    return
                # Try LibreOffice
                libreoffice_path = subprocess.run(
                    ["which", "libreoffice"], capture_output=True, text=True
                ).stdout.strip()
                if libreoffice_path:
                    subprocess.call(["libreoffice", "--calc", xdsrunner_excel_path])
                    return
                else:
                    QMessageBox.warning(self.window(), "Caution", "No LibreOffice or Explorer found.")
            except Exception as e:
                QMessageBox.critical(self.window(), "Caution", f"Error opening file: {e}")
        else:
            QMessageBox.critical(self.window(), "Caution",
                                 "Cannot find xdsrunner2.xlsx at the specified input path.")

    def update_excel(self):
        input_path = getattr(self, "input_path", None)
        if not input_path:
            # This warning is in the main thread, so it should display immediately.
            QMessageBox.warning(self, "Warning", "Input path is not set.")
            return

        def run_extraction():
            try:
                xds_runner.excel_extract(input_path, True)
            except PermissionError:
                self.errorOccurred.emit("Permission Error: Cannot write to xdsrunner.xlsx,"
                                        "It may be open in another application (e.g., Excel). "
                                        "Please close the Excel file and try again.")
                return
            QTimer.singleShot(0, self.show_results)

        t = threading.Thread(target=run_extraction)
        self.thread["update_excel"] = t
        t.start()

    def showError(self, err_msg):
        # Debug print to verify the slot is called
        print("showError called with:", err_msg)
        # This will run in the main thread and should display a QMessageBox.
        QMessageBox.critical(self, "Error", err_msg)

    # ------------------------------------------------------------------
    # Context-menu dispatch
    # ------------------------------------------------------------------

    # noinspection PyUnboundLocalVariable
    def _on_tree_context_menu(self, pos: QPoint) -> None:  # noqa: N802
        if self._tree is None:
            return
        selected_items = self._tree.selectedItems()
        if not selected_items:
            return

        # Find which column index corresponds to "Path"
        path_col = None
        for col in range(self._tree.columnCount()):
            if self._tree.headerItem().text(col) == "Path":
                path_col = col
                break
        if path_col is None:
            # If "Path" isn't visible, do nothing
            return

        # Build a list of path strings
        path_list: list[str] = [
            os.path.join(self.input_path, item.text(path_col)[4:]) if item.text(path_col).startswith(
                "...") else item.text(path_col) for item in selected_items]

        for path in path_list:
            if not os.path.exists(path):
                QMessageBox.warning(self.window(), "Warning", f"Path does not exist: {path}. "
                                                              f"Please update the excel.")
                return

        menu_pos = self._tree.viewport().mapToGlobal(pos)
        menu = QMenu(self)
        if len(path_list) == 1:
            act_open_folder = QAction("Open folder", self)
            act_open_html = QAction("Open HTML report", self)
            menu.addAction(act_open_folder)
            menu.addAction(act_open_html)
            menu.addSeparator()
        act_run = QAction("Run XDS", self)
        act_edit = QAction("Edit SG and Unit Cell", self)
        act_shelx = QAction("Bus to SHELX", self)
        act_move = QAction("Move to folder", self)
        menu.addAction(act_run)
        menu.addAction(act_edit)
        menu.addAction(act_shelx)
        menu.addAction(act_move)

        triggered = menu.exec(menu_pos)
        if len(path_list) == 1 and triggered is act_open_folder:
            self._open_folder(path_list[0])
        elif len(path_list) == 1 and triggered is act_open_html:
            self._open_html(path_list[0])
        elif triggered is act_edit:
            self._edit_sg_unit_cell(path_list)
        elif triggered is act_run:
            self._run_xds_with_paths(path_list, direct=True)
        elif triggered is act_shelx:
            self._bus_to_shelx(path_list)
        elif triggered is act_move:
            self._move_to_folder(path_list)

    def view_lattice(self):
        selected_mode = self.range_combo.currentText()
        if selected_mode == "Single":
            chosen = self.single_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
        elif selected_mode == "Failed":
            chosen = self.failed_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
        else:
            return
        chosen = chosen.split(":")[1]
        command = sys.executable
        arguments = [os.path.join(script_dir, "src", "visualisation", "recip_viewer_GUI.py"), "-f", self.input_path,
                     "-d", chosen]
        self.process.start(command, arguments)

    def run_xdsgui(self):
        selected_mode = self.range_combo.currentText()
        if selected_mode not in ["Single", "Failed"]:
            return
        if not self.input_path:
            QMessageBox.warning(self.window(), "Warning", "No input path set.")
            return

        if selected_mode == "Single":
            chosen = self.single_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
            _path = self.relative_paths[chosen]
        else:  # Failed
            chosen = self.failed_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
            _path = self.failed_relative_paths[chosen]

        def run_command(dirpath):
            print("The output of XDSGUI is as below.")
            os.chdir(dirpath)
            os.system("xdsgui")

        command_thread = threading.Thread(target=run_command, args=(_path,))
        command_thread.start()

    def open_html_report(self):
        selected = self.single_file_option_menu.currentText()
        if selected == "--":
            return

        _path = self.relative_paths[selected]

        t = threading.Thread(target=self._open_html, args=(_path,))
        t.start()

    def run_xdsconv_shelx(self):
        selected = self.single_file_option_menu.currentText()
        if selected == "--":
            return
        _path = self.relative_paths[selected]
        shelx_thread = threading.Thread(target=self._do_shelx, args=([_path],))
        shelx_thread.start()

    def open_folder_gui(self):
        selected_mode = self.range_combo.currentText()
        if selected_mode == "Single":
            chosen = self.single_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
            _path = self.relative_paths[chosen]
        elif selected_mode == "Failed":
            chosen = self.failed_file_option_menu.currentText()
            if chosen in ["--", "all"]:
                return
            _path = self.failed_relative_paths[chosen]
        else:
            return
        self._open_folder(_path)


class MergeData(QWidget):
    """
    Class MergeData
    Handles merging datasets after filtering them using xdspicker.xlsx.

    Methods:
        __init__(parent): Initializes the MergeData page and sets up its GUI elements.
        run_xds_merge(): Calls the merge function to run XSCALE on the filtered data.
        run_xdsconv_shelx(): Generates .hkl and .p4p files for SHELX from merged data.
        show_result(): Displays partial content of XSCALE.LP focusing on output statistics.
        open_xscale_lp(): Opens the entire XSCALE.LP file in a separate window.
        run_filter(): Filters data by chosen criteria (I/Sigma, CC1/2, etc.) and generates xdspicker.xlsx.
        handle_option_select(): Adjusts default filter values upon selecting a filter criterion.
        open_picker_xlsx(): Opens xdspicker.xlsx in LibreOffice or Explorer for manual editing.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize the MergeData page and set up its GUI for filtering and merging data.

        Args:
            parent (QWidget): The parent widget where this page will be placed.
        """
        super().__init__(parent)

        self.thread = {}
        self.input_path = ""  # To be set elsewhere

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(16)  # Use a bit more spacing between rows
        main_layout.addSpacing(12)

        # Label for merging data instruction
        merge_data_label = QLabel("Generate and Merge data from xdspicker.xlsx.")
        main_layout.addWidget(merge_data_label)

        # Note label with italic font
        note_label = QLabel("Note: Average unit cell parameters will be used during merging.")
        note_font = QFont("Liberation Sans", 13)
        note_font.setItalic(True)
        note_label.setFont(note_font)
        main_layout.addWidget(note_label)

        # Section I: Filter data for merging
        filter_section_label = QLabel("I. Filter data for merging")
        main_layout.addWidget(filter_section_label)

        # Row for filter options using a horizontal layout
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)
        row1_layout.addSpacing(20)

        label1 = QLabel("Use the data with")
        row1_layout.addWidget(label1)

        self.option_menu = ComboBox()
        self.option_menu.addItems(["--", "I/Sigma", "CC1/2", "R_meas", "Reso."])
        self.option_menu.setCurrentIndex(0)
        self.option_menu.setFixedWidth(100)
        self.option_menu.setToolTip("Choose a filter for initial data merging.")
        # Connect the signal to adjust default filter values
        self.option_menu.currentTextChanged.connect(self.handle_option_select)
        row1_layout.addWidget(self.option_menu)

        label2 = QLabel("better than")
        row1_layout.addWidget(label2)

        self.input_filter = QLineEdit()
        self.input_filter.setFixedWidth(100)
        self.input_filter.setToolTip("Use the default value or customise.")
        row1_layout.addWidget(self.input_filter)

        label3 = QLabel("for merging.")
        row1_layout.addWidget(label3)

        # Button to perform filtering action
        filter_button = QPushButton("Filter Data")
        filter_button.setToolTip('Generate "xdspicker.xlsx" for data merging.')
        filter_button.clicked.connect(self.run_filter)
        row1_layout.addWidget(filter_button)

        # Button for manual filtering
        manual_filter_button = QPushButton("Manually Filter")
        manual_filter_button.setToolTip('Open "xdspicker.xlsx" to delete \nundesired data in excel / libreoffice.')
        manual_filter_button.clicked.connect(self.open_picker_xlsx)
        row1_layout.addWidget(manual_filter_button)
        row1_layout.addStretch()
        main_layout.addLayout(row1_layout)

        # Section II: Merge Data
        merge_section_label = QLabel("II. Merge Data")
        main_layout.addWidget(merge_section_label)

        # Row for merge action buttons
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(30)
        row2_layout.addSpacing(20)

        merge_button = QPushButton("Merge Data")
        merge_button.setToolTip('Run XScale and merge data in "merge" subfolder.')
        merge_button.clicked.connect(self.run_xds_merge)
        row2_layout.addWidget(merge_button)

        show_result_button = QPushButton("Show Result")
        show_result_button.setToolTip('Display statistic table from XSCALE.LP in "merge" subfolder.')
        show_result_button.clicked.connect(self.show_result)
        row2_layout.addWidget(show_result_button)

        open_lp_button = QPushButton("Open XSCALE.LP")
        open_lp_button.setToolTip('Open XSCALE.LP of merged data in "merge" subfolder.')
        open_lp_button.clicked.connect(self.open_xscale_lp)
        row2_layout.addWidget(open_lp_button)

        pre_cluster_label = QLabel("* Recommend to cluster before")
        row2_layout.addWidget(pre_cluster_label)

        bus2shelx_button = QPushButton("Bus to SHELX")
        bus2shelx_button.setToolTip('Generate hkl and p4p file on merged data.')
        bus2shelx_button.clicked.connect(self.run_xdsconv_shelx)
        row2_layout.addWidget(bus2shelx_button)

        open_folder_button = QPushButton("Open Folder")
        open_folder_button.setToolTip('Open the folder of merged data.')
        open_folder_button.clicked.connect(self.open_folder)
        row2_layout.addWidget(open_folder_button)

        main_layout.addLayout(row2_layout)
        row2_layout.addStretch()

        # Text area to display XSCALE.LP content
        self.result_text = QTextEdit()
        result_font = QFont("Liberation Mono", 11)
        self.result_text.setFont(result_font)
        self.result_text.setReadOnly(True)
        main_layout.addWidget(self.result_text)

    def run_xds_merge(self) -> None:
        """
        Run XSCALE to merge filtered datasets. Executed in a separate thread.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return

        xds_cluster.merge(self.input_path, )

    def run_xdsconv_shelx(self) -> None:
        """
        Generate .hkl and .p4p files for SHELX from the merged data.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return

        self.thread["xdsconv"] = threading.Thread(target=xds_shelx.convert_to_shelx, args=(self.input_path,))
        self.thread["xdsconv"].start()
        merge_path = os.path.join(self.input_path, "merge")
        self.thread["report"] = threading.Thread(target=html_report.create_html_file,
                                                 args=(merge_path, "cluster"))
        self.thread["report"].start()

    def show_result(self) -> None:
        """
        Display partial content of XSCALE.LP focusing on output statistics of merged data.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return

        merge_dir_path = os.path.join(self.input_path, "merge")
        xscale_lp_path = None
        for file in os.listdir(merge_dir_path):
            if file.lower() == 'xscale.lp':
                xscale_lp_path = os.path.join(merge_dir_path, file)
                break

        if not xscale_lp_path or not os.path.exists(xscale_lp_path):
            QMessageBox.critical(self.window(), "Caution", "xscale.lp file not found in the merge directory.")
            return

        start_keyword = "SUBSET OF INTENSITY DATA"
        end_keyword = "STATISTICS OF INPUT DATA SET"
        content_to_display = ""
        capture = False

        with open(xscale_lp_path, "r") as file:
            for line in file:
                stripped_line = line.strip()
                if start_keyword in stripped_line:
                    capture = True
                elif end_keyword in stripped_line:
                    break
                if capture:
                    content_to_display += line

        self.result_text.clear()
        self.result_text.setPlainText(content_to_display)

    def open_xscale_lp(self) -> None:
        """
        Open the entire XSCALE.LP file in a separate window to inspect merged data statistics.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return

        merge_dir_path = os.path.join(self.input_path, "merge")
        xscale_lp_path = None
        for file in os.listdir(merge_dir_path):
            if file.lower() == 'xscale.lp':
                xscale_lp_path = os.path.join(merge_dir_path, file)
                break

        if not xscale_lp_path or not os.path.exists(xscale_lp_path):
            QMessageBox.critical(self.window(), "Caution", "xscale.lp file not found in the merge directory.")
            return

        # Create a dialogue to display the full content
        dialog = QDialog(self)
        dialog.setWindowTitle("Xscale.lp Content")
        dialog.resize(1000, 600)

        dialog_layout = QVBoxLayout(dialog)
        text_widget = QTextEdit()
        text_font = QFont("Liberation Mono", 11)
        text_widget.setFont(text_font)
        text_widget.setReadOnly(True)
        dialog_layout.addWidget(text_widget)

        with open(xscale_lp_path, "r") as file:
            content = file.read()
            text_widget.setPlainText(content)

        dialog.exec()

    def run_filter(self) -> None:
        """
        Filter data by chosen criteria (I/Sigma, CC1/2, etc.) and generate xdspicker.xlsx for merging.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        try:
            xdspicker_filter_value = float(self.input_filter.text())
        except ValueError:
            QMessageBox.critical(self.window(), "Error", "Please enter a valid value in the filter.")
            return

        selected_option = self.option_menu.currentText()
        keyword_dict = {'I/Sigma': 'isa', 'CC1/2': 'cc12', 'Reso.': 'reso', 'R_meas': 'rmeas'}
        if xdspicker_filter_value and selected_option in keyword_dict:
            xds_cluster.filter_data(self.input_path, xdspicker_filter_value, keyword_dict[selected_option])

    def handle_option_select(self, text: str) -> None:
        """
        Adjust default filter values upon selecting a filter criterion.

        Args:
            text (str): The selected filter option.
        """
        if text == 'I/Sigma':
            replace_entry(self.input_filter, "5")
        elif text == 'R_meas':
            replace_entry(self.input_filter, "50")
        elif text == 'CC1/2':
            replace_entry(self.input_filter, "95")
        elif text == 'Reso.':
            replace_entry(self.input_filter, "1.0")

    def open_picker_xlsx(self) -> None:
        """
        Open xdspicker.xlsx in LibreOffice or Explorer for manual editing of the filtered data list.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return

        xlsx_path = os.path.join(self.input_path, "xdspicker.xlsx")
        if not os.path.exists(xlsx_path):
            source_path = os.path.join(self.input_path, "xdsrunner2.xlsx")
            if os.path.exists(source_path):
                shutil.copy(source_path, xlsx_path)
            else:
                QMessageBox.critical(self.window(), "Caution", "Source xdsrunner2.xlsx not found.")
                return

        try:
            if is_wsl:  # Assuming is_wsl and linux_to_windows_path are defined elsewhere
                subprocess.call(["wsl.exe", "cmd.exe", "/C", f"start explorer.exe {linux_to_windows_path(xlsx_path)}"])
                return

            libreoffice_path = subprocess.run(["which", "libreoffice"], capture_output=True, text=True).stdout.strip()
            if libreoffice_path:
                subprocess.call(["libreoffice", "--calc", xlsx_path])
                return
        except Exception as e:
            QMessageBox.critical(self.window(), "Caution", f"Error opening the form due to {e}.")
        QMessageBox.critical(self.window(), "Caution", "Neither LibreOffice nor Explorer is available.")

    def open_folder(self) -> None:
        if self.input_path and os.path.exists(os.path.join(self.input_path, "merge")):
            if is_wsl:
                subprocess.Popen(["explorer.exe", "."], cwd=os.path.join(self.input_path, "merge"))
            else:
                open_folder_linux(os.path.join(self.input_path, "merge"))


class Cluster_Output(QWidget):
    """
    Class Cluster_Output
    Manages intensity-based clustering results and related outputs.

    Methods:
        __init__(parent): Initializes the Cluster_Output page.
        run_clustering(): Extracts dendrogram and sets cutoff distance from user interaction.
        update_distance(distance): Callback that updates the distance entry after dendrogram interaction.
        disable_set_distance_button(): Disables the dendrogram-related button.
        enable_set_distance_button(): Enables the dendrogram-related button.
        open_graph(): Generates and displays the dendrogram in a popup.
        generate_and_display_dendrogram(var): Generates dendrogram in a thread and displays on completion.
        show_image_popup(image_path): Shows the dendrogram image in a popup window.
        open_html(): Opens the HTML report for a chosen cluster.
        make_clusters(): Creates clusters using a specified cutoff distance and runs XSCALE on them.
        update_path_dict(output=False): Refreshes and displays the list of clusters and their statistics.
        run_xprep(): Run XPREP on the chosen cluster if configured.
        on_cryo_checkbox_change(): Updates temperature field if cryo conditions are toggled.
        update_metadata(): Updates .ins and .cif_od files with metadata.
        output_p4p_option(): Prints information about the selected cluster option.
        open_folder(): Opens the folder corresponding to the selected cluster.
    """

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.thread = {}
        self.p4p_path_dict = {}
        self.input_path = ""

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(12)
        main_layout.addSpacing(12)

        # Row 0: Clustering header
        clustering_label = QLabel("Intensity-Cluster based on Correlation Coefficients in XSCALE.LP")
        main_layout.addWidget(clustering_label)

        # Row 1: Distance instruction label
        distance_instruction = QLabel("The distance can either be gathered from the Dendrogram or manually input.")
        font = QFont("Liberation Sans", 13)
        font.setItalic(True)
        distance_instruction.setFont(font)
        main_layout.addWidget(distance_instruction)

        # Row 2: Clustering options (buttons and entries)
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_widget.setLayout(buttons_layout)
        main_layout.addWidget(buttons_widget)

        # "Set Distance from Dendrogram" button
        self.set_distance_button = QPushButton("Set Distance from Dendrogram")
        self.set_distance_button.setToolTip("Set the cut-off distance from the dendrogram.")
        self.set_distance_button.clicked.connect(self.run_clustering)
        buttons_layout.addWidget(self.set_distance_button)
        buttons_layout.setSpacing(20)

        # Distance label and input field
        distance_label = QLabel("Distance")
        buttons_layout.addWidget(distance_label)

        self.input_distance = QLineEdit()
        self.input_distance.setFixedWidth(70)
        self.input_distance.setToolTip("Distance used for clustering.")
        self.input_distance.setText("1.0")
        buttons_layout.addWidget(self.input_distance)

        # Overwrite checkbox
        self.overwrite_checkbox = QCheckBox("Overwrite previous result")
        self.overwrite_checkbox.setChecked(True)
        self.overwrite_checkbox.setToolTip("If ticked, existing cluster folders will be overwritten.")
        buttons_layout.addWidget(self.overwrite_checkbox)

        # "Make Cluster based on Distance" button
        make_cluster_button = QPushButton("Make Cluster based on Distance")
        make_cluster_button.setToolTip("Use the input distance for cluster making and data merging")
        make_cluster_button.clicked.connect(self.make_clusters)
        buttons_layout.addWidget(make_cluster_button)
        buttons_layout.addStretch()

        main_layout.addSpacing(20)

        # Row 3: Process clusters header
        process_label = QLabel("Process Clusters and Generate .INS")
        main_layout.addWidget(process_label)

        shelx_label = QLabel(
            "Press Refresh to view the information of all clusters. Run XPREP will raise XPREP in Windows. "
            "Set the XPREP path in `setting.ini` first!")
        shelx_label.setFont(font)
        main_layout.addWidget(shelx_label)

        # Row 4: Data processing (cluster selection and refresh)
        row22_widget = QWidget()
        row22_layout = QHBoxLayout()
        row22_layout.setSpacing(10)
        row22_widget.setLayout(row22_layout)
        row22_layout.setSpacing(30)

        data_label = QLabel("Data Processing Based on")
        row22_layout.addWidget(data_label)

        self.p4p_option_menu = ComboBox()
        self.p4p_option_menu.setMaxVisibleItems(10)
        self.p4p_option_menu.addItem("--")
        self.p4p_option_menu.setFixedWidth(250)
        self.p4p_option_menu.setToolTip("Choose the cluster to work with.")
        self.p4p_option_menu.currentTextChanged.connect(self.output_p4p_option)
        row22_layout.addWidget(self.p4p_option_menu)

        refresh_button = QPushButton("Refresh and Show Summary")
        refresh_button.setToolTip("Refresh and show clusters summary in the command window.")
        refresh_button.clicked.connect(lambda: self.update_path_dict(output=True))
        row22_layout.addWidget(refresh_button)
        row22_layout.addStretch()

        main_layout.addWidget(row22_widget)

        # Row 5: Additional processing buttons
        row23_widget = QWidget()
        row23_layout = QHBoxLayout()
        row23_layout.setSpacing(30)
        row23_widget.setLayout(row23_layout)

        open_graph_button = QPushButton("Open Dendrogram")
        open_graph_button.setToolTip("Show the dendrogram of current clusters.")
        open_graph_button.clicked.connect(self.open_graph)
        row23_layout.addWidget(open_graph_button)

        open_scale_button = QPushButton("Open XSCALE.LP")
        open_scale_button.setToolTip("Open XSCALE.LP of current clusters.")
        open_scale_button.clicked.connect(self.open_xscale_lp)
        row23_layout.addWidget(open_scale_button)

        run_xprep_button = QPushButton("Run XPREP")
        run_xprep_button.setToolTip("Run XPREP of the chosen cluster to generate symm_shelx .ins file.")
        run_xprep_button.clicked.connect(self.run_xprep)
        row23_layout.addWidget(run_xprep_button)

        open_html_button = QPushButton("Open Report")
        open_html_button.setToolTip("Generate and Open the web report on current working data.")
        open_html_button.clicked.connect(self.open_html)
        row23_layout.addWidget(open_html_button)
        row23_layout.addStretch()

        main_layout.addWidget(row23_widget)
        main_layout.addSpacing(20)

        # Row 6: Metadata header and instructions
        metadata_header = QLabel("Collect and Generate Metadata File")
        main_layout.addWidget(metadata_header)

        metadata_instruction = QLabel(
            "Metadata will be updated with provided information and headers in .img file, "
            "and saved in the .CIF_OD file. Olex2 will pick it up automatically.")
        metadata_instruction.setFont(font)
        main_layout.addWidget(metadata_instruction)

        compound_instr = QLabel("The compound name in short should be only one word.")
        compound_instr.setFont(font)
        main_layout.addWidget(compound_instr)

        # Row 7: Instrument Profile selection
        row32_widget = QWidget()
        row32_layout = QHBoxLayout()
        row32_layout.setSpacing(30)
        row32_widget.setLayout(row32_layout)

        instrument_profile_label = QLabel("Instrument Profile:")
        row32_layout.addWidget(instrument_profile_label)

        self.ins_option_menu = ComboBox()
        self.ins_option_menu.setMaxVisibleItems(10)
        self.ins_option_menu.setToolTip("Default Instrument Profile can be loaded.")
        self.ins_option_menu.currentTextChanged.connect(self.load_instrument_parameter)
        row32_layout.addWidget(self.ins_option_menu)
        row32_layout.addStretch()
        row32_layout.setSpacing(12)

        main_layout.addWidget(row32_widget)

        # Row 8: Instrument, Detector, Temperature, and Cryo checkbox
        row33_widget = QWidget()
        row33_layout = QHBoxLayout()
        row33_layout.setSpacing(20)
        row33_widget.setLayout(row33_layout)

        tem_label = QLabel("TEM Instrument")
        row33_layout.addWidget(tem_label)

        self.instrument = QLineEdit()
        self.instrument.setFixedWidth(200)
        row33_layout.addWidget(self.instrument)

        detector_label = QLabel("Detector")
        row33_layout.addWidget(detector_label)

        self.detector = QLineEdit()
        self.detector.setFixedWidth(200)
        row33_layout.addWidget(self.detector)

        temp_label = QLabel("Temperature")
        row33_layout.addWidget(temp_label)

        self.temperature = QLineEdit()
        self.temperature.setFixedWidth(75)
        row33_layout.addWidget(self.temperature)

        k_label = QLabel("K")
        row33_layout.addWidget(k_label)

        self.cryo_checkbox = QCheckBox("Cryoholder")
        self.cryo_checkbox.setChecked(True)
        self.cryo_checkbox.setToolTip("Tick if cryoholder is used.")
        self.cryo_checkbox.stateChanged.connect(self.on_cryo_checkbox_change)
        row33_layout.addWidget(self.cryo_checkbox)

        self.temperature.setText("100")
        row33_layout.addStretch()

        main_layout.addWidget(row33_widget)

        # Row 9: Compound names (short and long)
        row34_widget = QWidget()
        row34_layout = QHBoxLayout()
        row34_layout.setSpacing(20)
        row34_widget.setLayout(row34_layout)

        short_label = QLabel("Compound Name\t Short Name:")
        row34_layout.addWidget(short_label)

        self.short_name = QLineEdit()
        self.short_name.setFixedWidth(150)
        row34_layout.addWidget(self.short_name)

        long_label = QLabel("  Long Name:")
        row34_layout.addWidget(long_label)

        self.long_name = QLineEdit()
        self.long_name.setFixedWidth(250)
        row34_layout.addWidget(self.long_name)
        row34_layout.addStretch()

        main_layout.addWidget(row34_widget)

        # Row 10: Buttons to update metadata and open folder
        row35_widget = QWidget()
        row35_layout = QHBoxLayout()
        row35_layout.setSpacing(30)
        row35_widget.setLayout(row35_layout)

        update_metadata_button = QPushButton("Update INS and Metadata")
        update_metadata_button.setToolTip("Generate .CIF_OD containing metadata and data reduction detail.")
        update_metadata_button.clicked.connect(self.update_metadata)
        row35_layout.addWidget(update_metadata_button)

        open_folder_button = QPushButton("Open Folder")
        open_folder_button.setToolTip("Open the folder of selected cluster.")
        open_folder_button.clicked.connect(self.open_folder)
        row35_layout.addWidget(open_folder_button)
        row35_layout.addStretch()

        main_layout.addWidget(row35_widget)
        main_layout.addStretch()

        # Load instrument profile options into the instrument combobox
        self.ins_path_dict = self.load_instrument_profile()
        ins_options = ["--"] + list(self.ins_path_dict.keys())
        self.ins_option_menu.clear()
        self.ins_option_menu.addItems(ins_options)

    @classmethod
    def load_instrument_profile(cls) -> dict:
        _path_dict = {}
        _file_path = os.path.join(script_dir, "instrument_profile")
        if os.path.isdir(_file_path):
            _files_list = sorted([f for f in os.listdir(_file_path) if os.path.isfile(os.path.join(_file_path, f))])
            for f in _files_list:
                if f != "__init__.py":
                    _path_dict[f] = os.path.join(_file_path, f)
        return _path_dict

    def open_xscale_lp(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            return
        path = self.p4p_path_dict.get(var, "")
        if not path:
            return

        xscale_lp_path = None
        for file in os.listdir(path):
            if file.lower() == 'xscale.lp':
                xscale_lp_path = os.path.join(path, file)
                break

        if not xscale_lp_path or not os.path.exists(xscale_lp_path):
            QMessageBox.critical(self.window(), "Caution", "xscale.lp file not found in the merge directory.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Xscale.lp Content")
        dialog.resize(1000, 600)
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        font = QFont("Liberation Mono", 11)
        text_edit.setFont(font)
        layout.addWidget(text_edit)
        with open(xscale_lp_path, "r") as file:
            content = file.read()
            text_edit.setPlainText(content)
        dialog.exec()

    def load_instrument_parameter(self, text: str) -> None:
        if text == "--":
            return
        print(f"Reading Instrument Parameter: {text}")
        file_path = self.ins_path_dict.get(text, "")
        if not file_path:
            return
        try:
            with open(file_path, "r") as file:
                parameters = json.load(file)
                self.instrument.setText(parameters.get("instrument", ""))
                self.detector.setText(parameters.get("detector", ""))
                if "temperature" in parameters:
                    self.temperature.setText(str(parameters.get("temperature", "")))
        except FileNotFoundError:
            QMessageBox.critical(self.window(), "Caution", "Error: The file does not exist.")

    def run_clustering(self) -> None:
        if not self.input_path:
            QMessageBox.warning(self.window(), "Input Path Missing", "Please select an input path first.")
            return

        merge_path = os.path.join(self.input_path, "merge")
        if not os.path.exists(merge_path):
            QMessageBox.critical(self.window(), "Merge Directory Missing",
                                 f"The directory '{merge_path}' does not exist.")
            return

        self.set_distance_button.setEnabled(False)
        callback_with_self = partial(self.update_distance)
        xds_cluster.extract_dendrogram(
            input_path=merge_path,
            interactive=True,
            callback=callback_with_self,
            work_folder=self.input_path,
        )

    def update_distance(self, distance: float) -> None:
        if distance is not None:
            self.input_distance.setText(f"{distance:.4f}")
        else:
            QMessageBox.critical(self.window(), "Error", "Failed to extract cutoff distance.")
        self.set_distance_button.setEnabled(True)

    def open_graph(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            return
        self.generate_and_display_dendrogram(var)

    def generate_and_display_dendrogram(self, var: str) -> None:
        try:
            xds_cluster.extract_dendrogram(self.p4p_path_dict[var], interactive=False)
            image_path = os.path.join(self.p4p_path_dict[var], "dendrogram.png")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Dendrogram image not found at {image_path}")
            self.show_image_popup(image_path)
        except Exception as e:
            QMessageBox.critical(self.window(), "Error", str(e))

    def show_image_popup(self, image_path: str) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Dendrogram")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        label = QLabel()
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.critical(self.window(), "Error", "Failed to load image.")
            return
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        layout.addWidget(label)
        dialog.exec()

    def open_html(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            return
        html_report.open_html_file(self.p4p_path_dict[var], "cluster")

    def make_clusters(self) -> None:
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        try:
            distance = float(self.input_distance.text())
        except ValueError:
            QMessageBox.critical(self.window(), "Error", "Please enter a valid distance value.")
            return
        overwrite = self.overwrite_checkbox.isChecked()
        self.thread["cluster_maker"] = threading.Thread(
            target=xds_cluster.make_cluster,
            args=(self.input_path, distance, overwrite)
        )
        self.thread["cluster_maker"].start()

    def update_path_dict(self, output: bool = False) -> None:
        """
        Refreshes and displays the list of clusters and their statistics.

        Args:
            output (bool): If True, print the cluster statistics to the console.
        """
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        self.p4p_path_dict = {}
        self.p4p_option_menu.clear()
        self.p4p_option_menu.addItem("--")
        merge_folder_path = os.path.join(self.input_path, "merge")
        if not os.path.isdir(merge_folder_path):
            for root, dirs, files in os.walk(self.input_path):
                for dir_name in dirs:
                    if "cluster" in dir_name.lower() or "iter" in dir_name.lower() or "cls" in dir_name.lower():
                        merge_folder_path = root
                        break
        for item in os.listdir(merge_folder_path):
            item_path = os.path.join(merge_folder_path, item)
            if os.path.isdir(item_path) and (
                    'cluster' in item_path.lower() or "iter" in item_path.lower() or 'cls' in item_path.lower()):
                self.p4p_path_dict[item] = item_path
            elif os.path.isfile(item_path) and item.lower().endswith('.p4p'):
                self.p4p_path_dict["merge"] = merge_folder_path

        self.p4p_path_dict = {key: self.p4p_path_dict[key]
                              for key in sorted(self.p4p_path_dict.keys(), key=natural_sort_key)}
        options = ["--"] + list(self.p4p_path_dict.keys())
        self.p4p_option_menu.clear()
        self.p4p_option_menu.addItems(options)
        self.p4p_option_menu.setCurrentText("--")

        if output:
            columns = ["Cluster", "#Datasets", "Completeness", "Redundancy", "Resolution", "ISa", "CC1/2", "R_meas"]
            results_df = pd.DataFrame(columns=columns)
            reso_report = None
            for key, path in self.p4p_path_dict.items():
                if not os.path.isfile(os.path.join(path, "all.HKL")):
                    continue
                result_dict = xds_analysis.extract_cluster_result(path)
                if result_dict:
                    result = [
                        key,
                        len(result_dict.get("input", [])),
                        result_dict.get("completeness", 0.0),
                        "{:.2f}".format(result_dict.get("N_obs", 0) / result_dict.get("N_uni", 1)),
                        result_dict.get("resolution", 5.0),
                        result_dict.get("ISa_meas", 5.0),
                        result_dict.get("cc12_reso", result_dict.get("CC1/2", 0.0)),
                        result_dict.get("rmeas", result_dict.get("R_meas", 0.0))
                    ]
                    new_row = pd.DataFrame([result], columns=columns)
                    results_df = pd.concat([results_df, new_row], ignore_index=True)
                    reso_report = result_dict.get("merge_resolution", None)
            headers = ["Cluster", "#Set.", "Complete.", "Redun.", "Reso.", "ISa", "CC1/2", "R_meas"]
            col_widths = [15, 5, 9, 6, 6, 6, 6, 6]
            header_str = "  ".join(f"{header:<{width}}" for header, width in zip(headers, col_widths))
            row_strs = []
            for index, row in results_df.iterrows():
                row_strs.append("  ".join(f"{str(val):<{width}}" for val, width in zip(row, col_widths)))
            table = f"  {header_str}\n{'-' * (len(header_str) + 2)}\n  " + "\n  ".join(row_strs)
            title = ("\nList of Clusters (Abbr. = Datasets, Completeness, Redundancy, Resolution):\n" +
                     ("\n" if analysis_engine == "XDS" else f"Completeness calculates based on {reso_report} A\n\n"))
            print(title + table + "\n")

    def run_xprep(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            return
        xprep_path = f"\"{config['General']['xprep_location']}\"" if config["General"]["xprep_location"] else "xprep"

        def run_command(xprep, directory):
            print(f"\nRun XPREP under {directory}.\n")
            command = f'cmd.exe /c {xprep} 1' if is_wsl else "xprep 1"
            os.chdir(directory)
            os.system(command)

        command_thread = threading.Thread(target=run_command, args=(xprep_path, self.p4p_path_dict[var]))
        command_thread.start()

    def on_cryo_checkbox_change(self) -> None:
        if self.cryo_checkbox.isChecked():
            self.temperature.setText("100")
        else:
            self.temperature.setText("298")

    def update_metadata(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            return
        ins_path = self.p4p_path_dict[var]
        ins_files = glob.glob(os.path.join(ins_path, "*.ins"))
        pcf_files = glob.glob(os.path.join(ins_path, "*.pcf"))
        if ins_files and pcf_files:
            newest_ins_file = max(ins_files, key=os.path.getmtime)
            newest_pcf_file = max(pcf_files, key=os.path.getmtime)
            xds_analysis.collect_metadata(self.input_path)
            info_dict = {
                "detector": self.detector.text(),
                "instrument": self.instrument.text(),
                "temperature": self.temperature.text(),
                "short_name": self.short_name.text(),
                "long_name": self.long_name.text()
            }
            update_thread = threading.Thread(target=xds_shelx.update_after_prep,
                                             args=(self.input_path, newest_ins_file, newest_pcf_file, info_dict))
            update_thread.start()
            if self.short_name.text():
                short_name = self.short_name.text().split()[
                    0] if " " in self.short_name.text() else self.short_name.text()
                old_hkl_path = newest_ins_file[:-3] + "hkl"
                new_hkl_path = os.path.join(os.path.dirname(newest_ins_file), short_name + ".hkl")
                if old_hkl_path != new_hkl_path:
                    shutil.copy(old_hkl_path, new_hkl_path)
            QMessageBox.information(self.window(), "Info",
                                    "The INS file is updated and data reduction information is within cif_od file.")
        else:
            QMessageBox.critical(self.window(), "Caution", "XPREP needs to run before implementing metadata.")

    def output_p4p_option(self, text: str) -> None:
        """
        Prints information about the selected cluster option.

        Args:
            text (str): The selected cluster option.
        """
        if text in ["--", ".", ""]:
            return
        print(f"Process on {self.p4p_path_dict.get(text, '')}.")

    def open_folder(self) -> None:
        var = self.p4p_option_menu.currentText()
        if var == "--":
            if self.input_path:
                reply = QMessageBox.question(self.window(), "Caution", "Do you want to open the root folder?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    if is_wsl:
                        subprocess.Popen(["explorer.exe", "."], cwd=self.input_path)
                    else:
                        open_folder_linux(self.input_path)
        else:
            if is_wsl:
                subprocess.Popen(["explorer.exe", "."], cwd=self.p4p_path_dict[var])
            else:
                open_folder_linux(self.p4p_path_dict[var])
