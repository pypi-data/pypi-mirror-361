"""Tools GUI Module

This module provides a graphical interface for managing various operations within the
crystallographic data processing workflow. It enables users to perform tasks such as
generating REDp files, rolling back XDS.INP files to specific stages, modifying image paths,
and creating PETS input files. The `Tools` class integrates with other AutoLEI modules to
streamline data processing and visualisation.

Features:
    - **REDp File Generation**: Supports the generation of REDp files from FEI `.mrc` files.
    - **Rollback Operations**: Allows users to roll back XDS.INP files to the "P1 stage"
      "Cell stage" or the last refinement stage.
    - **Path Modification**: Facilitates updating image paths in XDS.INP files to either
      absolute or relative paths.
    - **PETS Input Generation**: Automates the creation of PETS input files from `.mrc` files.
    - **File Deletion**: Provides functionality to delete XDS-related files with user confirmation.
    - **GUI Animations**: Includes real-time animations for task progress visualisation.

Classes:
    Tools:
        Main class representing the GUI interface for managing crystallographic operations.

Attributes:
    config (configparser.ConfigParser): Configuration settings loaded from the `setting.ini` file.
    script_dir (str): The directory where the script is located.
    analysis_engine (str): The analysis engine configured for HKL analysis.
    path_filter (bool): Boolean flag indicating whether to apply a path filter.
    is_wsl (bool): Indicates whether the script is running in a Windows Subsystem for Linux (WSL) environment.

Dependencies:
    Standard Libraries:
        - configparser
        - tkinter
        - os
        - shutil
        - threading
        - warnings
    Custom Modules:
        - xds_input
        - image_io
        - generate_pets
        - util (various utility functions)

Notes:
    - The `setting.ini` file must be present and correctly configured in the script directory.
    - Ensure all required input files (e.g., `.mrc`, `XDS.INP`) are available in the specified input directories.
    - Operations such as path modification and rollback rely on valid backup files being present.
    - GUI components are designed to be compatible with high-resolution displays.

Contact:
    - Lei Wang: lei.wang@su.se
    - Yinlin Chen: yinlin.chen@su.se

License:
    BSD 3-Clause Licence
"""

try:
    from .src import xds_input, image_io
    from .src.image_io import generate_pets
    from .src.util import *
except ImportError:
    from src import xds_input, image_io
    from src.image_io import (generate_pets)
    from src.util import *

import configparser
import os
import shutil
import sys
import threading

from PyQt5.QtCore import QTimer, Qt, QProcess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QFileDialog, QMessageBox
)

# Read configuration settings
script_dir = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'setting.ini'))

analysis_engine = config["XDSRunner"]["engine_hkl_analysis"]
path_filter = strtobool(config["General"]["path_filter"])

is_wsl = is_wsl()


# --- Main Tools Class ---
class Tools(QWidget):
    """
    A class representing the Tools GUI interface for managing crystallographic operations.

    The `Tools` class provides a graphical interface for performing various tasks within the
    crystallographic data processing workflow. It includes functionality for generating REDp
    files, creating PETS input files, rolling back XDS.INP files, modifying image paths, and
    batch operations on XDS files. The GUI components are designed to streamline user interactions
    and provide real-time feedback on task progress.

    Attributes:
        input_path (str): The current directory path being processed.
        thread (dict): Dictionary of active threads for different operations.
        process (QProcess): Process object for executing external scripts.
        animation_canvas (AnimationWidget): Real-time animation widget for REDp file generation.
        animation_canvas_pets (AnimationWidget): Real-time animation widget for PETS input generation.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_path = ""
        self.thread = {}
        self.process = QProcess(self)

        # Main vertical layout
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(20, 10, 10, 10)
        mainLayout.setSpacing(18)  # Use a bit more spacing between rows
        mainLayout.addSpacing(12)

        # Row 0: Label
        row0_layout = QHBoxLayout()
        row0_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row0_layout.addWidget(QLabel("1. Make REDp file based on FEI .mrc files."))
        mainLayout.addLayout(row0_layout)

        # Row 1: "Input folder" label, entry, "Browse", "Run", animation
        row1_layout = QHBoxLayout()
        row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row1_layout.addWidget(QLabel("Input folder:"))

        self.path_entry = QLineEdit()
        self.path_entry.setFixedWidth(500)
        row1_layout.addWidget(self.path_entry)

        redp_browse_button = QPushButton("Browse")
        redp_browse_button.clicked.connect(self.select_path)
        row1_layout.addWidget(redp_browse_button)

        run_redp_button = QPushButton("Run")
        run_redp_button.clicked.connect(self.load_path)
        row1_layout.addWidget(run_redp_button)

        self.animation_canvas = AnimationWidget()
        row1_layout.addWidget(self.animation_canvas)
        row1_layout.addStretch()
        mainLayout.addLayout(row1_layout)

        #
        # 2) PETS input
        #
        row2_layout = QHBoxLayout()
        row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row2_layout.addWidget(QLabel("2. Generate PETS input from FEI .mrc files."))
        mainLayout.addLayout(row2_layout)

        row3_layout = QHBoxLayout()
        row3_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row3_layout.addWidget(QLabel("Input folder:"))

        self.path_entry_pets = QLineEdit()
        self.path_entry_pets.setFixedWidth(500)
        row3_layout.addWidget(self.path_entry_pets)

        pets_browse_button = QPushButton("Browse")
        pets_browse_button.clicked.connect(self.select_path_pets)
        row3_layout.addWidget(pets_browse_button)

        self.overwrite_checkbox = QCheckBox("Overwrite Existing TIFF")
        row3_layout.addWidget(self.overwrite_checkbox)

        pets_run_button = QPushButton("Run")
        pets_run_button.clicked.connect(self.load_path_pets)
        row3_layout.addWidget(pets_run_button)

        self.animation_canvas_pets = AnimationWidget()
        row3_layout.addWidget(self.animation_canvas_pets)
        row3_layout.addStretch()
        mainLayout.addLayout(row3_layout)

        #
        # 3) Roll back XDS.INP
        #
        row4_layout = QHBoxLayout()
        row4_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row4_layout.addWidget(QLabel("3. Roll back XDS.INP to certain stage."))
        mainLayout.addLayout(row4_layout)

        row5_layout = QHBoxLayout()
        row5_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        P1_button = QPushButton("Back to P1 Stage")
        P1_button.clicked.connect(self.rollback_P1)
        row5_layout.addWidget(P1_button)
        cell_button = QPushButton("Back to Cell Stage")
        cell_button.clicked.connect(self.rollback_cell)
        row5_layout.addWidget(cell_button)
        refine_button = QPushButton("Back to Last Refine")
        refine_button.clicked.connect(self.rollback_refine)
        row5_layout.addWidget(refine_button)
        mainLayout.addLayout(row5_layout)

        #
        # 4) Change image path
        #
        row6_layout = QHBoxLayout()
        row6_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row6_layout.addWidget(QLabel("4. Change image path in XDS.INP (SMV .img only)"))
        mainLayout.addLayout(row6_layout)

        row7_layout = QHBoxLayout()
        row7_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        abs_path_button = QPushButton("Absolute Path")
        abs_path_button.clicked.connect(self.absolute_path)
        row7_layout.addWidget(abs_path_button)
        rel_path_button = QPushButton("Relative Path")
        rel_path_button.clicked.connect(self.relative_path)
        row7_layout.addWidget(rel_path_button)
        mainLayout.addLayout(row7_layout)

        #
        # 5) Batch operate
        #
        row8_layout = QHBoxLayout()
        row8_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row8_layout.addWidget(QLabel("5. Batch operate on XDS.INP files."))
        mainLayout.addLayout(row8_layout)

        row9_layout = QHBoxLayout()
        row9_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        delete_xds_button = QPushButton("Delete XDS")
        delete_xds_button.setStyleSheet("background-color: #f3e3e3;")
        delete_xds_button.clicked.connect(self.confirm_delete_xds)
        row9_layout.addWidget(delete_xds_button)
        mainLayout.addLayout(row9_layout)

        mainLayout.addWidget(QLabel("6. Other Tools"))
        row10_layout = QHBoxLayout()
        row10_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        view_lattice_button = QPushButton("View Lattice")
        view_lattice_button.clicked.connect(self.view_lattice)
        row10_layout.addWidget(view_lattice_button)
        mainLayout.addLayout(row10_layout)

        mainLayout.addStretch()

        #
        # Tooltips
        #
        self.path_entry.setToolTip("The linux path for generating REDp input file")
        redp_browse_button.setToolTip("Browse the linux path.")
        run_redp_button.setToolTip("Tidy-up FEI mrc and perform REDp input file generation.")
        self.path_entry_pets.setToolTip("Data path in linux system.")
        pets_browse_button.setToolTip("Browse the linux path.")
        self.overwrite_checkbox.setToolTip("Overwrite Existing Tiff file for PETS.")
        pets_run_button.setToolTip("Perform PETS conversion and PETS auto-workflow.")
        P1_button.setToolTip("Restore XDS.INP to the state before running with cell.")
        cell_button.setToolTip("Restore XDS.INP to the state before running refinement.")
        refine_button.setToolTip("Restore XDS.INP to the state to last refinement.")
        abs_path_button.setToolTip("Change image path in XDS.INP to absolute path.")
        rel_path_button.setToolTip("Change image path in XDS.INP to relative path.")
        delete_xds_button.setToolTip("CAUTION! It will delete all XDS.INP with corresponding result files!")

    def absolute_path(self):
        if self.input_path:
            print("Changing input paths to absolute...")
            xds_input.change_path_input(self.input_path, "absolute")
            QMessageBox.information(self.window(), "Caution", "The image path is updated successfully.")

    def relative_path(self):
        if self.input_path:
            print("Changing input paths to relative...")
            xds_input.change_path_input(self.input_path, "relative")
            QMessageBox.information(self.window(), "Caution", "The image path is updated successfully.")

    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_entry.setText(path)
            self.input_path = path

    def load_path(self):
        input_path = self.path_entry.text()
        if input_path and os.path.isdir(input_path):
            self.input_path = input_path
            self.animation_canvas.startAnimation()
            self.thread["conversion_thread_redp"] = threading.Thread(
                target=image_io.generate_redp, args=(input_path,)
            )
            self.thread["conversion_thread_redp"].start()
            QTimer.singleShot(100, self.check_redp_thread)

    def check_redp_thread(self):
        t = self.thread.get("conversion_thread_redp")
        if t and t.is_alive():
            QTimer.singleShot(100, self.check_redp_thread)
        else:
            self.animation_canvas.stopAnimation()

    def rollback_P1(self):
        if not self.input_path:
            print("Input path not set.")
            return
        reply = QMessageBox.question(
            self.window(), "Warning",
            "Warning! Do you want to Rollback File to P1 stage?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            xds_files = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
            for xds_path in xds_files:
                backup_path = os.path.join(os.path.dirname(xds_path), "BACKUP-P1")
                if os.path.isfile(backup_path):
                    shutil.copy(backup_path, xds_path)
                    print(f"Copied {backup_path} to {xds_path}")

    def rollback_cell(self):
        if not self.input_path:
            print("Input path not set.")
            return
        reply = QMessageBox.question(
            self.window(), "Warning",
            "Warning! Do you want to Rollback File to Cell stage?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            xds_files = find_files(self.input_path, "XDS.INP", path_filter=path_filter)
            for xds_path in xds_files:
                backup_cell_path = os.path.join(os.path.dirname(xds_path), "BACKUP-CELL")
                backup_P1_path = os.path.join(os.path.dirname(xds_path), "BACKUP-P1")
                if os.path.isfile(backup_cell_path):
                    shutil.copy(backup_cell_path, xds_path)
                    print(f"Copied {backup_cell_path} to {xds_path}")
                elif os.path.isfile(backup_P1_path):
                    shutil.copy(backup_P1_path, xds_path)
                    print(f"Copied {backup_P1_path} to {xds_path}")

    def rollback_refine(self):
        if not self.input_path:
            print("Input path not set.")
            return
        reply = QMessageBox.question(
            self.window(), "Warning",
            "Warning! Do you want to Rollback File to Last Refine?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            xds_files = find_files(self.input_path, "XDS.INP")
            for xds_path in xds_files:
                backup_path = os.path.join(os.path.dirname(xds_path), "BACKUP-REFINE")
                if os.path.isfile(backup_path):
                    shutil.copy(backup_path, xds_path)
                    print(f"Copied {backup_path} to {xds_path}")

    def select_path_pets(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_entry_pets.setText(path)

    def load_path_pets(self):
        input_path = self.path_entry_pets.text()
        if input_path and os.path.isdir(input_path):
            self.animation_canvas_pets.startAnimation()
            self.thread["conversion_thread_pets"] = threading.Thread(
                target=generate_pets.run_pets_function,
                args=(input_path, self.overwrite_checkbox.isChecked())
            )
            self.thread["conversion_thread_pets"].start()
            QTimer.singleShot(100, self.check_pets_thread)

    def check_pets_thread(self):
        t = self.thread.get("conversion_thread_pets")
        if t and t.is_alive():
            QTimer.singleShot(100, self.check_pets_thread)
        else:
            self.animation_canvas_pets.stopAnimation()

    def confirm_delete_xds(self):
        if not self.input_path:
            print("Input path not set.")
            return
        reply = QMessageBox.question(
            self.window(), "Warning",
            "Warning! All XDS files will be deleted. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.run_delete_xds_script()

    def run_delete_xds_script(self):
        if not self.input_path:
            print("Input path not set.")
            return
        self.thread["delete_xds"] = threading.Thread(
            target=xds_input.delete_xds, args=(self.input_path,)
        )
        self.thread["delete_xds"].start()

    def view_lattice(self):
        if not self.input_path:
            print("Input path not set.")
            return
        command = sys.executable
        arguments = [os.path.join(script_dir, "src", "visualisation", "recip_viewer_GUI.py"), "-f", self.input_path]
        self.process.start(command, arguments)
