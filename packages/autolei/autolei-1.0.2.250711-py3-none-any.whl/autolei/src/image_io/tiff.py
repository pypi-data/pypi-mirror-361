import configparser
import glob
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import fabio
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QPushButton, QScrollArea, QMessageBox
)
from fabio import adscimage
from tqdm import tqdm

from ..util import *
from ..xds_input import extract_keywords

script_dir = os.path.dirname(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(script_dir), 'setting.ini'))

set_max_worker = int(config["General"]["max_core"])

# wavelength for different voltage
WAVELENGTHS = {
    '400': 0.016439,
    '300': 0.019687,
    '200': 0.025079,
    '150': 0.029570,
    '120': 0.033492,
    '100': 0.037014,
    '400000.0': 0.016439,
    '300000.0': 0.019687,
    '200000.0': 0.025079,
    '150000.0': 0.029570,
    '120000.0': 0.033492,
    '100000.0': 0.037014,
}


class MetadataDialog(QDialog):
    def __init__(self, path_dict: dict, cl_default: str, HV_default: str,
                 pixel_size_default: str, root_dir: str, parent=None):
        super().__init__(parent)
        self.path_dict = path_dict
        self.cl_default = cl_default
        self.HV_default = HV_default
        self.pixel_size_default = pixel_size_default
        self.root_dir = root_dir
        self.result = (None, None, None)
        self.metadata_entries = {}  # Holds QLineEdits for each file entry
        self.initUI()

    def initUI(self):
        # Modern, clean style for a contemporary look
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 14pt;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 4px;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton {
                background-color: #0B76A0;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: #B7D9FF;
            }
        """)
        self.setWindowTitle("Metadata Input")
        self.setMinimumSize(750, 700)

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(15, 15, 15, 15)
        mainLayout.setSpacing(10)

        # --- Top layout for HV and Pixel Size ---
        topLayout = QHBoxLayout()
        labelHV = QLabel("HV")
        self.hvLineEdit = QLineEdit(self.HV_default)
        labelUnit = QLabel("keV,  Pixel Size")
        self.pixelSizeLineEdit = QLineEdit(self.pixel_size_default)
        labelPixelUnit = QLabel("μm")

        topLayout.addWidget(labelHV)
        topLayout.addWidget(self.hvLineEdit)
        topLayout.addWidget(labelUnit)
        topLayout.addWidget(self.pixelSizeLineEdit)
        topLayout.addWidget(labelPixelUnit)
        mainLayout.addLayout(topLayout)

        # --- Horizontal separator ---
        sepLine = QFrame()
        sepLine.setFrameShape(QFrame.Shape.HLine)
        sepLine.setFrameShadow(QFrame.Shadow.Sunken)
        mainLayout.addWidget(sepLine)

        # --- Scroll area for metadata entries ---
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setMaximumHeight(600)  # Limit height for a compact view

        scrollWidget = QWidget()
        gridLayout = QGridLayout(scrollWidget)
        gridLayout.setContentsMargins(10, 10, 10, 10)
        gridLayout.setSpacing(8)
        gridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Define column stretch factors
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 0)
        gridLayout.setColumnStretch(2, 0)
        gridLayout.setColumnStretch(3, 0)
        gridLayout.setColumnStretch(4, 0)

        # Header row
        headers = ["Relative Path", "Frames  ", "Range Start", "Range End", "CL (mm)"]
        for col, header in enumerate(headers):
            headerLabel = QLabel(header)
            font = headerLabel.font()
            font.setBold(True)
            headerLabel.setFont(font)
            gridLayout.addWidget(headerLabel, 0, col)

        # Populate rows for each path entry
        row = 1
        for path, info in self.path_dict.items():
            relative_path = info.get("relative_path", "N/A")
            num_frames = info.get("num", 0)

            # Locate metadata file to extract default angles, if available
            meta_path = ""
            if os.path.isfile(os.path.join(path, "metadata.txt")):
                meta_path = os.path.join(path, "metadata.txt")
            elif os.path.isfile(os.path.join(os.path.dirname(path), "metadata.txt")):
                meta_path = os.path.join(os.path.dirname(path), "metadata.txt")

            if meta_path:
                with open(meta_path, "r") as f:
                    metadata_dict = extract_keywords(f.readlines())
                try:
                    start_angle = float(metadata_dict.get("START_ANGLE", [0])[0])
                except Exception:
                    start_angle = 0
                try:
                    end_angle = float(metadata_dict.get("END_ANGLE", [0])[0])
                except Exception:
                    end_angle = 0
                try:
                    osc_angle = float(metadata_dict.get("OSCILLATION_RANGE", [0])[0])
                except Exception:
                    osc_angle = 0

                if start_angle and (not end_angle) and osc_angle:
                    end_angle = round(start_angle + num_frames * osc_angle, 2)
                elif (not start_angle) and end_angle and osc_angle:
                    start_angle = round(end_angle - num_frames * osc_angle, 2)
                start_angle_str = str(start_angle) if start_angle else ""
                end_angle_str = str(end_angle) if end_angle else ""
            else:
                start_angle_str = ""
                end_angle_str = ""

            # Create row widgets
            labelRelPath = QLabel(relative_path)
            labelFrames = QLabel(str(num_frames))
            rangeStartEdit = QLineEdit(start_angle_str)
            rangeEndEdit = QLineEdit(end_angle_str)
            clEdit = QLineEdit(self.cl_default)

            gridLayout.addWidget(labelRelPath, row, 0)
            gridLayout.addWidget(labelFrames, row, 1)
            gridLayout.addWidget(rangeStartEdit, row, 2)
            gridLayout.addWidget(rangeEndEdit, row, 3)
            gridLayout.addWidget(clEdit, row, 4)

            self.metadata_entries[path] = {
                'range_start': rangeStartEdit,
                'range_end': rangeEndEdit,
                'cl': clEdit
            }
            row += 1

        # Add a stretch row so that if content is less than maximum height,
        # the grid content stays at the top.
        gridLayout.setRowStretch(row, 1)

        scrollArea.setWidget(scrollWidget)
        mainLayout.addWidget(scrollArea)

        # --- Buttons at the bottom ---
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()  # Push buttons to the right
        convertButton = QPushButton("CONVERT")
        cancelButton = QPushButton("CANCEL")
        convertButton.clicked.connect(self.on_convert)
        cancelButton.clicked.connect(self.on_cancel)
        buttonLayout.addWidget(convertButton)
        buttonLayout.addWidget(cancelButton)
        mainLayout.addLayout(buttonLayout)

    def on_convert(self):
        hv = self.hvLineEdit.text().strip()
        pixel_size = self.pixelSizeLineEdit.text().strip()

        if not (hv and pixel_size):
            QMessageBox.critical(self, "Error", "HV or Pixel Size is empty!")
            return

        if hv not in WAVELENGTHS:
            QMessageBox.critical(self, "Error", "HV not a valid int.")
            return

        updated_path_dict = {}
        for _path, _info in self.path_dict.items():
            updated_info = _info.copy()
            if _path in self.metadata_entries:
                entries = self.metadata_entries[_path]
                range_start = entries['range_start'].text().strip()
                range_end = entries['range_end'].text().strip()
                cl = entries['cl'].text().strip()

                if range_start and range_end and cl:
                    updated_info['range_start'] = range_start
                    try:
                        osc_range = round((float(range_end) - float(range_start)) / _info["num"], 4)
                    except Exception as exc:
                        QMessageBox.critical(self, "Error", f"Error in {_path}: {exc}")
                        return
                    updated_info['osc_range'] = str(osc_range)
                    updated_info['cl'] = cl
                else:
                    QMessageBox.critical(self, "Error", f"Some entries in {_path} are empty!")
                    return
            updated_path_dict[_path] = updated_info

        self.result = (updated_path_dict, WAVELENGTHS[hv], pixel_size)
        self.accept()

    def on_cancel(self):
        self.result = (None, None, None)
        self.close()


def metadata_input(path_dict: dict, root_dir: str) -> tuple:
    """
    Prompts the user to input metadata for file conversion via a PyQt6 dialog and updates the provided path dictionary.

    This function reads default parameters (if available) from "Input_parameters.txt", computes a default HV value,
    and displays a modal dialog allowing the user to modify metadata for each file entry.

    Returns:
        tuple: A tuple containing:
            - Updated path_dict with metadata.
            - The wavelength corresponding to the input HV.
            - The pixel size.
        If the user cancels, returns (None, None, None).
    """
    # Get defaults from Input_parameters.txt if available.
    ip_path = os.path.join(root_dir, "Input_parameters.txt")
    if os.path.isfile(ip_path):
        with open(ip_path, "r") as file:
            keyword = extract_keywords(file.readlines())
            cl_default = keyword.get("DETECTOR_DISTANCE", [""])[0]
            wavelength_default = keyword.get("X-RAY_WAVELENGTH", [""])[0]
            pixel_size_default = keyword.get("QX", [""])[0]
    else:
        cl_default = ""
        wavelength_default = ""
        pixel_size_default = ""

    try:
        # Calculate a default HV value using physical constants.
        h, m0, c, e = 6.62607015e-34, 9.10938356e-31, 2.99792458e8, 1.602176634e-19
        voltage = round((np.sqrt((m0 * c ** 2) ** 2 + (h * c / (float(wavelength_default) * 1e-10)) ** 2)
                         - m0 * c ** 2) / e / 1e4) * 10
        HV_default = str(voltage)
    except Exception:
        HV_default = ""

    dialog = MetadataDialog(path_dict, cl_default, HV_default, pixel_size_default, root_dir)
    dialog.exec()  # Show dialog modally
    return dialog.result


def get_tiff_size(file_path: str) -> tuple:
    """
    Retrieves the dimensions of a TIFF image.

    Args:
        file_path (str): Path to the TIFF file.

    Returns:
        tuple: Dimensions of the image as (height, width).
    """
    try:
        tiff = fabio.open(file_path)
        return tiff.data.shape
    except Exception as e:
        print(f"Error opening TIFF file: {e}")
        return ()


def write_smv_tiff(
        file_path: str,
        phi: float,
        osc_range: float,
        wavelength: float,
        camera_length: float,
        pixel_size: float,
        image_size: tuple
) -> tuple:
    """
    Writes a TIFF file as an SMV image file.

    Args:
        file_path (str): Path to the TIFF file.
        phi (float): Phi angle for the image.
        osc_range (float): Oscillation range for the image.
        wavelength (float): Wavelength value.
        camera_length (float): Camera length in millimeters.
        pixel_size (float): Pixel size in micrometers.
        image_size (tuple): Size of the image (height, width).

    Returns:
        tuple: File path and success status as a boolean.
    """
    # Open the TIFF file using FabIO
    if not os.path.isfile(file_path):
        data = np.zeros(image_size, dtype=np.uint16)
        time = 0
    else:
        img = fabio.open(file_path)
        data = img.data.astype(np.uint16)
        time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M')

    img = adscimage.AdscImage(data=data.astype(np.uint16))

    # Specify output filename with .img extension in the same folder
    base_name = os.path.splitext(file_path)[0]
    output_path = os.path.join(os.path.dirname(file_path), f'{base_name}.img')

    img.header = {
        'DIM': 2,
        'BYTE_ORDER': 'little_endian',
        'TYPE': 'unsigned_short',
        'HEADER_BYTES': 512,
        'DATE': time,
        'WAVELENGTH': wavelength,
        'TIME': 0,
        'PHI': round(phi, 4),
        'OSC_START': round(phi, 4),
        'OSC_RANGE': osc_range,
        'PIXEL_SIZE': pixel_size,
        'DISTANCE': camera_length,
        'Data_type': "unsigned short int"
    }
    # Write the image to an SMV file
    img.write(output_path)
    return file_path, True


def conversion_tiff_file(
        info: dict,
        wl: float,
        px_size: float,
        max_worker: int = set_max_worker
) -> int:
    """
    Converts TIFF files to SMV format using parallel processing.

    Args:
        info (dict): Metadata information for the conversion.
        wl (float): Wavelength value.
        px_size (float): Pixel size in micrometers.
        max_worker (int, optional): Maximum number of threads to use. Defaults to `set_max_worker`.

    Returns:
        int: Number of successfully converted files.
    """

    results = []
    osc_range = float(info["osc_range"])
    start_angle = float(info["range_start"])
    tiff_files = info["image"]
    cl = info["cl"]
    file_base_name = info["file_base_name"]
    first = info["first"]
    last = info["last"]

    placeholder_count = file_base_name.count('?')
    replacement_format = f"{{:0{placeholder_count}d}}"

    file_names = [
        file_base_name.replace('?' * placeholder_count, replacement_format.format(i))
        for i in range(first, last + 1)
    ]
    dimensions = get_tiff_size(file_names[0])
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        future_to_tiff = {
            executor.submit(write_smv_tiff, image_path, start_angle + i * osc_range, osc_range,
                            wl, cl, px_size, (dimensions[0], dimensions[1])):
                image_path for i, image_path in enumerate(file_names)}
        for future in tqdm(as_completed(future_to_tiff), total=len(tiff_files), desc="Converting", ascii=True):
            tiff_path = future_to_tiff[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f'{tiff_path} generated an exception: {exc}')
    # Log the results
    converted_count = sum(1 for _, converted in results if converted)
    print(f"{converted_count} of {len(tiff_files)} converted.\n")
    return converted_count


def grab_info_tiff2img(directory: str, path_filter: bool = False) -> tuple:
    """
    Converts all TIFF files in a directory to IMG format.

    Args:
        directory (str): Directory containing TIFF files.
        path_filter (bool, optional): Flag to filter paths during conversion. Defaults to False.
    """
    if not directory:
        print("No directory selected. Exiting.")
        return None, None, None

    folder_paths = find_folders_with_images(directory, extension=".tiff", path_filter=path_filter)

    path_dict = {}

    for path in folder_paths:
        # Check if directory is collected by specific criteria or has already been converted
        parent_folder = os.path.dirname(path)
        cred_log_path = os.path.join(parent_folder, 'cRED_log.txt')

        # Skip if path is specifically an 'redp' output directory or has a corresponding cRED log
        if path.endswith("tiff_image") or os.path.isfile(cred_log_path):
            continue

        tiff_files = sorted(glob.glob(os.path.join(path, '*.tiff')), key=natural_sort_key)

        file_groups = {}
        for file in tiff_files:
            filename = os.path.basename(file)

            if re.search(r'\d+\.tiff$', filename):
                length = len(filename)

                # Group files based on the length of the filename
                if length not in file_groups:
                    file_groups[length] = [file]
                else:
                    file_groups[length].append(file)

        # Find the largest group based on the number of files
        max_group_size = 0
        max_group = []

        for length, files in file_groups.items():
            if len(files) > max_group_size:
                max_group_size = len(files)
                max_group = files

        # tiff_files now contains only files from the largest group by filename length
        tiff_files = sorted(max_group, key=natural_sort_key)

        img_files = sorted(glob.glob(os.path.join(os.path.join(parent_folder, 'SMV', 'data'), '*.img')),
                           key=natural_sort_key)
        if not img_files:
            img_files = sorted(glob.glob(os.path.join(path, '*.img')), key=natural_sort_key)

        # Check if the count of .img files matches the count of .mrc files, indicating conversion might already be done
        if len(img_files) >= len(tiff_files):
            print(f"Directory {path} don't need to convert.")
            continue

        file_base_name, first, last = extract_pattern(tiff_files)
        path_dict[path] = {
            "relative_path": os.path.relpath(path, directory),
            "file_base_name": file_base_name,
            "first": first,
            "last": last,
            "num": last - first + 1,
            "frame": len(tiff_files),
            "image": tiff_files,
            "base_name": file_base_name,
        }
    if not path_dict:
        print("No valid tiff documents. Exiting.")
        return None, None, None
    feedback, wl, px_size = metadata_input(path_dict, directory)
    return feedback, wl, px_size


def convert_tiff2img(feedback: dict, wl: float, px_size: float) -> None:
    print("********************************************")
    print("*            TIFF to SMV Image             *")
    print("********************************************\n")
    for path, info in feedback.items():
        print(f"Enter {path}")
        conversion_tiff_file(info, wl, px_size)
    print("Conversion Finished.\n")
    return
