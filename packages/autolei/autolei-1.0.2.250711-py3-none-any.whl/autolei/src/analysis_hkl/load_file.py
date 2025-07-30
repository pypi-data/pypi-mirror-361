import numpy as np


def load_xdsascii_hkl(hkl_path: str) -> tuple:
    """Loads HKL data from an XDS ASCII file.

    Args:
        hkl_path (str): Path to the XDS ASCII HKL file.

    Returns:
        tuple: Contains space group number (int), unit cell constants (list),
            and reflection data (np.ndarray).
    """
    sg_no = 1  # Default space group number
    unit_cell_constants = []
    data = []
    header_ended = False

    with open(hkl_path, 'r') as f:
        for line_number, line in enumerate(f, start=1):
            stripped_line = line.strip()

            if not header_ended:
                # Parse header information
                if stripped_line.startswith('!SPACE_GROUP_NUMBER='):
                    try:
                        sg_no = int(stripped_line.split('=', 1)[1])
                    except ValueError:
                        print(f"Invalid space group number format on line {line_number}. Using default sg_no=1.")
                elif stripped_line.startswith('!UNIT_CELL_CONSTANTS='):
                    try:
                        unit_cell_constants = list(map(float, stripped_line.split('=', 1)[1].split()))
                        if len(unit_cell_constants) != 6:
                            raise ValueError
                    except ValueError:
                        print(f"Invalid unit cell constants format on line {line_number}.")
                        raise ValueError("Unit cell constants must contain exactly 6 floating-point numbers.")
                elif stripped_line == '!END_OF_HEADER':
                    if not unit_cell_constants:
                        print("Unit cell constants not found before !END_OF_HEADER.")
                        raise ValueError("Unit cell constants not found in the header.")
                    header_ended = True
            else:
                # Parse data lines
                if not stripped_line or stripped_line.startswith('#'):
                    continue  # Skip empty lines or comments

                parts = stripped_line.split()

                # Check if the line has at least 10 columns
                if len(parts) < 10:
                    continue

                try:
                    h = int(parts[0])
                    k = int(parts[1])
                    l = int(parts[2])
                    float1 = float(parts[3])
                    float2 = float(parts[4])
                    flag = int(parts[9])
                    if float2 <= 0:
                        continue
                    data.append([h, k, l, float1, float2, flag])

                except ValueError as ve:
                    print(f"Skipping line {line_number}: value conversion error ({ve}).")
                    continue  # Skip lines with invalid data types
                except IndexError as ie:
                    print(f"Skipping line {line_number}: index error ({ie}).")
                    continue  # Skip lines with unexpected structure

    if not unit_cell_constants:
        print("Unit cell constants not found in the file.")
        raise ValueError("Unit cell constants not found in the file.")

    if not data:
        print("No valid reflection data found.")
        raise ValueError("No valid reflection data found.")

    data_array = np.array(data, dtype=np.float64)

    # Verify that data_array has exactly 6 columns
    if data_array.shape[1] != 6:
        print(f"Data array has {data_array.shape[1]} columns, expected 6.")
        raise ValueError(f"Expected 6 columns in data_array, but got {data_array.shape[1]}.")

    return sg_no, unit_cell_constants, data_array
