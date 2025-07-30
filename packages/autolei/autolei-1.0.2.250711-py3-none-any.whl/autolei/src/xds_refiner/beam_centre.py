import os
from functools import partial

import numpy as np
from scipy.optimize import differential_evolution, minimize
from scipy.spatial import cKDTree

from ..xds_input import replace_value, extract_keywords


def calculate_pairs_with_intensity_penalty(center: tuple, data_xy: np.ndarray, data_intensity: np.ndarray,
                                           tree: cKDTree, tolerance: float,
                                           intensity_penalty_factor: float = 0.25,
                                           min_distance_sq: float = 225.0) -> tuple:
    """
    Calculates pairs of points with intensity penalties based on a specified center.

    Args:
        center (tuple): Center coordinates (x, y).
        data_xy (np.ndarray): Array of data points' (x, y) coordinates.
        data_intensity (np.ndarray): Array of data points' intensities.
        tree (cKDTree): KDTree for efficient nearest-neighbor searches.
        tolerance (float): Tolerance distance for pairing.
        intensity_penalty_factor (float, optional): Penalty factor for unmatched intensities. Defaults to 0.25.
        min_distance_sq (float, optional): Minimum squared distance to consider valid pairs. Defaults to 225.0.

    Returns:
        tuple:
            - pairs_found (np.ndarray): Boolean array indicating which pairs were found.
            - score (float): Overall penalty score.
    """
    center_x, center_y = center
    reflected_points = 2 * np.array([center_x, center_y]) - data_xy  # Shape: (N, 2)

    # Calculate squared distances from the center
    delta = data_xy - center
    distances_sq = np.einsum('ij,ij->i', delta, delta)

    # Exclude points within a 15-pixel radius (15^2 = 225)
    valid_mask = distances_sq > min_distance_sq

    # Query the KDTree for nearest neighbors within tolerance
    valid_reflected = reflected_points[valid_mask]
    if valid_reflected.size == 0:
        # No valid points to process
        return np.array([], dtype=bool), 0.0

    distances, indices = tree.query(valid_reflected, distance_upper_bound=tolerance)

    # Determine which points have a valid pair
    pairs_found = distances < tolerance

    # Calculate penalty for unmatched pairs
    unmatched_intensities = data_intensity[valid_mask][~pairs_found]
    penalty = unmatched_intensities.sum() * intensity_penalty_factor

    # Calculate the score
    score = -pairs_found.sum() + penalty

    return pairs_found, score


def objective_pairs_with_intensity_penalty(center: tuple, data_xy: np.ndarray, data_intensity: np.ndarray,
                                           tree: cKDTree, tolerance: float,
                                           intensity_penalty_factor: float) -> float:
    """
    Objective function for optimizing pairs with intensity penalties.

    Args:
        center (tuple): Center coordinates (x, y).
        data_xy (np.ndarray): Array of data points' (x, y) coordinates.
        data_intensity (np.ndarray): Array of data points' intensities.
        tree (cKDTree): KDTree for efficient nearest-neighbor searches.
        tolerance (float): Tolerance distance for pairing.
        intensity_penalty_factor (float): Penalty factor applied to unmatched intensities.

    Returns:
        float: Penalty score, where a lower score indicates better optimization.
    """
    _, score = calculate_pairs_with_intensity_penalty(center, data_xy, data_intensity, tree, tolerance,
                                                      intensity_penalty_factor)
    return score


def objective_func_fixed(c: tuple, data_xy: np.ndarray, data_intensity: np.ndarray,
                         tree: cKDTree, tolerance: float, intensity_penalty_factor: float) -> float:
    """
    Fixed objective function for optimizing beam center positions.

    Args:
        c (tuple): Current center coordinates (x, y).
        data_xy (np.ndarray): Array of data points' (x, y) coordinates.
        data_intensity (np.ndarray): Array of data points' intensities.
        tree (cKDTree): KDTree for efficient nearest-neighbor searches.
        tolerance (float): Tolerance distance for pairing.
        intensity_penalty_factor (float): Penalty factor applied to unmatched intensities.

    Returns:
        float: Penalty score, where a lower score indicates better optimization.
    """
    return objective_pairs_with_intensity_penalty(c, data_xy, data_intensity, tree, tolerance, intensity_penalty_factor)


def optimise_beam_centre(fp: str,
                         length1: int = 1024,
                         length2: int = 1024,
                         tol_ratio: float = 0.003,
                         intensity_penalty_factor: float = 0.25) -> tuple:
    """
    Optimizes the beam center using intensity penalties and nearest neighbor searches.

    Args:
        fp (str): Path to the SPOT.XDS file.
        length1 (int, optional): Length of the image along axis 1. Defaults to 1024.
        length2 (int, optional): Length of the image along axis 2. Defaults to 1024.
        tol_ratio (float, optional): Tolerance ratio for pairing. Defaults to 0.003.
        intensity_penalty_factor (float, optional): Penalty factor for unmatched intensities. Defaults to 0.25.

    Returns:
        tuple: Optimized beam center coordinates (ORGX, ORGY).
    """
    tolerance = max(tol_ratio * max(length1, length2), 3)
    dtype = np.float32
    try:
        data = np.loadtxt(fp, usecols=(0, 1, 3), dtype=dtype)  # X, Y, Intensity
    except Exception as e:
        print(f"Error loading data from {fp}: {e}")
        return ()

    data_xy = data[:, :2]
    data_intensity = data[:, 2]

    # Normalize the intensity to a maximum of 100
    max_intensity = data_intensity.max()
    if max_intensity == 0:
        print("Maximum intensity is zero. Cannot normalize intensities.")
        return ()
    data_intensity = (data_intensity / max_intensity) * 100.0

    # Define bounds for optimization
    bounds = [(0.45 * length1, 0.55 * length1), (0.45 * length2, 0.55 * length2)]

    # Create a KDTree for efficient nearest neighbor search
    tree = cKDTree(data_xy)

    # Create a partial function with fixed parameters
    objective_func = partial(objective_func_fixed,
                             data_xy=data_xy,
                             data_intensity=data_intensity,
                             tree=tree,
                             tolerance=tolerance,
                             intensity_penalty_factor=intensity_penalty_factor)

    # Perform the global optimization using differential evolution
    result_de = differential_evolution(
        objective_func,
        bounds,
        strategy='best1bin',
        popsize=25,  # Reduced population size for speed; adjust as needed
        tol=0.01,
        workers=-1,  # Utilize all available CPU cores
        updating='deferred',  # Better memory management
        disp=False
    )
    initial_centre = result_de.x

    # Perform the local optimization using the result of the global optimization
    result_local = minimize(
        objective_func,
        initial_centre,
        method='L-BFGS-B',  # More memory-efficient than 'BFGS'
        options={'ftol': 1e-6, 'disp': False}
    )

    best_centre = result_local.x
    best_score = result_local.fun

    # Define a distance function using NumPy for efficiency
    def distance(vec1, vec2):
        return np.linalg.norm(vec1 - vec2) if not (np.array_equal(vec2, [512, 512]) or
                                                   np.array_equal(vec2, [1024, 1024])) else 0.0

    # If the score is larger than 0, perform another round of optimization with increased penalty
    if best_score > 0 or distance(best_centre, initial_centre) > 0.02 * length1:
        print("Score is larger than 0 or center moved significantly, performing refinement.")
        intensity_penalty_factor += 0.1  # Increase penalty factor

        # Create a new partial function with updated penalty factor
        objective_func_refined = partial(objective_func_fixed,
                                         data_xy=data_xy,
                                         data_intensity=data_intensity,
                                         tree=tree,
                                         tolerance=tolerance,
                                         intensity_penalty_factor=intensity_penalty_factor)

        # Perform refined global optimization
        result_de_refined = differential_evolution(
            objective_func_refined,
            bounds,
            strategy='best1bin',
            popsize=15,  # Further reduced for speed
            tol=0.01,
            workers=-1,
            updating='deferred',
            disp=False
        )
        refined_centre = result_de_refined.x

        # Perform refined local optimization
        result_local_refined = minimize(
            objective_func_refined,
            refined_centre,
            method='L-BFGS-B',
            options={'ftol': 1e-6, 'disp': False}
        )

        # Update best_centre if the refined score is better
        if result_local_refined.fun < best_score:
            best_centre = result_local_refined.x
            best_score = result_local_refined.fun

    print("Best Centre:", best_centre)
    print("Best Score:", best_score)

    # Optionally plot the results (commented out for speed; enable if needed)
    pairs_found, _ = calculate_pairs_with_intensity_penalty(
        best_centre, data_xy, data_intensity, tree, tolerance, intensity_penalty_factor)
    print("Pairs Found:", np.sum(pairs_found), f"/ {len(data_xy)}\n")

    return best_centre


def refine_beam_centre(path: str) -> None:
    """
    Refines the beam center by optimizing the ORGX and ORGY parameters.

    Args:
        path (str): Path to the directory containing XDS files.

    Returns:
        None
    """
    inp_path = os.path.join(path, "XDS.INP")
    spot_path = os.path.join(path, "SPOT.XDS")
    if not os.path.exists(inp_path):
        print("You should write the XDS.INP file first.")
        return
    elif not os.path.exists(spot_path):
        print("You should run XDS first.")
        return
    else:
        # Extract parameters from XDS.INP
        with open(inp_path, "r", errors="replace") as f:
            lines = f.readlines()
        input_parameter_dict = extract_keywords(lines)

        # Optimize beam center
        centre = optimise_beam_centre(
            spot_path,
            length1=int(input_parameter_dict.get("NX", [1024])[0]),
            length2=int(input_parameter_dict.get("NY", [1024])[0]),
        )
        if centre is None:
            print("Beam center optimization failed.")
            return

    # Update XDS.INP with the new center
    with open(inp_path, "r") as f:
        lines = f.readlines()

    new_orgx = f"{centre[0]:.3f}"
    new_orgy = f"{centre[1]:.3f}"
    lines = replace_value(lines, "ORGX", [new_orgx], comment=False)
    lines = replace_value(lines, "ORGY", [new_orgy], comment=False)

    with open(inp_path, "w") as f:
        f.writelines(lines)

    print(f"Updated beam center to ORGX={new_orgx}, ORGY={new_orgy} in {inp_path}")
