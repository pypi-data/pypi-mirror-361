import os
import re

import numpy as np

from .cell_distance import unit_cell_distance_procrustes
from .metrics import calculate_cc_half, calculate_r_factors
from .refl_combine import generate_unique_no_d, load_refls_bravais
from .util import shape_cell_parameter_bravais, inverse_transform_hkl, transform_hkl
from ..symm_shelx.laue_symm_ops import symmetry_operations
from ..symm_shelx.symm_function import get_laue_group

IDXV = {'P': 1, 'C': 2, 'I': 2, 'R': 3, 'F': 4}


def parse_and_rank_marked_lines(marked_lines: list) -> dict:
    """Parses and ranks marked lines from the file content.

    Args:
        marked_lines (list): List of marked lines from the file.

    Returns:
        dict: Parsed and ranked data grouped by Bravais lattice type.
    """
    parsed_data = {}
    for line in marked_lines:
        line = re.sub(r'(\d)-', r'\1 -', line)
        parts = line.split()
        if len(parts) < 12:
            continue
        lattice_char, bravais, qof = parts[:3]
        if float(qof) >= 500:
            continue
        cell_params = list(map(float, parts[3:9]))
        transformation_matrix = list(map(int, parts[9:]))
        parsed_data.setdefault(bravais, []).append({
            "lattice_char": lattice_char,
            "bravais_lattice": bravais,
            "qof": float(qof),
            "cell_parameters": cell_params,
            "transformation_matrix": transformation_matrix
        })

    # Sort each Bravais lattice's entries by FOM (qof)
    for bravais in parsed_data:
        parsed_data[bravais].sort(key=lambda x: x["qof"])

    return parsed_data


def find_lattice_correct_lp(file_path: str) -> tuple:
    """Finds and parses the lattice from the correct LP file.

    Args:
        file_path (str): Path to the correct LP file.

    Returns:
        tuple: Test list, resolution range, and selected lattice data.
    """
    with open(file_path, 'r') as f:
        file_content = f.readlines()

    auto_sg_idx = next((i for i, line in enumerate(file_content) if 'AUTOMATIC SPACE GROUP ASSIGNMENT' in line), None)
    if auto_sg_idx is None:
        return ()

    space_group_number = None
    reso_low, reso_high = None, None
    marked_lines = []

    # Extract SPACE_GROUP_NUMBER
    for line in file_content[auto_sg_idx:]:
        if 'SPACE_GROUP_NUMBER' in line:
            space_group_number = int(line.split('=')[1].strip().split()[0])
            break

    # Extract lattice determination section
    lattice_det_idx = next((i for i, line in enumerate(file_content) if
                            'DETERMINATION OF LATTICE CHARACTER AND BRAVAIS LATTICE' in line), None)
    sym_ref_idx = next((i for i, line in enumerate(file_content) if
                        'SYMMETRY OF REFLECTION INTENSITIES' in line), None)

    lattice_section = file_content[lattice_det_idx:sym_ref_idx]
    symmetry_section = file_content[sym_ref_idx:] if sym_ref_idx else []

    record = False
    for line in lattice_section:
        stripped = line.strip()
        if stripped.startswith('*') and not stripped.startswith('**'):
            record = True
            marked_lines.append(line.replace("*", "").strip())
        elif stripped.startswith('**') and record:
            break
        elif record:
            marked_lines.append(line.replace("*", "").strip())

    # Extract resolution range and final lattice
    final_lattice = None
    for line in symmetry_section:
        if "TEST_RESOLUTION_RANGE=" in line:
            match = re.search(r'([\d\.]+)\s+([\d\.]+)', line)
            if match:
                reso_low, reso_high = map(float, match.groups())
        if line.strip().startswith('*') and not line.strip().startswith('**'):
            final_lattice = line.split()[-2]
            break

    parsed_data = parse_and_rank_marked_lines(marked_lines[:-1])
    test_list = []

    # Define the lattices that can have multiple entries
    multiple_option_lattices = {"aP", "mP", "mC", "mI"}

    for bravais, entries in parsed_data.items():
        if bravais in multiple_option_lattices:
            # Select up to 3 distinct entries based on a, b, c parameters
            selected_entries = []
            for entry in entries:
                shaped = shape_cell_parameter_bravais(entry, bravais)
                if shaped:
                    a_new, b_new, c_new = shaped[:3]
                    is_distinct = True
                    for selected in selected_entries:
                        a_sel, b_sel, c_sel = selected["cell_bravais_lattice"][:3]
                        if (abs(a_new - a_sel) <= 0.5 and
                                abs(b_new - b_sel) <= 0.5 and
                                abs(c_new - c_sel) <= 0.5):
                            if selected["lattice_char"] not in ["44", "31"]:
                                is_distinct = False
                                break
                    if is_distinct:
                        selected_entries.append({
                            **entry,
                            "cell_bravais_lattice": shaped
                        })
                        if len(selected_entries) == 3:
                            break
            test_list.extend(selected_entries)
        else:
            # For other lattices, select only the top entry
            top_entry = entries[0]
            shaped = shape_cell_parameter_bravais(top_entry, bravais)
            if shaped:
                test_list.append({
                    **top_entry,
                    "cell_bravais_lattice": shaped
                })
    try:
        for value_list in parsed_data.values():
            for value in value_list:
                if final_lattice in value['lattice_char']:
                    selected_lattice = value
    except Exception:
        selected_lattice = next(iter(parsed_data.values()), [None])[0]
    return test_list, reso_low, reso_high, selected_lattice


def test_lattice_symmetry_hkl(dir_path: str, output: bool = False) -> dict:
    """Tests lattice symmetry using HKL file and correct LP file.

    Args:
        dir_path (str): Directory containing HKL and LP files.
        output (bool, optional): Whether to print progress messages. Defaults to False.

    Returns:
        dict: Results of the lattice symmetry test, grouped by Bravais lattice.
    """
    correct_lp_path = os.path.join(dir_path, 'CORRECT.LP')
    xds_hkl_path = os.path.join(dir_path, 'XDS_ASCII.HKL')

    lattice_data = find_lattice_correct_lp(correct_lp_path)
    if not lattice_data:
        return {}

    bravais_lattice_sg = {
        'aP': [1], 'mP': [3], 'mC': [5], 'mI': [5], 'oP': [16], 'oC': [21], 'oI': [23], 'oF': [22],
        'tP': [75, 89], 'tI': [79, 97], 'hP': [143, 149, 150, 168, 177], 'hR': [146, 155],
        'cP': [195, 207], 'cI': [197, 211], 'cF': [196, 209]
    }

    test_list, reso_low, reso_high, lattice_used = lattice_data
    refls, _ = load_refls_bravais(xds_hkl_path, 30, 1)
    if refls.shape[0] < 200:
        refls, _ = load_refls_bravais(xds_hkl_path, 30, 0.8)
    if refls.shape[0] < 20:
        if output:
            print("Too few strong reflections in HKL file")
        return {}
    # Inverse transform reflections
    transformed_refls = inverse_transform_hkl(
        refls,
        lattice_used["transformation_matrix"],
        IDXV[lattice_used["bravais_lattice"][-1]]
    )

    result_list = []
    for value in test_list:
        bravais = value["bravais_lattice"]
        transformed = transform_hkl(
            transformed_refls,
            value["transformation_matrix"],
            IDXV[value["bravais_lattice"][-1]]
        )
        distance = unit_cell_distance_procrustes(value["cell_parameters"], value["cell_bravais_lattice"])

        for sg in bravais_lattice_sg.get(bravais, []):
            symmetry_ops = symmetry_operations.get(get_laue_group(sg), [])
            unique = generate_unique_no_d(transformed, symmetry_ops)
            r_meas = calculate_r_factors(unique)[1]

            result_list.append({
                "uniq": len(unique),
                "r_meas": r_meas,
                "diff": distance * 20,
                "sg_no": sg,
                "cc12": calculate_cc_half(unique)[0],
                "bravais_lattice": bravais,
                **value
            })

    # Compute base R_meas and base CC12 from space group 1 if available
    base_r_meas = next((res["r_meas"] for res in result_list if res["sg_no"] == 1), 1)
    base_cc12 = 100 - next((res["cc12"] for res in result_list if res["sg_no"] == 1), 100)

    if not base_r_meas:
        return {}

    for res in result_list:
        res["r_meas_ratio"] = np.round(res["r_meas"] / base_r_meas, 3) if base_r_meas != 0 else float('inf')
        res["cc12_ratio"] = np.round((100 - res["cc12"]) / base_cc12, 3) if base_cc12 != 0 else float('inf')

    # Organize results by Bravais lattice
    return_dict = {}
    for res in sorted(result_list, key=lambda x: x["sg_no"], reverse=True):
        bravais = res["bravais_lattice"]
        return_dict.setdefault(bravais, []).append(res)

    # Filter out unwanted Bravais lattice groups
    filtered_return_dict = {}
    for bravais, values in return_dict.items():
        r_ratios = [v["r_meas_ratio"] for v in values]
        r_values = [v["r_meas"] for v in values]

        if not (all(r > 5 for r in r_ratios) or
                all(r > 3 and rm > 60 for r, rm in zip(r_ratios, r_values))):
            filtered_return_dict[bravais] = values

    ap_entry = filtered_return_dict["aP"]
    if len(ap_entry) == 1:
        pass
    else:
        for entry in ap_entry:
            if entry["lattice_char"] == '31':
                aP_31 = entry
            elif entry["lattice_char"] == '44':
                aP_44 = entry
        if aP_31["qof"] < 40 and all(x < 92 for x in aP_31["cell_parameters"][3:7]):
            aP_31["cc12_ratio"] = 1
            filtered_return_dict["aP"] = [aP_31]
        else:
            filtered_return_dict["aP"] = [aP_44]

    return filtered_return_dict


if __name__ == "__main__":
    # Example usage
    dir_path = "/mnt/c/AutoLEI_demo/Tyrosine/experiment_2/SMV"
    results = test_lattice_symmetry_hkl(dir_path, output=True)
    for bravais, entries in results.items():
        print(f"Bravais Lattice: {bravais}")
        for entry in entries:
            print(entry)
