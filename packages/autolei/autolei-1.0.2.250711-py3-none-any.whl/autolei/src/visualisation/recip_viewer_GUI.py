import argparse
import os
import sys

import numpy as np
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QGridLayout,
    QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QGroupBox, QDialog, QWidget, QLabel, QLineEdit, QHBoxLayout
)
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D

from autolei.src.util import natural_sort_key, ComboBox, SegmentedControl, LabeledSlider
from recip_viewer import (plot_slice_reciprocal_space, slice_rule_dict,
                          read_hkl, transform_points, plot_reciprocal_space_3D)

script_dir = os.path.dirname(__file__)


def format_angle(angle: float) -> str:
    """
    Convert the given angle (float) to a string with:
      - 0 decimals if exactly 90.00 or 120.00
      - else 2 decimals
    """
    angle_rounded = round(angle, 2)
    if abs(angle_rounded - 90) < 1e-9:
        return "90"
    elif abs(angle_rounded - 120) < 1e-9:
        return "120"
    else:
        return f"{angle_rounded:.2f}"


class RecipViewer(QMainWindow):
    def __init__(self, input_path=None, dataset=None):
        super().__init__()
        self._3d_azim = 0
        self._3d_elev = 0
        self.setWindowTitle("Reciprocal Space Viewer")
        self.resize(1200, 900)
        font_main = QFont("Liberation Sans", 14)
        QApplication.setFont(font_main)
        self._last_plot_mode = None

        # Variables
        self.xds_path = ""
        self.selected_pattern = "--"
        self.resolution = 0.8
        self.show_grid = True
        self.spot_size = 5.5
        self.linewidth = 0.15
        self.min_reso = 0.8
        self.max_reso = 30
        self.spot_size_3d = 30
        self.intensity_percentile = 30.0
        self.bkg_black = False
        self.show_label = True
        self.show_axis = True

        self.updating = False

        # Cache for reading data
        self.last_xds_path = None
        self.cached_data = None

        # Dataset selection variables
        self.dataset_dict = {}  # mapping display name -> (type, relative path)

        # Create main widget and layout
        main_widget = QWidget()
        if os.path.isfile(os.path.join(script_dir, "../../qt/style.qss")):
            with open(os.path.join(script_dir, "../../qt/style.qss"), "r") as file:
                style = file.read()
        else:
            with open(os.path.join(script_dir, "style.qss"), "r") as file:
                style = file.read()
        main_widget.setStyleSheet(style)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Top frame: XDS path and dataset selection
        top_widget = QWidget()
        top_layout = QGridLayout()
        top_widget.setLayout(top_layout)

        # XDS Path
        label_path = QLabel("XDS Path:")
        label_path.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        top_layout.addWidget(label_path, 0, 0)

        self.path_line_edit = QLineEdit()
        top_layout.addWidget(self.path_line_edit, 0, 1)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_path)
        top_layout.addWidget(browse_button, 0, 2)

        # Dataset selection
        label_dataset = QLabel("Select Dataset:")
        label_dataset.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        top_layout.addWidget(label_dataset, 1, 0)

        self.dataset_combo = ComboBox()
        self.dataset_combo.addItem("--")
        self.dataset_combo.currentIndexChanged.connect(self.plot)
        top_layout.addWidget(self.dataset_combo, 1, 1, 1, 2)

        main_layout.addWidget(top_widget)

        # Middle frame: left (plot) and right (controls)
        middle_widget = QWidget()
        middle_layout = QHBoxLayout()
        middle_widget.setLayout(middle_layout)
        main_layout.addWidget(middle_widget, stretch=1)

        # Left: Matplotlib figure
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        middle_layout.addWidget(left_widget, stretch=10)

        self.figure, self.ax = plt.subplots(figsize=(6, 6), facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        left_layout.addWidget(self.canvas)

        # Right: Controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_layout.setSpacing(8)
        middle_layout.addWidget(right_widget, stretch=4)

        # Unit cell info
        unit_cell_title = QLabel("Unit Cell:")
        unit_cell_title.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        right_layout.addWidget(unit_cell_title)

        self.unit_cell_line1 = QLabel("a= -- Å, b= -- Å, c= -- Å")
        right_layout.addWidget(self.unit_cell_line1)
        self.unit_cell_line2 = QLabel("α= --°, β= --°, γ= --°")
        right_layout.addWidget(self.unit_cell_line2)
        right_layout.addSpacing(8)

        row3_frame = QHBoxLayout()
        right_layout.addLayout(row3_frame)

        self.mode_switch_button = SegmentedControl(["Slice", "3DViewer"], default_index=1)
        self.mode_switch_button.buttonGroup.buttonClicked.connect(self.button_switch)
        row3_frame.addWidget(self.mode_switch_button)
        row3_frame.addStretch()
        right_layout.addSpacing(8)

        # Pattern selection
        self.pattern_label = QLabel("Select Pattern:")
        self.pattern_label.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        right_layout.addWidget(self.pattern_label)

        self.pattern_combo = ComboBox()
        self.pattern_combo.addItem("--")
        for key in slice_rule_dict.keys():
            self.pattern_combo.addItem(key)
        self.pattern_combo.currentIndexChanged.connect(self.pattern_changed)
        right_layout.addWidget(self.pattern_combo)

        # Recip 3D Viewer
        self.td_params_title = QLabel("Mode:")
        self.td_params_title.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        right_layout.addWidget(self.td_params_title)

        # Parameters area
        self.td_mode_widget = QWidget()
        td_mode_layout = QVBoxLayout()
        self.td_mode_widget.setLayout(td_mode_layout)
        right_layout.addWidget(self.td_mode_widget)

        # 3D Viewer Mode -1
        row3d_1_frame = QHBoxLayout()
        td_mode_layout.addWidget(QLabel("Plot Data from:"))
        td_mode_layout.addLayout(row3d_1_frame)
        self.data_switch_button = SegmentedControl(["Index", "Index&&HKL"], default_index=0)
        self.data_switch_button.buttonGroup.buttonClicked.connect(self.plot)
        row3d_1_frame.addWidget(self.data_switch_button)
        row3d_1_frame.addStretch()
        td_mode_layout.addSpacing(4)

        row3d_4_frame = QHBoxLayout()
        td_mode_layout.addWidget(QLabel("Show Intensity:"))
        td_mode_layout.addLayout(row3d_4_frame)
        self.intensity_switch_button = SegmentedControl(["Yes", "No"], default_index=1)
        self.intensity_switch_button.buttonGroup.buttonClicked.connect(self.plot)
        row3d_4_frame.addWidget(self.intensity_switch_button)
        row3d_4_frame.addStretch()
        td_mode_layout.addSpacing(4)

        row3d_2_frame = QHBoxLayout()
        td_mode_layout.addWidget(QLabel("Show Points of:"))
        td_mode_layout.addLayout(row3d_2_frame)
        self.point_switch_button = SegmentedControl(["All", "Indexed", "Unindexed"], default_index=0)
        self.point_switch_button.buttonGroup.buttonClicked.connect(self.plot)
        row3d_2_frame.addWidget(self.point_switch_button)
        row3d_2_frame.addStretch()
        td_mode_layout.addSpacing(4)

        row3d_3_frame = QHBoxLayout()
        td_mode_layout.addWidget(QLabel("View Direction as:"))
        td_mode_layout.addLayout(row3d_3_frame)
        self.view_switch_button = SegmentedControl(["None", "a", "b", "c"], default_index=0)
        self.view_switch_button.buttonGroup.buttonClicked.connect(self.plot)
        row3d_3_frame.addWidget(self.view_switch_button)
        row3d_3_frame.addStretch()

        self.td_mode_widget.setVisible(False)

        right_layout.addSpacing(8)

        # Parameters title
        self.params_title = QLabel("Parameters:")
        self.params_title.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        right_layout.addWidget(self.params_title)

        # Parameters area
        self.params_widget = QWidget()
        params_layout = QVBoxLayout()
        self.params_widget.setLayout(params_layout)
        right_layout.addWidget(self.params_widget)

        # Create sliders using our LabeledSlider widget
        # Resolution: slider from 4.0 down to 0.6; note: lower resolution value gives higher radius (1/resolution)
        self.slider_resolution = LabeledSlider("Resolution:", 0.4, 4.0, 0.01, self.resolution)
        self.slider_resolution.value_changed.connect(self.plot)
        params_layout.addWidget(self.slider_resolution)
        params_layout.addSpacing(8)

        # Spot Size slider: 1 to 20
        self.slider_spot = LabeledSlider("Spot Size:", 1, 20, 0.01, self.spot_size)
        self.slider_spot.value_changed.connect(self.plot)
        params_layout.addWidget(self.slider_spot)
        params_layout.addSpacing(8)

        # Line Width slider: 0.05 to 0.7
        self.slider_linewidth = LabeledSlider("Line Width:", 0.05, 0.7, 0.01, self.linewidth)
        self.slider_linewidth.value_changed.connect(self.plot)
        params_layout.addWidget(self.slider_linewidth)
        params_layout.addSpacing(8)

        # Intensity Percentile slider: 0 to 95
        self.slider_intensity = LabeledSlider("Contrast:", 0, 95, 0.01, self.intensity_percentile)
        self.slider_intensity.value_changed.connect(self.plot)
        params_layout.addWidget(self.slider_intensity)
        params_layout.addSpacing(8)

        self.params_widget_3d = QWidget()
        params_layout_3d = QVBoxLayout()
        self.params_widget_3d.setLayout(params_layout_3d)
        right_layout.addWidget(self.params_widget_3d)

        # Create sliders using our LabeledSlider widget
        # Resolution: slider from 4.0 down to 0.6; note: lower resolution value gives higher radius (1/resolution)
        self.slider_min_reso = LabeledSlider("Min Reso.:", 0.4, 1.5, 0.02, self.min_reso)
        self.slider_min_reso.value_changed.connect(self.plot)
        params_layout_3d.addWidget(self.slider_min_reso)
        params_layout_3d.addSpacing(8)

        # Line Width slider: 0.05 to 0.7
        self.slider_max_reso = LabeledSlider("Max Reso.:", 1.5, 35, 0.5, self.max_reso)
        self.slider_max_reso.value_changed.connect(self.plot)
        params_layout_3d.addWidget(self.slider_max_reso)
        params_layout_3d.addSpacing(8)

        # Spot Size slider: 1 to 20
        self.slider_spot_3d = LabeledSlider("Spot Size:", 20, 100, 5, self.spot_size_3d)
        self.slider_spot_3d.value_changed.connect(self.plot)
        params_layout_3d.addWidget(self.slider_spot_3d)
        params_layout_3d.addSpacing(8)

        # Additional Options in a GroupBox
        self.options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.options_group.setLayout(options_layout)
        right_layout.addWidget(self.options_group)

        self.checkbox_axis = QCheckBox("Show Axes")
        self.checkbox_axis.setChecked(self.show_axis)
        self.checkbox_axis.stateChanged.connect(self.plot)
        options_layout.addWidget(self.checkbox_axis)

        self.checkbox_grid = QCheckBox("Show Grid")
        self.checkbox_grid.setChecked(self.show_grid)
        self.checkbox_grid.stateChanged.connect(self.plot)
        options_layout.addWidget(self.checkbox_grid)

        self.checkbox_bkg = QCheckBox("Background Black")
        self.checkbox_bkg.setChecked(self.bkg_black)
        self.checkbox_bkg.stateChanged.connect(self.plot)
        options_layout.addWidget(self.checkbox_bkg)

        self.checkbox_label = QCheckBox("Show Label")
        self.checkbox_label.setChecked(self.show_label)
        self.checkbox_label.stateChanged.connect(self.plot)
        options_layout.addWidget(self.checkbox_label)

        # Spacer
        options_layout.addStretch()
        right_layout.setSpacing(10)

        # Save Plot button
        save_button = QPushButton("Save Plot")
        save_button.clicked.connect(self.save_plot)
        right_layout.addWidget(save_button)

        # Stretch at end so controls are at top
        right_layout.addStretch()

        # Initial blank plot
        self.draw_blank_plot("Please load a work path and \n select a dataset.")

        if input_path:
            self.set_path(input_path)
            if dataset and dataset in self.dataset_dict:
                self.dataset_combo.setCurrentText(dataset)

        self.mode_switch_button.buttonGroup.button(1).click()

    def pattern_changed(self):
        self.selected_pattern = self.pattern_combo.currentText()
        self.plot()

    def draw_blank_plot(self, message=""):
        self.ax.clear()
        self.ax.set_axis_off()

        if isinstance(self.ax, Axes3D):
            # For a 3D Axes, we can use text2D() to place text in 2D coordinates (like a HUD).
            self.ax.text2D(
                0.5, 0.5, message,
                transform=self.ax.transAxes,
                ha='center', va='center',
                fontsize=16, color='blue'
            )
        else:
            # For 2D Axes, the usual text() with transform=ax.transAxes works fine.
            self.ax.text(
                0.5, 0.5, message,
                ha='center', va='center',
                transform=self.ax.transAxes,
                fontsize=16, color='blue'
            )

        self.canvas.draw()

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select XDS Path")
        if path:
            self.set_path(path)

    def button_switch(self, button):
        btn_id = self.mode_switch_button.buttonGroup.id(button)
        if btn_id == 0:
            self.td_mode_widget.setVisible(False)
            self.td_params_title.setVisible(False)
            self.params_widget_3d.setVisible(False)
            self.pattern_label.setVisible(True)
            self.pattern_combo.setVisible(True)
            self.params_widget.setVisible(True)
            self.options_group.setVisible(True)
        elif btn_id == 1:
            self.pattern_label.setVisible(False)
            self.pattern_combo.setVisible(False)
            self.params_widget.setVisible(False)
            self.options_group.setVisible(False)
            self.td_mode_widget.setVisible(True)
            self.td_params_title.setVisible(True)
            self.params_widget_3d.setVisible(True)
        self.plot()

    def set_path(self, path):
        self.xds_path = path
        self.path_line_edit.setText(path)

        single_datasets = []
        merged_datasets = []

        for root, dirs, files in os.walk(path):
            rel_dir = os.path.relpath(root, path)
            if "SPOT.XDS" in files:
                single_datasets.append(rel_dir)
            if "all.HKL" in files:
                merged_datasets.append(rel_dir)

        single_datasets.sort(key=natural_sort_key)
        merged_datasets.sort(key=natural_sort_key)

        combo_values = ["--"]
        self.dataset_dict.clear()

        SINGLE_DATASET_HEADER = "Single Dataset"
        MERGED_DATA_HEADER = "Merged Data"

        if single_datasets:
            combo_values.append(SINGLE_DATASET_HEADER)
            combo_values.append("------")
            for sd in single_datasets:
                display_name = sd
                combo_values.append(display_name)
                self.dataset_dict[display_name] = ("S", sd)

        if merged_datasets:
            combo_values.append("    ")
            combo_values.append(MERGED_DATA_HEADER)
            combo_values.append("------")
            for md in merged_datasets:
                display_name = md
                combo_values.append(display_name)
                self.dataset_dict[display_name] = ("M", md)

        self.dataset_combo.clear()
        self.dataset_combo.addItems(combo_values)
        # Reset selection
        self.dataset_combo.setCurrentIndex(0)
        self.draw_blank_plot("Please select a dataset from the dropdown.")

    def read_data(self, dataset_file, mode=None):
        folder_dir = os.path.dirname(dataset_file)
        cell_info, reflection, origin = read_hkl(folder_dir, mode=mode)
        if "unit_cell" in cell_info and len(cell_info["unit_cell"]) == 6:
            a0, b0, c0, alpha0, beta0, gamma0 = cell_info["unit_cell"]
            self.unit_cell_line1.setText(f"a= {a0:.2f} Å, b= {b0:.2f} Å, c= {c0:.2f} Å")
            self.unit_cell_line2.setText(f"α= {format_angle(alpha0)}°, β= {format_angle(beta0)}°,"
                                         f" γ= {format_angle(gamma0)}°")
            # Build reciprocal cell
            a = np.array(cell_info["a_axis"])
            b = np.array(cell_info["b_axis"])
            c = np.array(cell_info["c_axis"])
            V = np.dot(a, np.cross(b, c))
            a_star = np.cross(b, c) / V
            b_star = np.cross(c, a) / V
            c_star = np.cross(a, b) / V
        else:
            self.unit_cell_line1.setText("a= -- Å, b= -- Å, c= -- Å")
            self.unit_cell_line2.setText("α= --°, β= --°, γ= --°")
            a_star = np.array([0, 0, 0])
            b_star = np.array([0, 0, 0])
            c_star = np.array([0, 0, 0])
        if len(reflection[0]) == 7:
            refls = transform_points(reflection, cell_info, a_star, b_star, c_star)
        else:
            refls = reflection
        self.cached_data = {"a_star": a_star,
                            "b_star": b_star,
                            "c_star": c_star,
                            "refls": refls,
                            "origin": origin
                            }
        self.last_xds_path = dataset_file

    def plot(self):
        if self.updating:
            return
        self.updating = True

        current_mode = self.mode_switch_button.currentText()  # "Slice" or "3DViewer"
        selection = self.dataset_combo.currentText().strip()

        # ---------------------------------------------------------------------
        # (A) Decide whether we must create a new Axes or just clear the old one
        # ---------------------------------------------------------------------
        if current_mode == "3DViewer":
            # If we are switching from "Slice" -> "3DViewer", create new 3D Axes
            if self._last_plot_mode != "3DViewer":
                self.figure.clear()
                self.ax = self.figure.add_subplot(111, projection='3d', proj_type='ortho')
            else:
                # Already in 3D mode, so just clear the existing Axes3D
                self.ax.cla()
        else:
            # We are going to do a 2D slice
            if self._last_plot_mode != "Slice":
                self.figure.clear()
                self.ax = self.figure.add_subplot(111)
            else:
                # Already in 2D mode, just clear it
                self.ax.cla()

        # ---------------------------------------------------------------------
        # (B) Validate dataset selection
        # ---------------------------------------------------------------------
        if selection in ("--", "Single Dataset", "Merged Data", "------", ""):
            self.draw_blank_plot("Please select a valid dataset.")
            self.updating = False
            self._last_plot_mode = current_mode
            return

        if selection not in self.dataset_dict:
            self.draw_blank_plot("Invalid selection.")
            self.updating = False
            self._last_plot_mode = current_mode
            return

        ds_type, ds_relpath = self.dataset_dict[selection]
        work_path = self.xds_path
        if not work_path or not os.path.exists(work_path):
            self.draw_blank_plot("Please load a valid work path.")
            self.updating = False
            self._last_plot_mode = current_mode
            return

        ds_full_folder = os.path.join(work_path, ds_relpath)
        if not os.path.isdir(ds_full_folder):
            self.draw_blank_plot("Invalid dataset folder.")
            self.updating = False
            self._last_plot_mode = current_mode
            return

        if ds_type == "S":
            dataset_file = os.path.join(ds_full_folder, "SPOT.XDS")
        else:
            dataset_file = os.path.join(ds_full_folder, "all.HKL")

        if not os.path.exists(dataset_file):
            self.draw_blank_plot(f"{os.path.basename(dataset_file)} not found.")
            self.updating = False
            self._last_plot_mode = current_mode
            return

        # ---------------------------------------------------------------------
        # (C) Actually read data if needed
        # ---------------------------------------------------------------------
        if current_mode == "Slice":
            # Possibly re-read data if it's new or if we changed the type
            if (
                    dataset_file != self.last_xds_path
                    or (
                    os.path.isfile(os.path.join(ds_full_folder, "XDS_ASCII.HKL"))
                    and self.cached_data
                    and self.cached_data["origin"] != "xds_ascii")
            ):
                try:
                    self.read_data(dataset_file)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to read data: {e}")
                    self.draw_blank_plot(f"{os.path.basename(dataset_file)} is not available.")
                    self.updating = False
                    self._last_plot_mode = current_mode
                    return

            if (
                    np.all(self.cached_data["a_star"] == 0)
                    or np.all(self.cached_data["b_star"] == 0)
                    or np.all(self.cached_data["c_star"] == 0)
            ):
                self.draw_blank_plot("Unit Cell information is needed.")
                self.updating = False
                self._last_plot_mode = current_mode
                return

            # (D) Get slice parameters
            pattern = self.pattern_combo.currentText()
            if pattern == "--":
                self.draw_blank_plot("Please select a pattern.")
                self.updating = False
                self._last_plot_mode = current_mode
                return

            try:
                res_val = self.slider_resolution.get_value()
                radius = 1.0 / res_val if abs(res_val) > 1e-9 else 9999.0
                spot_size = self.slider_spot.get_value()
                linewidth = self.slider_linewidth.get_value()
                intensity_percentile = self.slider_intensity.get_value()
                show_grid = self.checkbox_grid.isChecked()
                bkg_black = self.checkbox_bkg.isChecked()
                show_label = self.checkbox_label.isChecked()
                show_axes = self.checkbox_axis.isChecked()
            except Exception as e:
                QMessageBox.critical(self, "Input Error", f"Invalid input: {e}")
                self.updating = False
                self._last_plot_mode = current_mode
                return

            # (E) Plot slice
            data = self.cached_data
            try:
                plot_slice_reciprocal_space(
                    refls=data["refls"],
                    pattern=pattern,
                    basis_sets=(data["a_star"], data["b_star"], data["c_star"]),
                    show_grid=show_grid,
                    radius=radius,
                    intensity_percentile=intensity_percentile,
                    spot_size=spot_size,
                    linewidth=linewidth,
                    bkg_black=bkg_black,
                    show_label=show_label,
                    show_axes=show_axes,
                    ax=self.ax
                )
                self.ax.set_facecolor('white' if not bkg_black else 'black')
                self.canvas.draw()
            except Exception as e:
                QMessageBox.critical(self, "Plot Error", f"Failed to generate plot: {e}")
                self.updating = False
                self._last_plot_mode = current_mode
                return

            # Update your internal slider states as needed
            self.slider_resolution.set_value(res_val)
            self.slider_spot.set_value(spot_size)
            self.slider_linewidth.set_value(linewidth)
            self.slider_intensity.set_value(intensity_percentile)

        else:
            # 3D Viewer
            if self.cached_data is not None:
                origin_update_bool = (
                        (self.data_switch_button.currentText() == "Index&&HKL" and self.cached_data[
                            "origin"] == "index")
                        or
                        (self.data_switch_button.currentText() == "Index" and self.cached_data["origin"] == "xds_ascii")
                )
            else:
                origin_update_bool = False

            if dataset_file != self.last_xds_path or origin_update_bool:
                try:
                    self.read_data(dataset_file, mode=self.data_switch_button.currentText())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to read data: {e}")
                    self.draw_blank_plot(f"{os.path.basename(dataset_file)} is not available.")
                    self.updating = False
                    self._last_plot_mode = current_mode
                    return

            # (F) 3D plot
            data = self.cached_data
            fig, ax = plot_reciprocal_space_3D(
                s_vectors=data["refls"],
                a_star=data["a_star"],
                b_star=data["b_star"],
                c_star=data["c_star"],
                min_reso=self.slider_min_reso.get_value(),
                max_reso=self.slider_max_reso.get_value(),
                spot_size=self.slider_spot_3d.get_value(),
                show_intensity=(self.intensity_switch_button.currentText() == "Yes"),
                show_points=self.point_switch_button.currentText().lower(),
                view_direction=self.view_switch_button.currentText().lower(),
                ax=self.ax
            )
            self.canvas.draw()

        # (G) Done
        self._last_plot_mode = current_mode
        self.updating = False

    def save_plot(self):
        # Build sidebar URLs from folders under /mnt
        dialog = QFileDialog(self, "Save Plot As", "", "PNG Files (*.png);;All Files (*)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        sidebar_urls = []
        if os.path.exists('/mnt'):
            for folder in os.listdir('/mnt'):
                full_path = os.path.join('/mnt', folder)
                if os.path.isdir(full_path):
                    sidebar_urls.append(QUrl.fromLocalFile(full_path))

        # Create a QFileDialog instance instead of using the static method
        dialog = QFileDialog(self, "Save Plot As", "", "PNG Files (*.png);;All Files (*)")
        dialog.setOptions(QFileDialog.Option(0))  # Set empty options
        dialog.setSidebarUrls([QUrl.fromLocalFile(os.path.expanduser("~")), QUrl.fromLocalFile("/")]
                              + sidebar_urls[::-1])

        # Execute the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            save_path = dialog.selectedFiles()[0]
            # Append .png extension if needed
            if not os.path.splitext(save_path)[1]:
                save_path += ".png"
            try:
                self.figure.savefig(
                    save_path,
                    dpi=450,
                    bbox_inches='tight',
                    facecolor=self.figure.get_facecolor()
                )
                QMessageBox.information(self, "Save Successful", f"Plot saved to {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save plot: {e}")


def main():
    parser = argparse.ArgumentParser(description="RecipViewer GUI")
    parser.add_argument("-f", "--folder", type=str, default='',
                        help="Folder name (input path)")
    parser.add_argument("-d", "--dataset", type=str, default="",
                        help="Dataset name")
    parser.add_argument("-s", "--scale", type=str, default="1.0",
                        help="Scaling factor")
    args = parser.parse_args()

    os.environ["QT_SCALE_FACTOR"] = str(args.scale)
    app = QApplication(sys.argv)
    gui = RecipViewer(input_path=args.folder, dataset=args.dataset)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # app = QApplication(sys.argv)
    # gui = RecipViewer(input_path="/mnt/d/Work/ED/dbb01415", dataset="56/56_Bi_TATZ_MY_1/xds")
    # gui.show()
    # sys.exit(app.exec())
