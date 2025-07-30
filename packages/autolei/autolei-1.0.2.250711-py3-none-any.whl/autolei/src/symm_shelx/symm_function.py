from __future__ import annotations
# Space Group and Laue Group Operations
import copy
import numpy as np


def get_laue_group(sg_no: int) -> str:
    """Determines the Laue group based on the space group number.

    Args:
        sg_no (int): Space group number.

    Returns:
        str: Laue group corresponding to the given space group number.
    """
    laue_groups = {
        range(1, 3): "-1",
        range(3, 16): "2/m",
        range(16, 75): "mmm",
        range(75, 89): "4/m",
        range(89, 143): "4/mmm",
        range(143, 149): "-3",
        range(149, 168): "-3m",
        range(168, 177): "6/m",
        range(177, 195): "6/mmm",
        range(195, 207): "m-3",
        range(207, 231): "m-3m"
    }
    for rg, laue in laue_groups.items():
        if sg_no in rg:
            if laue != "-3m":
                return laue
            else:
                if sg_no in [149, 151, 153, 157, 159, 162, 163]:
                    return "-31m"
                else:
                    return "-3m1"

    return "Invalid space group number"


# Symmetry Operations and Extinction Rules
def combine_rules(rules: dict) -> tuple:
    """Combines extinction rules into a condition string and a function.

    Args:
        rules (dict): Dictionary of extinction rules.

    Returns:
        tuple: A condition string (str) and a lambda function for evaluating
            extinction rules.
    """
    condition_dict = {
        "hkl": "",
        "0kl": "h == 0 and ",
        "h0l": "k == 0 and ",
        "hk0": "l == 0 and ",
        "h00": "k == 0 and l == 0 and ",
        "0k0": "h == 0 and l == 0 and ",
        "00l": "h == 0 and k == 0 and ",
        "2h-hl": "h == -2 * k and ",
        "h-2hl": "k == -2 * h and ",
        "hhl": "h == k and ",
        "h-hl": "h == -k and ",
        "hll": "k == l and ",
        "hl-l": "k == -l and ",
        "lk-l": "h == -l and ",
        "lkl": "h == l and "
    }

    combined_conditions = []
    rule_text = ""
    for rule_key, rule_expression in rules.items():
        rule_expression = rule_expression.replace(", ", " or ")
        rule_text += f"{rule_key}: {rule_expression}, "
        base_condition = condition_dict.get(rule_key, "")
        if not rule_expression:
            continue
        if base_condition:
            full_condition = f"({base_condition}({rule_expression}))"
        else:
            full_condition = f"({rule_expression})"
        combined_conditions.append(full_condition)

    if not combined_conditions:
        # If no conditions are combined, return a function that always returns False
        return "", lambda h, k, l: False
    # Combine all conditions with logical OR
    final_condition_str = " or ".join(combined_conditions)

    # Compile the combined condition into a Python function
    try:
        condition_func = eval(f"lambda h, k, l: {final_condition_str}")
    except Exception as e:
        raise ValueError(f"Error compiling extinction rules: {e}")

    return rule_text, condition_func


def test_rules(refls: list | np.array, sg_number: int, _rule: dict, is_R: bool = False) -> tuple:
    """Tests space group rules against reflection data.

    Args:
        refls (list): List of reflection data.
        sg_number (int): Space group number.
        _rule (dict): Extinction rule dictionary.
        is_R (bool, optional): Indicates rhombohedral cell. Defaults to False.

    Returns:
        tuple: Extinction rule text, a lambda function, and space group name.
    """

    def sum_intensity(forbidden_reflections, pos):
        total = 0.0
        for reflection in forbidden_reflections:
            intensity = reflection[pos]
            if isinstance(intensity, list):
                total += sum(intensity)
            else:
                total += intensity
        return total

    sub_sgs = _rule[sg_number].get("SG", [])

    if not sub_sgs:
        return "", "False", "Unknown"

    if is_R:
        return "", eval(f"lambda h, k, l: 0"), sub_sgs[0].get("name", "Unknown")[:-1] + "h"

    if len(sub_sgs) == 1:
        extinction_rules = sub_sgs[0].get("extinction", {})
        if extinction_rules:
            rule_text, combined_condition = combine_rules(extinction_rules)
            return rule_text, combined_condition, sub_sgs[0].get("name", "Unknown")
        else:
            return "", eval(f"lambda h, k, l: 0"), sub_sgs[0].get("name", "Unknown")

    best_rule = None
    best_name = "Unknown"
    rule = ""
    min_total_intensity = float('inf')

    # Determine if reflections have five columns
    try:
        has_five_columns = len(refls[0]) == 5 if refls else False
    except ValueError:
        has_five_columns = len(refls[0]) == 5 if refls.any() else False

    for sub_sg in sub_sgs:
        sg_name = sub_sg.get("name", "Unknown")
        extinction_rules = sub_sg.get("extinction", {})
        if not extinction_rules:
            continue  # Skip if no extinction rules are defined

        rule_text, combined_condition = combine_rules(extinction_rules)
        forbidden_indices = mark_forbidden_reflections(refls, combined_condition)
        forbidden_refls = [refls[idx] for idx in forbidden_indices]

        if not forbidden_refls:
            # No forbidden reflections, select this rule immediately
            return rule_text, combined_condition, sg_name

        intensity_pos = 3 if has_five_columns else 4
        total_intensity = sum_intensity(forbidden_refls, intensity_pos)

        if total_intensity < min_total_intensity:
            min_total_intensity = total_intensity
            best_rule = copy.deepcopy(combined_condition)  # Make a deep copy here
            best_name = sg_name
            rule = rule_text
        elif total_intensity == 0:
            best_rule = copy.deepcopy(combined_condition)  # And here
            best_name = sg_name
            rule = rule_text
            break

    if best_rule:
        return rule, best_rule, best_name
    else:
        return "", "False", "Unknown"


def mark_forbidden_reflections(refls: list, condition_func: callable) -> list:
    """Marks forbidden reflections based on a condition function.

    Args:
        refls (list): List of reflection data.
        condition_func (callable): Function to evaluate extinction conditions.

    Returns:
        list: Indices of forbidden reflections.
    """
    if condition_func is None:
        return []
    forbidden_indices = []
    for idx, reflection in enumerate(refls):
        h, k, l = reflection[:3]
        try:
            if condition_func(h, k, l):
                forbidden_indices.append(idx)
        except Exception as e:
            print(f"Error evaluating condition for reflection {reflection}: {e}")
            continue

    return forbidden_indices
