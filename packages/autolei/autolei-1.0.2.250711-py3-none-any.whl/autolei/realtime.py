import hashlib
import json
import time

# Matplotlib for PyQt
import matplotlib
import mplcursors
import pandas as pd
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox, QPushButton, QVBoxLayout, QMessageBox, QDialog,
    QPlainTextEdit
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# -- If these are your own local imports, keep them as-is:
try:
    from .src import image_io, xds_input, xds_runner, xds_analysis, analysis_hkl, xds_cluster
    from .src.visualisation import html_report
    from .src.util import *
    from .src.symm_shelx.space_group_finder import DEFAULT_SGC
except ImportError:
    from src import image_io, xds_input, xds_runner, xds_analysis, analysis_hkl, xds_cluster
    from src.visualisation import html_report
    from src.util import *
    from src.symm_shelx.space_group_finder import DEFAULT_SGC

matplotlib.use("QtAgg")
spgfinder = DEFAULT_SGC


class RealTimeWorker(QThread):
    """
    A QThread-based worker that performs the old 'monitor_folder()' logic:
    - Continuously checks the input folder
    - Calls update_status_dict()
    - Runs data reduction if needed
    - Waits for user-specified intervals
    - Emits signals so the GUI can update safely in the main thread.
    """
    statusChanged = pyqtSignal(dict)  # Emitted when self.status_dict updates
    finishedSignal = pyqtSignal(str)  # Emitted when the thread finishes or is stopped
    logMessage = pyqtSignal(str)  # For debug messages, optionally shown in the GUI

    def __init__(self, input_path, name: str, cell, sg, reso_limit,
                 do_correct, beam_stop, p1_mode,
                 old_status_dict=None, strategy_dict=None,
                 parent=None):
        super().__init__(parent)
        self.realtime_json = ""
        self.input_path = input_path
        self.name = name
        self.cell = cell
        self.sg = sg
        self.reso_limit = reso_limit
        self.do_correct = do_correct
        self.beam_stop = beam_stop
        self.P1 = p1_mode

        # If old dict or strategy is given, store it, else empty
        self.status_dict = old_status_dict if old_status_dict else {}
        self.strategy_dict = strategy_dict if strategy_dict else {}

        self.run_bool = True  # Worker loop flag
        self.good_set = set()

    def run(self):
        """
        The main loop:
          1) Load strategy (if needed)
          2) Set up initial statuses
          3) Continuously scan the folder, update statuses, run data reduction
          4) Sleep cycle_time seconds each loop
          5) Stop when self.run_bool is set to False
        """
        # We load strategy here if not already loaded:
        strategy_path = os.path.join(self.input_path, "strategy.txt")
        if not self.strategy_dict and not os.path.isfile(strategy_path):
            self.write_default_strategy(strategy_path)
        elif not self.strategy_dict:
            with open(strategy_path, "r") as f:
                lines = f.readlines()
            self.strategy_dict = xds_input.extract_keywords(lines)

        # update initial status
        self.update_status_initial()

        # If name is not suitable or already used, rename:
        if (self.name in self.status_dict and self.status_dict[self.name]["status"] != "document") \
                or not is_suitable_linux_folder_name(self.name) or self.name == "RealTimeED":
            self.name = "realtime"
            os.makedirs(os.path.join(self.input_path, "realtime"), exist_ok=True)
            if "realtime" in self.status_dict:
                self.status_dict["realtime"]["status"] = "document"
            else:
                self.status_dict["realtime"] = {
                    "status": "document",
                    "input": {
                        "name": self.name,
                        "cell": self.cell,
                        "sg": self.sg,
                        "do_correct": self.do_correct,
                        "beam_stop": self.beam_stop,
                        "reso_limit": self.reso_limit
                    }
                }
        elif self.name not in self.status_dict:
            os.makedirs(os.path.join(self.input_path, self.name), exist_ok=True)
            self.status_dict[self.name] = {
                "status": "document",
                "input": {
                    "name": self.name,
                    "cell": self.cell,
                    "sg": self.sg,
                    "do_correct": self.do_correct,
                    "beam_stop": self.beam_stop,
                    "reso_limit": self.reso_limit
                }
            }
        elif self.name in self.status_dict:
            self.status_dict[self.name]["input"] = {
                "name": self.name,
                "cell": self.cell,
                "sg": self.sg,
                "do_correct": self.do_correct,
                "beam_stop": self.beam_stop,
                "reso_limit": self.reso_limit
            }

        if not os.path.exists(self.realtime_json):
            with open(self.realtime_json, 'w') as file:
                json.dump(self.status_dict, file, indent=4)

        monitor_folder = {
            f for f in self.status_dict.keys()
            if self.status_dict[f]["status"] in ["empty", "collecting"]
        }
        last_image_no = {folder: self.status_dict[folder]["image_no"] for folder in monitor_folder}
        last_check_time = {folder: time.time() for folder in monitor_folder}

        # Force a statusChanged signal so the GUI can do an immediate update
        self.statusChanged.emit(self.status_dict)

        cycle_time = int(self.strategy_dict.get("CYCLE_TIME", ["5"])[0])
        waiting_time = int(self.strategy_dict.get("WAITING_TIME", ["20"])[0])

        while self.run_bool:
            print("\rRealTimeWorker scanning folder...", end='', flush=True)

            self.status_dict = self.update_status_dict(self.status_dict)
            self.statusChanged.emit(self.status_dict)

            # Check for new collecting folders
            current_folders = set(self.status_dict.keys())
            new_folders = {
                folder for folder in current_folders
                if self.status_dict[folder]["status"] == "collecting"
            }
            new_list = []
            for folder in new_folders:
                if folder not in monitor_folder:
                    new_list.append(folder)
                    monitor_folder.add(folder)
                    last_image_no[folder] = self.status_dict[folder]["image_no"]
                    last_check_time[folder] = time.time()

            if new_list:
                msg = f"Found new collecting folders: {new_list}"
                self.logMessage.emit(msg)

            # Check if collecting -> collected
            collected_folders = []
            for folder in monitor_folder:
                if folder not in self.status_dict:
                    continue
                current_image_count = self.status_dict[folder]["image_no"]
                if self.status_dict[folder]["status"] == "collecting":
                    if current_image_count != last_image_no[folder]:
                        last_image_no[folder] = current_image_count
                        last_check_time[folder] = time.time()
                    elif (time.time() - last_check_time[folder] >= waiting_time
                          and current_image_count > 10):
                        self.status_dict[folder]["status"] = "collected"
                        collected_folders.append(folder)

            # remove them from monitor
            for folder in collected_folders:
                if folder in monitor_folder:
                    monitor_folder.remove(folder)

            # Now see if there's any "collected" or "transferred" or "ready" or "instamatic-ready"
            run_list = {
                self.status_dict[f]["folder"]: self.status_dict[f]["status"]
                for f in self.status_dict.keys()
                if self.status_dict[f]["status"] in [
                    "collected", "transferred", "ready", "instamatic-ready"
                ]
            }
            if run_list:
                self.run_data_reduction(run_list)

            if not self.P1:
                self.run_cluster()

            # Emit updated dict so main can refresh
            self.statusChanged.emit(self.status_dict)

            # Sleep
            time.sleep(cycle_time)

        # If we exit the while loop => done
        self.finishedSignal.emit("RealTime has stopped monitoring.")

    def stop(self):
        """Stop the loop."""
        with open(self.realtime_json, 'w') as file:
            json.dump(self.status_dict, file, indent=4)
        self.run_bool = False

    @staticmethod
    def write_default_strategy(strategy_file):
        """Writes a default strategy.txt if missing."""
        with open(strategy_file, "w") as f:
            f.write("! CYCLE_TIME, refresh time, default 5 s. \n")
            f.write("! WAITING_TIME, time waiting for real processing\n")
            f.write("! after folder is unchanged, default 10 s.\n")
            f.write(" CYCLE_TIME= 5\n")
            f.write(" WAITING_TIME= 20\n\n")
            f.write("! Available Filter for RUN_FILTER: CC12, ISA, REXP, RMEAS, RESOLUTION, VOLUME_DEV\n")
            f.write(" RUN_FILTER= CC12 > 85\n")
            f.write(" RUN_FILTER= ISA > 2\n")
            f.write(" RUN_FILTER= ISA < 50\n\n")
            f.write("! Available Filter for MERGE_FILTER: CC12, DISTANCE\n")
            f.write(" MERGE_FILTER= CC12 > 0\n\n\n")

    def update_status_initial(self):
        """Load or init realtime.json -> self.status_dict."""
        self.realtime_json = os.path.join(self.input_path, "realtime.json")
        if os.path.exists(self.realtime_json):
            with open(self.realtime_json, 'r') as file:
                self.status_dict = json.load(file)
        else:
            self.status_dict = {}
        # We'll call update_status_dict once
        self.update_status_dict(self.status_dict, initial=True)

    def update_status_dict(self, _status_dict: dict, initial: bool = False) -> dict:
        """
        Moved from RealTime.  We do NOT call any GUI methods here.
        Instead, we just update the dict. The GUI will update upon receiving signals.
        """
        backup_dict = _status_dict.copy()
        subfolders = {
            f for f in os.listdir(self.input_path)
            if os.path.isdir(os.path.join(self.input_path, f))
        }

        existing_folders = set(_status_dict.keys())
        non_existing = existing_folders - subfolders
        for folder in non_existing:
            del _status_dict[folder]

        # If any folder is marked "discard" but doesn't start with "!", revert to "ready"
        for folder in [f for f in _status_dict.keys()
                       if _status_dict[f].get("status") == "discard"]:
            if not folder.startswith("!"):
                _status_dict[folder]["status"] = "ready"

        # Merge iteration logic if not initial
        if not initial and self.name in _status_dict:
            pattern = re.compile(r'iter(\d+)')
            numbers = []
            try:
                resolution = float(self.reso_limit)
            except ValueError:
                resolution = 1.0

            merged_dir = os.path.join(self.input_path, self.name)
            if os.path.isdir(merged_dir):
                for _item in os.listdir(merged_dir):
                    if os.path.isdir(os.path.join(merged_dir, _item)):
                        match = pattern.match(_item)
                        if match:
                            numbers.append(int(match.group(1)))
                for num in sorted(numbers):
                    all_hkl = os.path.join(merged_dir, f"iter{num}", "all.HKL")
                    cluster_dir = os.path.join(merged_dir, f"iter{num}")
                    if os.path.isfile(all_hkl):
                        _status_dict[self.name][f"iter{num}"] = xds_analysis.extract_cluster_result(
                            cluster_dir, reso=resolution
                        )

        # Exclude finished from subfolders if not initial
        if not initial:
            finished_folder = {
                f for f in _status_dict.keys()
                if _status_dict[f]["status"] in ["discard", "good", "bad", "failed", "document"]
            }
            subfolders -= finished_folder
        else:
            finished_folder = {
                f for f in _status_dict.keys()
                if _status_dict[f]["status"] == "document"
            }
            for folder in finished_folder:
                if folder != self.name and folder in _status_dict:
                    _status_dict[folder]["status"] = "empty"
            if self.name in subfolders:
                subfolders.remove(self.name)

        for subfolder in sorted(subfolders):
            folder_path = os.path.join(self.input_path, subfolder)
            # if "!" => discard
            if subfolder.startswith("!"):
                _status_dict[subfolder] = {
                    "status": "discard", "folder": folder_path
                }
                continue

            if subfolder not in _status_dict:
                _status_dict[subfolder] = {
                    "status": "empty", "folder": folder_path,
                    "MD5": "", "image_no": 0, "statistics": {}
                }

            mrc_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".mrc")]
            cRED_file = os.path.join(folder_path, "cRED_log.txt")
            image_no = len(mrc_files)
            mrc_md5 = ""
            statistics = {}

            if mrc_files:
                mrc_md5 = self.get_md5(os.path.join(folder_path, mrc_files[0]))
                img_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".img")]
                # Decide status
                if len(img_files) == 0:
                    folder_status = "collecting"
                elif len(img_files) >= len(mrc_files) - 5:
                    xds_folder = os.path.join(folder_path, 'xds')
                    if os.path.exists(xds_folder):
                        init_lp = os.path.join(xds_folder, 'INIT.LP')
                        hkl_file = os.path.join(xds_folder, 'XDS_ASCII.HKL')
                        if os.path.exists(init_lp) and os.path.exists(hkl_file):
                            statistics = xds_analysis.extract_run_result(xds_folder)
                            if self.meet_criteria(statistics):
                                folder_status = "good"
                            else:
                                folder_status = "bad"
                        elif os.path.exists(init_lp):
                            folder_status = "failed"
                            statistics["mtime"] = os.path.getmtime(init_lp)
                        else:
                            folder_status = "ready"
                    else:
                        folder_status = "transferred"
                else:
                    folder_status = "collected"
            elif os.path.isfile(cRED_file) and os.path.isdir(os.path.join(folder_path, 'SMV', 'data')):
                # Instamatic approach
                mrc_md5 = self.get_md5(cRED_file)
                xds_folder = os.path.join(folder_path, 'SMV')
                data_folder = os.path.join(xds_folder, 'data')
                img_files = [f for f in os.listdir(data_folder) if f.lower().endswith(".img")]
                img_collect_no = xds_input.read_cRED_log(cRED_file)
                init_lp = os.path.join(xds_folder, 'INIT.LP')
                hkl_file = os.path.join(xds_folder, 'XDS_ASCII.HKL')
                if len(img_files) >= img_collect_no - 1:
                    if os.path.exists(init_lp) and os.path.exists(hkl_file):
                        statistics = xds_analysis.extract_run_result(xds_folder)
                        if self.meet_criteria(statistics):
                            folder_status = "good"
                        else:
                            folder_status = "bad"
                    elif os.path.exists(init_lp):
                        folder_status = "failed"
                        statistics["mtime"] = os.path.getmtime(init_lp)
                    else:
                        folder_status = "instamatic-ready"
                else:
                    image_no = len(img_files)
                    folder_status = "instamatic-collecting"
            else:
                folder_status = "empty"

            _status_dict[subfolder]["status"] = folder_status
            _status_dict[subfolder]["folder"] = folder_path
            _status_dict[subfolder]["MD5"] = mrc_md5
            _status_dict[subfolder]["image_no"] = image_no
            _status_dict[subfolder]["statistics"] = statistics

        if {k: _status_dict[k] for k in sorted(_status_dict, key=natural_sort_key)} != backup_dict:
            with open(self.realtime_json, 'w') as file:
                json.dump(_status_dict, file, indent=4)
        return {k: _status_dict[k] for k in sorted(_status_dict, key=natural_sort_key)}

    def meet_criteria(self, statistics: dict) -> bool:
        """Same as your original code, but never calls GUI."""
        rules = self.strategy_dict.get("RUN_FILTER", [])
        cc12 = statistics.get("cc12_reso", statistics.get("CC1/2", 0))
        isa = statistics.get("ISa_model", 0)
        resolution = statistics.get("resolution", 99)
        rexp = statistics.get("rexp", statistics.get("R_exp", 0))
        rmeas = statistics.get("rmeas", statistics.get("R_meas", 0))

        vol_dev = 0
        if self.cell and "VOLUME_DEV" in rules:
            try:
                vol = statistics["volume"]
                # parse cell
                if ", " in self.cell:
                    cell_split = self.cell.split(", ")
                else:
                    cell_split = self.cell.split()
                cell_split = [float(i) for i in cell_split]
                std_vol = analysis_hkl.unit_cell_volume(*cell_split)
                vol_dev = abs(vol - std_vol) / std_vol * 100
            except Exception as e:
                print("volume deviation error:", e)
                vol_dev = 0

        local_vars = {
            'CC12': cc12,
            'ISA': isa,
            'RESOLUTION': resolution,
            'REXP': rexp,
            'RMEAS': rmeas,
            'VOLUME_DEV': vol_dev,
        }

        for rule in rules:
            try:
                if not eval(rule, {}, local_vars):
                    return False
            except Exception as e:
                print("Meet criteria error:", e)
                return False
        return True

    def run_data_reduction(self, run_dict: dict):
        """
        The logic that processes "collected" -> "transferred" -> "ready" -> run xds, then merges if needed.
        We never call GUI methods here. We do the real work, and rely on signals for updates.
        """
        # 1) Convert if "collected"
        for key, value in run_dict.items():
            if value == "collected":
                self.logMessage.emit(f"Converting {key} MRC->SMV")
                self.convert_image(key)
                run_dict[key] = "transferred"

        # 2) Write and correct XDS
        for key, value in run_dict.items():
            if value == "transferred":
                xds_input.write_xds_file(key, os.path.join(self.input_path, "Input_parameters.txt"))
                if self.do_correct:
                    xds_input.correct_inputs(key)
                if self.beam_stop:
                    image_io.beam_stop_calculate(key)
                else:
                    image_io.centre_calculate(key)
                if not self.P1:
                    xds_input.cell_correct_online(os.path.join(key, "xds", "XDS.INP"), self.cell, self.sg)
                run_dict[key] = "ready"
            elif value == "instamatic-ready":
                xds_input.instamatic_update(key, True)
                if self.do_correct:
                    xds_input.correct_inputs(key)
                if not self.P1:
                    xds_input.cell_correct_online(os.path.join(key, "SMV", "XDS.INP"), self.cell, self.sg)
                run_dict[key] = "ready"

        # 3) Gather XDS.inp
        xds_list = []
        for k in run_dict.keys():
            if run_dict[k] == "ready":
                xds_inp1 = os.path.join(k, "xds", "XDS.INP")
                xds_inp2 = os.path.join(k, "SMV", "XDS.INP")
                if os.path.isfile(xds_inp1):
                    xds_list.append(xds_inp1)
                elif os.path.isfile(xds_inp2):
                    xds_list.append(xds_inp2)

        if xds_list:
            # run xds
            self.logMessage.emit(f"Running XDS on: {xds_list}")
            xds_runner.xdsrunner(self.input_path, xds_list, True, False)

        # 4) update statuses
        self.status_dict = self.update_status_dict(self.status_dict)
        # 5) if not P1 => cluster
        if not self.P1:
            try:
                self.run_cluster()
            except Exception as e:
                self.logMessage.emit(f"Error in run_cluster: {e}")

    @staticmethod
    def convert_image(key: str):
        """Convert MRC->SMV in a separate thread if needed."""
        conv_thread = KillableThread(target=image_io.convert_mrc2img, args=(key,))
        conv_thread.start()
        conv_thread.join()

    def run_cluster(self):
        """Same logic from your original run_cluster, but no GUI calls."""
        pattern = re.compile(r'iter(\d+)')
        cluster_dir = os.path.join(self.input_path, self.name)
        if not os.path.isdir(cluster_dir):
            return
        numbers = []
        for _item in os.listdir(cluster_dir):
            if os.path.isdir(os.path.join(cluster_dir, _item)):
                match = pattern.match(_item)
                if match:
                    numbers.append(int(match.group(1)))

        if numbers:
            start_num = max(numbers) + 1
            last_cluster_number = len(self.status_dict[self.name][f"iter{max(numbers)}"]["input"])
        else:
            start_num = 1
            last_cluster_number = 0

        new_good_set = {
            f for f in self.status_dict.keys()
            if self.status_dict[f]["status"] == "good"
        }
        if self.good_set != new_good_set and len(new_good_set) != last_cluster_number and len(new_good_set) > 1:
            self.good_set = new_good_set
            new_iter_folder = os.path.join(self.input_path, self.name, f"iter{start_num}")
            os.mkdir(new_iter_folder)
            if self.make_picker_excel(new_iter_folder):
                xds_cluster.merge(
                    new_iter_folder, folder="",
                    reso=float(self.reso_limit), alert=False
                )
                self.status_dict[self.name][f"iter{start_num}"] = xds_analysis.extract_cluster_result(
                    new_iter_folder, self.reso_limit
                )
                html_report.create_html_file(new_iter_folder, "cluster")

    def make_picker_excel(self, path: str) -> bool:
        """Copied from your code. No GUI calls here."""
        data = []
        columns = ["No.", "Path", "Space group", "Unit cell", "Vol.", "ISa", "CC1/2", "Completeness", "Reso."]
        dtypes = {
            'No.': int, 'Path': str, 'Space group': int, 'Unit cell': str, "Vol.": str,
            'ISa': float, 'CC1/2': float, 'Completeness': float, 'Reso.': float,

        }

        num = 1
        for key, item in self.status_dict.items():
            if item["status"] == "good":
                stats = item["statistics"]
                uc = stats.get("unit_cell", [])
                uc_str = " ".join(map(str, uc)) if uc else ""
                volume_str = xds_runner.calculate_vol(stats.get("unit_cell", []), stats.get("unit_cell_esd", []))
                row = [
                    num,
                    os.path.join(item["folder"], "SMV") if os.path.isdir(os.path.join(item["folder"], "SMV"))
                    else os.path.join(item["folder"], "xds"),
                    self.sg,
                    uc_str,
                    volume_str,
                    stats.get("ISa_model", 0),
                    stats.get("cc12_reso", stats.get("CC1/2", 0)),
                    stats.get("completeness", 0),
                    stats.get("resolution", 0)
                ]
                data.append(row)
                num += 1

        if len(data) < 1:
            try:
                os.rmdir(path)
            except Exception as e:
                print("Error in make_picker_excel:", e)
                pass
            return False

        df = pd.DataFrame(data, columns=columns)
        for c, dt in dtypes.items():
            if c in df.columns:
                df[c] = df[c].astype(dt)

        excel_filename = os.path.join(path, "xdspicker.xlsx")
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return True

    @staticmethod
    def get_md5(file_path: str):
        """
        Compute the MD5 checksum of a file.
        If the file is not readable, logs a warning and returns None.
        """
        # Optional: early check if file is readable
        if not os.access(file_path, os.R_OK):
            print(f"Permission denied (unreadable): {file_path}")
            return None

        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hash_md5.update(chunk)
        except PermissionError:
            print(f"Permission denied when opening: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
        return hash_md5.hexdigest()


class RealTime(QWidget):
    """
    The main GUI component (PyQt6) for monitoring and processing real-time MicroED data.
    Now uses RealTimeWorker (QThread) for background tasks.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Basic Variables
        self.strategy_dict = None
        self.P1 = False
        self.cursors = []
        self.run_bool = False
        self.reso_limit = None
        self.name = None
        self.sg = None
        self.cell = None
        self.status_dict = {}
        self.good_set = set()
        self.thread = {}

        # The path user sets
        self.input_path = ""
        self.realtime_current_average_unit_cell = "Waiting..."
        self.worker = None
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 10, 10)
        main_layout.setSpacing(16)
        main_layout.addSpacing(12)
        self.setLayout(main_layout)

        introduce_label = QLabel(
            "RealTime MicroED data processing, compatible for EPU-D and Instamatic.\n"
            "Load the path and Save Parameters before continuing!"
        )
        main_layout.addWidget(introduce_label)

        # Row 2: "Basic Information" label
        note_label = QLabel("Basic Information:")
        note_label.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        main_layout.addWidget(note_label)

        # Row 3: Name, Unit cell, SG
        row3_frame = QHBoxLayout()
        main_layout.addLayout(row3_frame)
        row3_frame.addSpacing(20)
        row3_frame.setSpacing(20)

        self.mode_switch_button = SegmentedControl(["Screen", "Merge"], default_index=1)
        self.mode_switch_button.buttonGroup.buttonClicked.connect(self.button_switch)
        row3_frame.addWidget(self.mode_switch_button)

        row3_frame.addWidget(self.mode_switch_button)

        row3_frame.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setFixedWidth(200)
        row3_frame.addWidget(self.name_edit)

        row3_frame.addWidget(QLabel("Filter Strategy:"))
        self.strategy_option_var = ComboBox()
        self.strategy_options = ["--", "default", "edit"]
        self.strategy_option_var.addItems(self.strategy_options)
        row3_frame.addWidget(self.strategy_option_var)

        self.strategy_option_var.currentIndexChanged.connect(self.load_strategy)

        # Beam Stop Used
        self.is_beam_stop = QCheckBox("Beam Stop Used")
        self.is_beam_stop.setChecked(False)
        row3_frame.addWidget(self.is_beam_stop)

        # Correct Input
        self.do_correct = QCheckBox("Correct Input")
        self.do_correct.setChecked(True)
        row3_frame.addWidget(self.do_correct)
        row3_frame.addStretch()

        # Row 4: Resolution limit, Strategy, Beam Stop, Correct
        row4_frame = QHBoxLayout()
        main_layout.addLayout(row4_frame)
        row4_frame.addSpacing(20)

        row4_frame.addWidget(QLabel("Space Group:"))
        self.sg_edit = QLineEdit()
        self.sg_edit.setFixedWidth(80)
        row4_frame.addWidget(self.sg_edit)

        row4_frame.addWidget(QLabel("Unit Cell:"))
        self.cell_edit = QLineEdit()
        self.cell_edit.setFixedWidth(400)
        row4_frame.addWidget(self.cell_edit)

        row4_frame.addWidget(QLabel("Resolution Limit:"))
        self.reso_edit = QLineEdit()
        self.reso_edit.setFixedWidth(60)
        row4_frame.addWidget(self.reso_edit)

        row4_frame.addStretch()

        # Row 5: Start/Stop
        row5_frame = QHBoxLayout()
        main_layout.addLayout(row5_frame)
        row5_frame.addSpacing(20)

        self.btn_run = QPushButton("RealTime MicroED")
        self.realtime_animation = AnimationWidget(word="RealTime Processing...")
        self.btn_stop = QPushButton("Stop Run")
        row5_frame.addWidget(self.btn_run)
        row5_frame.addWidget(self.realtime_animation)
        row5_frame.addWidget(self.btn_stop)
        row5_frame.addStretch()

        self.btn_run.clicked.connect(self.run_realtime_microed)
        self.btn_stop.clicked.connect(self.stop_running)

        # Row 6-8: Display
        result_label = QLabel("Current Result:")
        result_label.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        main_layout.addWidget(result_label)

        row6_frame = QHBoxLayout()
        main_layout.addLayout(row6_frame)
        row6_frame.addSpacing(20)

        row6_frame.addWidget(QLabel("Running Summary:"))
        self.running_summary = QLineEdit()
        self.running_summary.setFixedWidth(200)
        row6_frame.addWidget(self.running_summary)
        row6_frame.addWidget(QLabel("(Good / Proc. / All),"))

        row6_frame.addWidget(QLabel("Overall Complete.:"))
        self.completeness_display = QLineEdit()
        self.completeness_display.setFixedWidth(80)
        row6_frame.addWidget(self.completeness_display)

        row6_frame.addWidget(QLabel("under Resolution of"))
        self.resolution_display = QLineEdit()
        self.resolution_display.setFixedWidth(60)
        row6_frame.addWidget(self.resolution_display)
        replace_entry_readonly(self.running_summary, "0 / 0 / 0")
        row6_frame.addStretch()

        row7_frame = QHBoxLayout()
        main_layout.addLayout(row7_frame)
        row7_frame.addSpacing(20)

        self.overall_cc12_label = QLabel("Overall CC1/2")
        row7_frame.addWidget(self.overall_cc12_label)
        self.cc12_display = QLineEdit()
        self.cc12_display.setFixedWidth(100)
        row7_frame.addWidget(self.cc12_display)

        row7_frame.addWidget(QLabel("Status of Last Run:"))
        self.last_status = QLineEdit()
        self.last_status.setFixedWidth(550)
        row7_frame.addWidget(self.last_status)
        self.single_cc12_label = QLabel("Last CC1/2")
        self.cc12_display_P1 = QLineEdit()
        self.cc12_display_P1.setFixedWidth(100)
        row7_frame.addWidget(self.single_cc12_label)
        row7_frame.addWidget(self.cc12_display_P1)
        row7_frame.addStretch()

        replace_entry_readonly(self.last_status, "Waiting...")
        replace_entry_readonly(self.completeness_display, "0.0")
        replace_entry_readonly(self.resolution_display, "0.0")
        replace_entry_readonly(self.cc12_display, "0.0")
        replace_entry_readonly(self.cc12_display_P1, "0.0")
        self.cc12_display_P1.setVisible(False)
        self.single_cc12_label.setVisible(False)

        row8_frame = QHBoxLayout()
        main_layout.addLayout(row8_frame)
        row8_frame.addSpacing(20)

        self.unit_cell_label = QLabel("Average Unit Cell")
        row8_frame.addWidget(self.unit_cell_label)
        self.unit_cell_display = QLineEdit()
        self.unit_cell_display.setFixedWidth(600)
        row8_frame.addWidget(self.unit_cell_display)
        row8_frame.addStretch()

        replace_entry_readonly(self.unit_cell_display, "Waiting...")

        # Row 9: 2 Buttons: Open Cluster Report, Open xscale.lp
        row12_frame = QHBoxLayout()
        main_layout.addLayout(row12_frame)
        row12_frame.addSpacing(20)

        open_cluster_button = QPushButton("Open Cluster Report")
        open_cluster_button.clicked.connect(self.open_report)
        open_xscale_button = QPushButton("Open Current xscale.lp")
        open_xscale_button.clicked.connect(self.open_current_xscale_lp)

        row12_frame.addWidget(open_cluster_button)
        row12_frame.addWidget(open_xscale_button)
        row12_frame.addStretch()

        # Row 10: "Live Statistics"
        note_label2 = QLabel("Live Statistics:")
        note_label2.setFont(QFont("Liberation Sans", 14, QFont.Weight.Bold))
        main_layout.addWidget(note_label2)

        # Row 11: Plot area with 3 subplots
        plots_layout = QHBoxLayout()
        main_layout.addLayout(plots_layout)

        self.figures = []
        self.axes = []
        self.plot_canvases = []
        for i in range(3):
            fig = Figure(figsize=(3.5, 3), dpi=96)
            canvas = FigureCanvasQTAgg(fig)
            ax = fig.add_subplot(111)
            self.figures.append(fig)
            self.plot_canvases.append(canvas)
            self.axes.append(ax)
            plots_layout.addWidget(canvas)

        self.update_plots()
        main_layout.addStretch()

        self.mode_switch_button.setToolTip("Toggle between screening mode (P1) and merging mode")
        self.name_edit.setToolTip("Sample Name")
        self.strategy_option_var.setToolTip("Select filtering strategy for data processing")
        self.is_beam_stop.setToolTip("Check if beam stop was using during data collection")
        self.do_correct.setToolTip("Enable automatic correction of input parameters")
        self.sg_edit.setToolTip("Space group number (e.g., 1 for P1, 19 for P212121)")
        self.cell_edit.setToolTip("Unit cell parameters: a b c alpha beta gamma (e.g., 50 60 70 90 90 90)")
        self.reso_edit.setToolTip("Resolution for completeness calculation (e.g., 1.5)")
        self.btn_run.setToolTip("Start real-time data processing")
        self.btn_stop.setToolTip("Stop the real-time monitoring and processing")
        self.running_summary.setToolTip("Count of good datasets / processable datasets / all datasets")
        self.completeness_display.setToolTip("Overall data completeness percentage")
        self.resolution_display.setToolTip("Resolution limit used for processing")
        self.cc12_display.setToolTip("CC1/2 value for the merged data")
        self.last_status.setToolTip("Status of the most recently processed dataset")
        self.cc12_display_P1.setToolTip("CC1/2 value for the most recent dataset")
        self.unit_cell_display.setToolTip("Unit cell parameters")
        open_cluster_button.setToolTip("Open HTML report of clustered datasets")
        open_xscale_button.setToolTip("View detailed merging statistics in XSCALE.LP file")

    def button_switch(self, button):
        btn_id = self.mode_switch_button.buttonGroup.id(button)
        try:
            if self.worker and self.worker.isRunning():
                QMessageBox.warning(
                    self, "Warning", "Please stop the current run first.",
                    QMessageBox.StandardButton.Ok
                )
                return
        except RuntimeError:
            pass
        if btn_id == 0:
            self.P1 = True
            self.cell_edit.setReadOnly(True)
            self.sg_edit.setReadOnly(True)
            self.reso_edit.setReadOnly(True)
            self.unit_cell_label.setText("Last Unit Cell/SG")
            self.overall_cc12_label.setVisible(False)
            self.cc12_display.setVisible(False)
            self.cc12_display_P1.setVisible(True)
            self.single_cc12_label.setVisible(True)
        else:
            self.P1 = False
            self.cell_edit.setReadOnly(False)
            self.sg_edit.setReadOnly(False)
            self.reso_edit.setReadOnly(False)
            self.unit_cell_label.setText("Average Unit Cell")
            self.single_cc12_label.setVisible(False)
            self.cc12_display_P1.setVisible(False)
            self.overall_cc12_label.setVisible(True)
            self.cc12_display.setVisible(True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Worker Start/Stop ~~~~~~~~~~~~~~~~~~~~
    def run_realtime_microed(self):
        """Create and start the RealTimeWorker thread."""
        if not self.input_path:
            QMessageBox.warning(self, "Warning", "No input folder chosen.")
            return

        # Check for input_parameters
        iparam = os.path.join(self.input_path, "Input_parameters.txt")
        if not os.path.isfile(iparam):
            QMessageBox.information(self, "Warning", "Input_parameters.txt is missing.")
            return

        # Possibly write default strategy if missing
        strategy_file = os.path.join(self.input_path, "strategy.txt")
        if not os.path.isfile(strategy_file):
            self.write_default_strategy()

        # Gather user input
        self.mode = self.mode_switch_button.currentText()
        self.cell = self.cell_edit.text().strip()
        if not self.P1:
            if not self.sg_edit.text().strip():
                QMessageBox.warning(self, "Warning", "Space group should be present in the Merge mode.")
                return
            try:
                self.sg = spgfinder.get_int_number(self.sg_edit.text().strip())
                if self.sg is None and not self.P1:
                    raise ValueError("Invalid space group number.")
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Invalid space group: {e}")
                return
        self.reso_limit = self.reso_edit.text().strip()
        do_correct = self.do_correct.isChecked()
        beam_stop = self.is_beam_stop.isChecked()

        if self.mode == "Screen":
            reply2 = QMessageBox.question(
                self, "Warning",
                "Screen mode will only do P1 stage and not merge.\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                self.P1 = True
                self.reso_limit = "1.0" if not self.reso_limit else self.reso_limit
            else:
                return
        # If user left cell or sg blank => ask about P1
        elif self.mode == "Merge" and (not self.cell or not self.sg):
            reply = QMessageBox.question(
                self, "Warning",
                "You haven't provided cell or space group.\nRun in Screen mode (P1)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.mode_switch_button.buttonGroup.button(0).click()
                reply2 = QMessageBox.question(
                    self, "Warning",
                    "Screen mode will only do P1 stage and not merge.\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply2 == QMessageBox.StandardButton.Yes:
                    self.P1 = True
                    self.reso_limit = "1.0" if not self.reso_limit else self.reso_limit
                else:
                    return
            else:
                return
        elif self.mode == "Merge":
            self.P1 = False
        else:
            return

        if not self.name_edit.text().strip():
            replace_entry(self.name_edit, "RealTimeED")
        self.name = self.name_edit.text().strip()

        # Create worker
        self.worker = RealTimeWorker(
            self.input_path, self.name, self.cell, self.sg, self.reso_limit,
            do_correct, beam_stop, self.P1,
            old_status_dict=self.status_dict,  # pass current dict if you like
            strategy_dict=self.strategy_dict
        )
        # Connect signals
        self.worker.statusChanged.connect(self.onStatusChanged)
        self.worker.logMessage.connect(self.onWorkerLog)
        self.worker.finishedSignal.connect(self.onWorkerFinished)
        self.worker.finished.connect(lambda: self.worker.deleteLater())

        # Start
        self.worker.start()
        self.realtime_animation.startAnimation()

    @pyqtSlot()
    def stop_running(self, output: str = True):
        """Stop real-time MicroED worker."""
        try:
            if self.worker and self.worker.isRunning():
                self.worker.stop()
        except RuntimeError:
            pass
        self.realtime_animation.stopAnimation()
        if output:
            QMessageBox.warning(self, "Caution", "RealTime MicroED has been requested to stop.")

    @pyqtSlot(dict)
    def onStatusChanged(self, new_dict: dict):
        """Slot called when worker updates status_dict."""
        self.status_dict = new_dict
        # Re-run your normal "update_display" and "update_plots" here
        self.update_display()
        self.update_plots()

    @pyqtSlot(str)
    def onWorkerLog(self, msg: str):
        """Optional: handle worker debug/log messages."""
        print("WorkerLog:", msg)

    @pyqtSlot(str)
    def onWorkerFinished(self, msg: str):
        """Called when worker's run() ends."""
        self.realtime_animation.stopAnimation()
        print("Worker finished:", msg)

    def load_strategy(self, index: int):
        """
        Load/edit the strategy. If user picks 'edit', open text editor.
        """
        text = self.strategy_option_var.currentText()
        if not self.input_path:
            print("Input path is not set. Please set the input path first.")
            return
        if text == "--":
            return
        else:
            strategy_file = os.path.join(self.input_path, "strategy.txt")
            if not os.path.isfile(strategy_file):
                self.write_default_strategy()
            if text == "edit":
                self.text_edit(strategy_file)

    def write_default_strategy(self):
        """
        Write a default processing strategy to strategy.txt (same as original).
        """
        strategy_file = os.path.join(self.input_path, "strategy.txt")
        with open(strategy_file, "w") as f:
            f.write("! CYCLE_TIME, refresh time, default 5 s. \n")
            f.write("! WAITING_TIME, time waiting for real processing\n")
            f.write("! after folder is unchanged, default 10 s.\n")
            f.write(" CYCLE_TIME= 5\n")
            f.write(" WAITING_TIME= 20\n\n")
            f.write("! Available Filter for RUN_FILTER: CC12, ISA, REXP, RMEAS, RESOLUTION, VOLUME_DEV\n")
            f.write(" RUN_FILTER= CC12 > 85\n")
            f.write(" RUN_FILTER= ISA > 2\n")
            f.write(" RUN_FILTER= ISA < 50\n\n")
            f.write("! Available Filter for MERGE_FILTER: CC12, DISTANCE\n")
            f.write(" MERGE_FILTER= CC12 > 0\n\n\n")

    def text_edit(self, file_path: str):
        """
        Same as your existing method to open a text editor QDialog.
        """

        class TextEditorDialog(QDialog):
            def __init__(self, parent=None, file_to_edit=""):
                super().__init__(parent)
                self.setWindowTitle("Text Editor")
                self.resize(600, 400)

                self.file_to_edit = file_to_edit

                vlayout = QVBoxLayout(self)
                self.text_edit = QPlainTextEdit(self)
                vlayout.addWidget(self.text_edit)

                hlayout = QHBoxLayout()
                save_btn = QPushButton("Save")
                hlayout.addWidget(save_btn)
                vlayout.addLayout(hlayout)

                save_btn.clicked.connect(self.save_file)

                # Load file
                if os.path.isfile(self.file_to_edit):
                    with open(self.file_to_edit, "r") as fp:
                        content = fp.read()
                        self.text_edit.setPlainText(content)

            def save_file(self):
                with open(self.file_to_edit, "w") as fp:
                    fp.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Save", "File saved successfully")

        dlg = TextEditorDialog(self, file_path)
        dlg.exec()

    def update_display_initial(self) -> None:
        """Initialize the GUI display with the current status dictionary.

        Loads the realtime.json file, updates GUI entry widgets with dataset information,
        and sets up initial display states.

        Returns:
            None
        """
        if os.path.exists(os.path.join(self.input_path, 'online.json')):
            shutil.move(os.path.join(self.input_path, 'online.json'), os.path.join(self.input_path, 'realtime.json'))
        with open(os.path.join(self.input_path, 'realtime.json'), 'r') as file:
            self.status_dict = json.load(file)
        for key, item in self.status_dict.items():
            if item["status"] == "document":
                try:
                    if key == "realtime":
                        key = "RealTimeED"
                    replace_entry(self.name_edit, key)
                    replace_entry(self.cell_edit, item["input"]["cell"])
                    replace_entry(self.sg_edit, item["input"]["sg"])
                    replace_entry(self.reso_edit, item["input"]["reso_limit"])
                    self.is_beam_stop.setChecked(strtobool(item["input"]["beam_stop"]))
                    self.do_correct.setChecked(strtobool(item["input"]["do_correct"]))
                    return
                except KeyError:
                    return

    def update_plots(self):
        """
        Same logic as your original. We just call it after we get new status_dict
        from the worker.
        """

        def dynamic_size(length):
            if length <= 10:
                ms, me = 8, 3
            elif length <= 20:
                ms, me = 6, 2
            elif length <= 40:
                ms, me = 4.5, 2
            else:
                ms, me = 4, 1.5
            return ms, me

        # Clear old cursors
        for c in self.cursors:
            try:
                c.remove()
            except:
                pass
        self.cursors.clear()

        # Prepare data
        try:
            good_list = sorted([(key, item["statistics"]) for key, item in self.status_dict.items()
                                if item["status"] == "good"], key=lambda x: x[1]["mtime"])
        except KeyError:
            good_list = [("Empty", {"resolution": 1, "isa": 1, "cc12_reso": 0})]
        if not good_list:
            good_list = [("Empty", {"resolution": 1, "isa": 1, "cc12_reso": 0})]

        y1_values = [d["resolution"] for (_, d) in good_list]
        x1_values = list(range(1, len(y1_values) + 1))
        ms1, me1 = dynamic_size(len(y1_values))
        name_good = [item[0] for item in good_list]

        y4_values = [d.get("cc12_reso", d.get("CC1/2", 0)) for (_, d) in good_list]
        y5_values = [d.get("isa", d.get("ISa_meas", 0)) for (_, d) in good_list]

        # Build cluster list if self.name is valid
        try:
            if self.name == "RealTimeED":
                name = "realtime"
            else:
                name = self.name
            cluster_subdict = self.status_dict.get(name, {})
            cluster_list = [(k, v) for (k, v) in cluster_subdict.items() if "resolution" in v]
            cluster_list.sort(key=lambda pair: natural_sort_key(pair[0]))
        except:
            cluster_list = [("Empty", {"completeness": 0, "cc12_reso": 0})]
        if not cluster_list:
            cluster_list = [("Empty", {"completeness": 0, "cc12_reso": 0})]

        name_cluster = [c[0].replace("cluster_", "") for c in cluster_list]

        if not self.P1:
            y2_values = [c[1]["completeness"] for c in cluster_list]
            y3_values = [c[1].get("cc12_reso", c[1].get("CC1/2", 0)) for c in cluster_list]
            x2_values = list(range(1, len(y2_values) + 1))
            ms2, me2 = dynamic_size(len(y2_values))

            for fig in self.figures:
                fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1, wspace=0.4)

            self.axes[0].clear()
            self.axes[0].plot(x1_values, y1_values, linestyle='--', marker='o', color='#EF9C66', linewidth=1.2,
                              markersize=ms1, markerfacecolor='white', markeredgewidth=me1)
            self.axes[0].set_title("Resolution vs Good Datasets", fontsize=13)
            self.axes[0].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)
            self.axes[0].invert_yaxis()

            self.axes[1].clear()
            self.axes[1].plot(x2_values, y2_values, linestyle='-', marker='o', color='#B3BC7A', linewidth=2,
                              markersize=ms2, markerfacecolor='white', markeredgewidth=me2)
            self.axes[1].set_title("Completeness vs Iters", fontsize=14)
            self.axes[1].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)

            self.axes[2].clear()
            self.axes[2].plot(x2_values, y3_values, linestyle='-', marker='o', color='#78ABA8', linewidth=2,
                              markersize=ms2, markerfacecolor='white', markeredgewidth=me2)
            self.axes[2].set_title("CC1/2 vs Iters", fontsize=14)
            self.axes[2].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)
        else:
            # P1 => resolution vs Good, CC1/2 vs Good, I/Sigma vs Good
            for fig in self.figures:
                fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1, wspace=0.4)

            self.axes[0].clear()
            self.axes[0].plot(x1_values, y1_values, linestyle='--', marker='o', color='#EF9C66', linewidth=1.2,
                              markersize=ms1, markerfacecolor='white', markeredgewidth=me1)
            self.axes[0].set_title("Resolution vs Good Datasets", fontsize=13)
            self.axes[0].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)
            self.axes[0].invert_yaxis()

            self.axes[1].clear()
            self.axes[1].plot(x1_values, y4_values, linestyle='--', marker='o', color='#B3BC7A', linewidth=1.2,
                              markersize=ms1, markerfacecolor='white', markeredgewidth=me1)
            self.axes[1].set_title("CC1/2 vs Good Datasets", fontsize=14)
            self.axes[1].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)

            self.axes[2].clear()
            self.axes[2].plot(x1_values, y5_values, linestyle='--', marker='o', color='#78ABA8', linewidth=1.2,
                              markersize=ms1, markerfacecolor='white', markeredgewidth=me1)
            self.axes[2].set_title("I/Sigma vs Good Datasets", fontsize=14)
            self.axes[2].grid(True, which='major', axis="y", linestyle='--', linewidth=0.5)

        def on_add(sel, name_list, data):
            xval = round(sel.target[0], 1)
            yval = round(sel.target[1], 3)
            index = int(round(xval, 0) - 1)
            if index < 0:
                index = 0
            elif index > len(name_list) - 1:
                index = len(name_list) - 1
            dataset_name = name_list[index]
            if len(dataset_name) > 16:
                dataset_name = dataset_name[:7] + ".." + dataset_name[-7:]
            sel.annotation.set_text(f"{dataset_name}\nX: {xval}\nY: {yval}")
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.6)

        # Add mplcursors
        for i, ax in enumerate(self.axes):
            cursor = mplcursors.cursor(ax, hover=True)
            self.cursors.append(cursor)
            if i == 0:
                data = y1_values
                names = name_good
            elif i == 1:
                data = (y4_values if self.P1 else [c[1].get("completeness", 0) for c in cluster_list])
                names = name_good if self.P1 else name_cluster
            else:
                data = (y5_values if self.P1 else [c[1].get("cc12_reso", c[1].get("CC1/2", 0)) for c in cluster_list])
                names = name_good if self.P1 else name_cluster

            cursor.connect("add", lambda sel, name_list=names, data=data: on_add(sel, name_list, data))

        for canvas in self.plot_canvases:
            try:
                canvas.draw()
            except Exception as exc:
                print(f"Plot failed due to {exc}")

    def update_display(self):
        """
        Similar to your original code: update line edits with the latest info from status_dict.
        """
        # Gather
        good_list = [item for key, item in self.status_dict.items() if item["status"] == "good"]
        failed_list = [item for key, item in self.status_dict.items() if item["status"] == "failed"]
        all_list = []
        for key, val in self.status_dict.items():
            st = val["status"]
            if st in ["good", "bad", "failed"]:
                all_list.append((key, val))
        all_list.sort(key=lambda x: x[1]["statistics"].get("mtime", 0), reverse=True)

        if len(all_list) < 1:
            return

        replace_entry_readonly(
            self.running_summary,
            f"{len(good_list)} / {len(all_list) - len(failed_list)} / {len(all_list)}"
        )
        replace_entry_readonly(
            self.last_status,
            f"{all_list[0][0]}: {all_list[0][1]['status']}"
        )
        if self.P1:
            replace_entry_readonly(self.resolution_display, "--")
            if 'unit_cell' in all_list[0][1]['statistics']:
                unit_cell = all_list[0][1]['statistics']['unit_cell']
                formatted_cell = []
                for x in unit_cell:
                    if abs(x - 90.0) < 1e-6:
                        formatted_cell.append("90")
                    elif abs(x - 120.0) < 1e-6:
                        formatted_cell.append("120")
                    else:
                        formatted_cell.append(str(round(x, 3)))
                sg_name = all_list[0][1]['statistics'].get("space_group_name",
                                                           all_list[0][1]['statistics'].get("space_group_number", ""))
                if sg_name:
                    replace_entry_readonly(self.unit_cell_display, "  ".join(formatted_cell) + ", SG: " + str(sg_name))
                else:
                    replace_entry_readonly(self.unit_cell_display, "  ".join(formatted_cell))
            else:
                replace_entry_readonly(self.unit_cell_display, "--")
            try:
                cc12 = all_list[0][1]['statistics'].get("cc12_reso", all_list[0][1]['statistics'].get("CC1/2", 0))
            except KeyError:
                cc12 = 0
            if cc12:
                replace_entry_readonly(self.cc12_display_P1, f"{cc12:.1f} %")
            else:
                replace_entry_readonly(self.cc12_display_P1, "--")
        else:
            replace_entry_readonly(self.resolution_display, f"{self.reso_edit.text().strip()}")
            # If merges exist, gather last iteration
            pattern = re.compile(r'iter(\d+)')
            name_text = self.name_edit.text().strip()
            if not name_text:
                return

            numbers = []
            cpath = os.path.join(self.input_path, name_text)
            if os.path.isdir(cpath):
                for _item in os.listdir(cpath):
                    if os.path.isdir(os.path.join(cpath, _item)):
                        match = pattern.match(_item)
                        if match:
                            numbers.append(int(match.group(1)))
            if numbers:
                last_num = max(numbers)
                folder_path = os.path.join(cpath, f"iter{last_num}")
                try:
                    info_dict = xds_analysis.extract_cluster_result(
                        folder_path, reso=float(self.reso_edit.text().strip() or "1.0")
                    )
                except Exception as e:
                    print("Error in extract_cluster_result:", e)
                    info_dict = {}
                cc12 = info_dict.get("cc12_reso", info_dict.get("CC1/2", 0))
                completeness = info_dict.get("completeness", 0)
                unit_cell = info_dict.get("unit_cell", [])

                replace_entry_readonly(self.completeness_display, f"{completeness:.1f} %")
                replace_entry_readonly(self.cc12_display, f"{cc12} %")

                if unit_cell:
                    formatted_cell = []
                    for x in unit_cell:
                        if abs(x - 90.0) < 1e-6:
                            formatted_cell.append("90")
                        elif abs(x - 120.0) < 1e-6:
                            formatted_cell.append("120")
                        else:
                            formatted_cell.append(str(round(x, 3)))
                    replace_entry_readonly(self.unit_cell_display, "  ".join(formatted_cell))
                else:
                    replace_entry_readonly(self.unit_cell_display, "Waiting...")

    def open_report(self):
        """
        Same as your original open_report, no changes needed.
        """
        pattern = re.compile(r'iter(\d+)')
        numbers = []
        if not self.name:
            print("No name set. Aborting open_report.")
            return
        cpath = os.path.join(self.input_path, self.name)
        if not os.path.isdir(cpath):
            print("No directory for cluster merges. Aborting.")
            return

        for _item in os.listdir(cpath):
            if os.path.isdir(os.path.join(cpath, _item)):
                match = pattern.match(_item)
                if match:
                    numbers.append(int(match.group(1)))

        if numbers:
            last_num = max(numbers)
            xds_path = os.path.join(self.input_path, self.name, f"iter{last_num}")
            html_report.open_html_file(xds_path, "cluster")
        else:
            print("No merged data present. Please wait.\n")

    def open_current_xscale_lp(self):
        """
        Same as your original open_current_xscale_lp, with a local QDialog.
        """
        pattern = re.compile(r'iter(\d+)')
        numbers = []
        if not self.name:
            print("No name set. Aborting open_current_xscale_lp.")
            return
        cpath = os.path.join(self.input_path, self.name)
        if not os.path.isdir(cpath):
            print("No directory for cluster merges. Aborting.")
            return

        for _item in os.listdir(cpath):
            if os.path.isdir(os.path.join(cpath, _item)):
                match = pattern.match(_item)
                if match:
                    numbers.append(int(match.group(1)))

        if numbers:
            last_num = max(numbers)
        else:
            print("No merged data present. Please wait.\n")
            return

        xscale_lp_path = os.path.join(self.input_path, self.name, f"iter{last_num}", "XSCALE.LP")
        if not os.path.isfile(xscale_lp_path):
            print("XSCALE.LP file not found.")
            return

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
