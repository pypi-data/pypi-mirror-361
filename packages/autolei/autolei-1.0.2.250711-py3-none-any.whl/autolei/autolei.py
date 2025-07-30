if __name__ == "__main__" and __package__ is None:
    __package__ = "autolei"

import warnings

warnings.filterwarnings(action='ignore', category=FutureWarning)
warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.filterwarnings(action='ignore', category=RuntimeWarning)

from matplotlib import MatplotlibDeprecationWarning

warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)

import configparser
import sys
from multiprocessing import Process

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QMessageBox,
)
from PyQt5.QtGui import QFont

try:
    from .src.util import *
    from .realtime import RealTime
    from .tool import Tools
    from .autolei_core import (
        Input,
        XDSRunner,
        UnitCellCorr,
        XDSRefine,
        MergeData,
        Cluster_Output
    )
except ImportError:
    from src.util import *
    from realtime import RealTime
    from tool import Tools
    from autolei_core import (
        Input,
        XDSRunner,
        UnitCellCorr,
        XDSRefine,
        MergeData,
        Cluster_Output
    )

script_dir = os.path.dirname(__file__)
# Read configuration settings
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'setting.ini'))


class AutoLei(QMainWindow):
    """
    A class representing the main GUI application for AutoLEI using Qt6.

    AutoLEI is an interactive application designed to facilitate dataset
    processing, unit cell refinement, merging of data, and various other
    scientific computations. This class handles the initialization and
    configuration of the GUI, including the creation of multiple tabs
    for different functionalities.

    Attributes:
        notebook (QTabWidget): The main tabbed interface for the application.
        dataset_counts (int): Number of datasets currently loaded.
        input_path (str or None): The current directory path being processed.
        pages (dict): Dictionary of instantiated pages for different functionalities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Title
        self.bypassCloseConfirmation = False
        self.setWindowTitle("AutoLEI 1.0.2")

        # Adjust scaling factor
        window_width = 1200
        window_height = 900
        self.resize(window_width, window_height)

        # Central widget + layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName("customWidget")

        layout = QVBoxLayout(central_widget)
        central_widget.setLayout(layout)

        # Now the style sheet will match the widget with the object name.
        central_widget.setStyleSheet("#customWidget { background-color: #e5e5e5; }")

        # Set a default font for the application
        default_font = QFont()
        default_font.setFamily("Liberation Sans")
        default_font.setPointSize(14)
        QApplication.setFont(default_font)

        # QTabWidget to mimic the old Notebook
        self.notebook = QTabWidget()
        layout.addWidget(self.notebook)
        with open(os.path.join(script_dir, "qt/style.qss"), "r") as file:
            style = file.read()
        self.notebook.setStyleSheet(style)

        # Initialization
        self.dataset_counts = 0
        self.input_path = None
        self.pages = {}

        if not self.check_XDS():
            # Schedule the window to close after the event loop starts.
            QTimer.singleShot(0, self.close)

        # Prepare page names
        page_name_mapping = {
            "Input": "Input",
            "XDSRunner": "XDSRunner",
            "UnitCellCorr": "CellCorr",
            "XDSRefine": "XDSRefine",
            "MergeData": "DataMerge",
            "Cluster_Output": "Cluster&&Output",
            "Tools": "Expert",
            "RealTime": "RealTime",
        }

        page_classes = [
            Input,
            XDSRunner,
            UnitCellCorr,
            XDSRefine,
            MergeData,
            Cluster_Output,
            Tools,
            RealTime
        ]
        #
        # Instantiate each page/class and add to the tab widget
        for F in page_classes:
            page = F()  # In Qt, we usually do not pass 'parent' to custom pages
            self.pages[F.__name__] = page
            # Use the mapping to set the page name
            page_name = page_name_mapping.get(F.__name__, F.__name__)
            self.notebook.addTab(page, page_name)

    def set_input_path(self, path: str):
        """
        Set the input path and update pages accordingly.
        """
        self.input_path = path
        for page_name, page in self.pages.items():
            if hasattr(page, 'input_path'):
                page.input_path = path
        os.chdir(path)
        self.update_title()

        try:
            self.pages["XDSRefine"].range_combo.setCurrentIndex(0)
            self.pages["Cluster_Output"].p4p_option_menu.setCurrentIndex(0)
        except KeyError:
            pass

        # If 'merge' dir exists, update that page's path dictionary
        if os.path.isdir(os.path.join(path, "merge")):
            if "Cluster_Output" in self.pages:
                self.pages["Cluster_Output"].update_path_dict(output=False)

        # Check for realtime/online files
        if (os.path.isfile(os.path.join(path, "online.json")) or
                os.path.isfile(os.path.join(path, "realtime.json"))):
            if "RealTime" in self.pages:
                self.pages["RealTime"].update_display_initial()

    def update_title(self):
        """
        Update the application title to reflect the current input path
        and dataset count.
        """
        if self.input_path:
            self.setWindowTitle(
                f"AutoLEI 1.0.2 - {self.input_path} - {self.dataset_counts} datasets"
            )
        else:
            self.setWindowTitle("AutoLEI 1.0.2")

    def closeEvent(self, event):
        """
        Override the window close event to confirm with the user.
        """
        if getattr(self, '_bypassConfirmation', False):
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to close the window? Realtime monitor will disconnect.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Terminate realtime process if running
            if "RealTime" in self.pages:
                self.pages["RealTime"].stop_running(output=False)
            event.accept()
        else:
            event.ignore()

    def check_XDS(self) -> bool:
        """
        Check if the XDS program is in the system path (Linux only).
        Returns True if XDS is available or the user wishes to continue,
        False if the user cancels.
        """
        if sys.platform.startswith("linux") and not shutil.which("xds"):
            reply = QMessageBox.question(
                self,
                "Warning",
                "XDS not found in your system PATH! Do you wish to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                # Set flag to bypass the confirmation dialog on close
                self._bypassConfirmation = True
                return False
        return True


def start_gui() -> None:
    """
    Start the AutoLEI GUI application using Qt6.
    """
    app = QApplication(sys.argv)
    auto_lei = AutoLei()
    auto_lei.show()
    app.exec()


def main() -> None:
    """
    Main entry point for the AutoLEI application.
    """
    print("Report bug: \nlei.wang@su.se\nyinlin.chen@su.se\n")
    print("AutoLEI version 1.0.2, build date 2025-07-11")
    print("Welcome using AutoLEI!\n")
    os.environ["QT_SCALE_FACTOR"] = str(1.0)
    # Run the GUI in a separate process
    gui_process = Process(target=start_gui)
    gui_process.start()
    gui_process.join()


def setting():
    """
    Open the AutoLEI settings file for editing.
    """
    print("You will change the setting file of AutoLEI.")
    setting_path = os.path.join(os.path.dirname(__file__), 'setting.ini')
    subprocess.run(['nano', setting_path])


def add_instrument(file_name: str) -> None:
    """
    Add an instrument profile to the AutoLEI instrument directory.
    """
    src = file_name
    if not os.path.isfile(src):
        print(f"File {src} does not exist.")
        return
    dest_dir = os.path.join(os.path.dirname(__file__), 'instrument_profile')
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    dest = os.path.join(dest_dir, os.path.basename(file_name))
    shutil.copyfile(src, dest)
    print(f"Copied {src} to AutoLEI Instrument Files.")


if __name__ == "__main__":
    main()
