import json
import os

import numpy as np

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load extinction rules
with open(os.path.join(script_dir, 'extinction.json'), 'r') as file:
    extinction_rule = json.load(file)
from .load_file import load_xdsascii_hkl
from .util import unit_cell_volume
from .generate_hkl import generate_complete_reflection_list
from .metrics import slice_reflections, calculate_resolution_limit, accumulate_statistics, generate_slice_report
from .refl_combine import generate_unique_reflections, combine_hkl, mark_multiple_reflections
from ..symm_shelx.symm_function import test_rules, mark_forbidden_reflections


def get_unique_ideal_reflection(cell: list, sg: int, resolution: float, rule=None, MM: bool = False) -> list:
    """Generates unique ideal reflections based on unit cell, space group, and resolution.

    Args:
        cell (list): Unit cell parameters [a, b, c, alpha, beta, gamma].
        sg (int): Space group number.
        resolution (float): Resolution limit.
        rule (callable, optional): Extinction rule function. Defaults to None.
        MM (bool, optional): Macromolecular mode. Defaults to False.

    Returns:
        list: Unique ideal reflections.
    """

    a, b, c, al, be, ga = cell
    if (abs(a - b) < 0.01 and abs(b - c) < 0.01 and abs(al - be) < 0.1 and abs(
            be - ga) < 0.1 and al != 90 and be != 90 and ga != 90):
        is_R = True
    else:
        is_R = False
    total_refls = generate_complete_reflection_list(cell, resolution, MM)
    if not total_refls:
        return []
    unique_refls = generate_unique_reflections(total_refls, sg, cell)
    unique_refls = slice_reflections(unique_refls, 100, resolution)
    if not rule:
        _, _rule, _ = test_rules(unique_refls, sg, extinction_rule, is_R=is_R)
    else:
        _rule = rule
    forbid_idces = set(mark_forbidden_reflections(unique_refls, _rule))
    unique_refls = [reflection for idx, reflection in enumerate(unique_refls) if idx not in forbid_idces]
    return unique_refls


def analysis_xds_hkl(hkl_file: str, merge: bool = False, reso: float = None, output: bool = False, exclude: list = None,
                     MM: bool = False) -> dict:
    """Analyzes an HKL file to extract and compute crystallographic parameters.

    Args:
        hkl_file (str): Path to the HKL file.
        merge (bool, optional): Whether to merge reflections by identical hkl. Defaults to False.
        reso (float, optional): Resolution limit. Defaults to None.
        output (bool, optional): Whether to print progress messages. Defaults to False.
        exclude (list, optional): Data sources to exclude during merging. Defaults to None.
        MM (bool, optional): Macromolecular mode. Defaults to False.

    Returns:
        dict: Analysis results, including unit cell parameters, reflection statistics, and resolution limit.
    """
    if output:
        print(f"Analysis {hkl_file}.")
    # Load reflections and space group information
    space_group_number, unit_cell, reflections = load_xdsascii_hkl(hkl_file)

    if unit_cell[0] * unit_cell[1] * unit_cell[2] > 300000 and not MM:
        return {"mtime": os.path.getmtime(hkl_file),
                "space_group_number": space_group_number,
                "unit_cell": unit_cell,
                "volume": unit_cell_volume(*unit_cell),
                }

    if merge:
        if output:
            print("Merging peak with same (hkl) ...", end="", flush=True)
        reflections = combine_hkl(reflections, exclude=exclude)
        if output:
            print("\rMerging peak with same (hkl) ... OK")
    else:
        reflections = reflections[:, :5]

    if output:
        print("Test space group and Generate unique reflection ...", end="", flush=True)
    a, b, c, al, be, ga = unit_cell
    if abs(a - b) < 0.01 and abs(b - c) < 0.01 and abs(al - be) < 0.1 and abs(
            be - ga) < 0.1 and al != 90 and be != 90 and ga != 90:
        is_R = True
    else:
        is_R = False
    rule_text, rule, sg_name = test_rules(reflections, space_group_number, extinction_rule, is_R=is_R)
    unique_reflections = generate_unique_reflections(reflections, space_group_number, unit_cell)
    forbidden_indices = mark_forbidden_reflections(unique_reflections, rule)
    unique_reflections = [reflection for idx, reflection in enumerate(unique_reflections) if
                          idx not in forbidden_indices]

    fourth_column = []
    for reflection in unique_reflections:
        try:
            fourth_column.append(float(reflection[3]))
        except ValueError:
            continue

    fourth_column = np.array(fourth_column)

    # Find the max and min values
    max_d = np.max(fourth_column)
    min_d = np.min(fourth_column)

    if output:
        print("\rTest space group and Generate unique reflection ... OK")

    if output:
        print("Analysis the statistics ...", end="", flush=True)

    multi_refls = mark_multiple_reflections(unique_reflections)
    reso_limit = calculate_resolution_limit(unique_reflections, multi_refls)

    if reso_limit == 999 and not reso:
        print(f"\nThe data {hkl_file} is really bad.")
        return {"mtime": os.path.getmtime(hkl_file),
                "space_group_number": space_group_number,
                "unit_cell": unit_cell}

    ideal_reflections = get_unique_ideal_reflection(unit_cell, space_group_number, min(min_d, reso) if reso else min_d,
                                                    rule=rule, MM=MM)

    if not ideal_reflections:
        print(f"\nHuge Unit Cell Detected in {hkl_file}.")
        return {"mtime": os.path.getmtime(hkl_file),
                "space_group_number": space_group_number,
                "unit_cell": unit_cell,
                "volume": unit_cell_volume(*unit_cell),
                }

    num_reso, isa_reso, r_values, cc12_reso = accumulate_statistics(unique_reflections, reso_limit)
    rint_reso, rmeas_reso, rexp_reso = r_values

    if not reso:
        ideal_unique_num = len(slice_reflections(ideal_reflections, 999, reso_limit))
        completeness = num_reso / ideal_unique_num
    else:
        ideal_unique_num = len(slice_reflections(ideal_reflections, 999, reso))
        completeness = len(slice_reflections(unique_reflections, 999, reso)) / ideal_unique_num

    slice_report = generate_slice_report(ideal_reflections, unique_reflections, multi_refls)
    if output:
        print("\rAnalysis the statistics ... OK")

    refl_reso = 0
    ideal_refl_reso = 0
    for item in slice_report:
        if item["high_res"] >= reso_limit:
            refl_reso += item["N_obs"]
            ideal_refl_reso += item["ideal_N"]

    # Compile information dictionary
    info_dict = {
        "mtime": os.path.getmtime(hkl_file),
        "max_res": np.round(max_d, 3),
        "min_res": np.round(min_d, 3),
        "space_group_number": space_group_number,
        "space_group_name": sg_name,
        "rule": rule_text,
        "unit_cell": unit_cell,
        "volume": np.round(unit_cell_volume(*unit_cell), 3),
        "refls_all": len(reflections),
        "refls_reso": refl_reso,
        "uniq_reso": num_reso,
        "multi_reso": round(refl_reso / num_reso, 2),
        "ideal_reso": len(slice_reflections(ideal_reflections, 999, reso_limit)),
        "completeness": round(100 * completeness, 2),
        "resolution": reso_limit,
        "isa": isa_reso,
        "rint": rint_reso,
        "rmeas": rmeas_reso,
        "rexp": rexp_reso,
        "cc12_reso": cc12_reso[0],
        "cc12_crit": cc12_reso[1],
        "slice_report": slice_report
    }

    return info_dict
