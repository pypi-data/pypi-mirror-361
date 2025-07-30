from __future__ import annotations

import os
import re
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Any

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Circle
from numpy import ndarray
from scipy.spatial import cKDTree

from autolei.src.xds_input import extract_keywords


def read_hkl_from_spot_xds(file_path: str) -> np.ndarray:
    """
    Reads the SPOT.XDS file and returns the data as a numpy array.

    For a 7-column file, the expected columns are:
        [x, y, z, I, h, k, l]
    and the function returns:
        [h, k, l, I, x, y, z]

    For a 4-column file, it is assumed the file contains:
        [I, x, y, z]
    and since h, k, l are not available, they are replaced with zeros.
    The returned array will then be:
        [0, 0, 0, I, x, y, z]

    Parameters:
    - file_path (str): Path to the directory containing SPOT.XDS.

    Returns:
    - np.ndarray: Numpy array with columns [h, k, l, I, x, y, z].
    """
    full_path = os.path.join(file_path, "SPOT.XDS")
    data = np.loadtxt(full_path)

    # Ensure data is 2D (in case of a single line file)
    if data.ndim == 1:
        data = data[np.newaxis, :]

    if data.shape[1] == 7:
        # Rearrange columns: from [x, y, z, I, h, k, l] to [h, k, l, I, x, y, z]
        data = data[:, [4, 5, 6, 3, 0, 1, 2]]
    elif data.shape[1] == 4:
        # Assume columns are [I, x, y, z] and prepend zeros for h, k, l.
        zeros = np.zeros((data.shape[0], 3))
        data = np.hstack((zeros, data[:, [3, 0, 1, 2]]))
    else:
        raise ValueError("Unexpected number of columns in SPOT.XDS file. "
                         "Expected either 4 or 7 columns.")

    return data


def read_hkl_from_xds_ascii(file_path: str, ratio_cutoff: float = 1.0) -> np.ndarray:
    """
    Reads XDS_ASCII.HKL, filters out reflections with I/sigma(I) < ratio_cutoff,
    and returns the data with columns [h, k, l, I, x, y, z].

    Parameters:
    - file_path (str): Directory containing XDS_ASCII.HKL.
    - ratio_cutoff (float): Minimum allowed I/sigma(I) ratio (default: 2.0).

    Returns:
    - np.ndarray: Filtered array with columns [h, k, l, I, x, y, z].
    """
    # Load h,k,l,I,sigma,x,y,z
    all_data = np.loadtxt(
        os.path.join(file_path, "XDS_ASCII.HKL"),
        usecols=(0, 1, 2, 3, 4, 5, 6, 7),
        comments='!'
    )

    I = all_data[:, 3]
    sigma = all_data[:, 4]
    mask = (I / np.abs(sigma)) >= ratio_cutoff

    # Keep only rows passing the cutoff
    filtered = all_data[mask]

    # Drop the sigma column, returning [h, k, l, I, x, y, z]
    return filtered[:, [0, 1, 2, 3, 5, 6, 7]]


def read_hkl_merged(file_path: str, ratio_cutoff: float = 1.0) -> tuple:
    """
    Reads the all.HKL file, merges reflections with the same (h, k, l) integer indices,
    and returns the merged data with weighted averaged intensity, plus the reciprocal-space
    coordinates (x, y, z) of each reflection and its magnitude d_star (= 1/d).

    Parameters:
    - file_path (str): Path to the directory containing all.HKL.

    Returns:
    - tuple: (unit_cell, merged_data) where
      * unit_cell is the unit cell parameters extracted from the HKL file [a, b, c, alpha, beta, gamma].
      * merged_data is a NumPy array with columns:
        [h, k, l, I_avg, x, y, z, h_int, k_int, l_int, d_star].
    """
    hkl_path = os.path.join(file_path, "all.HKL")

    # Check if the file exists
    if not os.path.isfile(hkl_path):
        raise FileNotFoundError(f"The file {hkl_path} does not exist.")

    try:
        # Load columns [h, k, l, I, sigma_I]
        all_data = np.loadtxt(hkl_path, usecols=(0, 1, 2, 3, 4), comments='!')
        I = all_data[:, 3]
        sigma = all_data[:, 4]
        mask = (I / np.abs(sigma)) >= ratio_cutoff
        # Keep only rows passing the cutoff
        data = all_data[mask]

        # Parse out unit cell constants if present
        unit_cell = None
        with open(hkl_path, 'r') as file:
            for line in file:
                if "!UNIT_CELL_CONSTANTS" in line:
                    parts = line.split("=")
                    if len(parts) > 1:
                        unit_cell_parts = parts[1].split()
                        if len(unit_cell_parts) == 6:
                            unit_cell = [float(x) for x in unit_cell_parts]
                    break
    except Exception as e:
        raise ValueError(f"Error reading the HKL file: {e}")

    if unit_cell is None:
        raise ValueError("Unit cell parameters not found in the HKL file.")

    # Convert data into a DataFrame
    df = pd.DataFrame(data, columns=['h', 'k', 'l', 'I', 'sigma_I'])

    # Integer indices
    df['h_int'] = df['h'].astype(int)
    df['k_int'] = df['k'].astype(int)
    df['l_int'] = df['l'].astype(int)

    # Precompute weights (1 / sigma_I^2) and weighted intensities
    df['weight'] = 1.0 / (df['sigma_I'] ** 2)
    df['I_weighted'] = df['I'] * df['weight']

    # Aggregate by integer h, k, l
    grouped = df.groupby(['h_int', 'k_int', 'l_int'], sort=False).agg(
        h=('h', 'mean'),
        k=('k', 'mean'),
        l=('l', 'mean'),
        I_sum=('I_weighted', 'sum'),
        w_sum=('weight', 'sum')
    ).reset_index()

    # Compute weighted average intensity
    grouped['I_avg'] = grouped['I_sum'] / grouped['w_sum']

    # Filter out negative intensities if needed
    filtered_grouped = grouped[grouped['I_avg'] >= 0].copy()

    # Extract unit cell parameters
    a, b, c, alpha, beta, gamma = unit_cell

    # Convert angles to radians
    alpha_r = np.radians(alpha)
    beta_r = np.radians(beta)
    gamma_r = np.radians(gamma)

    # Direct lattice vectors in Cartesian coords (for a general triclinic cell)
    a1 = np.array([a, 0.0, 0.0])
    a2 = np.array([
        b * np.cos(gamma_r),
        b * np.sin(gamma_r),
        0.0
    ])

    # For the third vector, we use the standard relationships:
    cx = c * np.cos(beta_r)
    cy = c * (np.cos(alpha_r) - np.cos(beta_r) * np.cos(gamma_r)) / np.sin(gamma_r)
    cz = np.sqrt(c ** 2 - cx ** 2 - cy ** 2)
    a3 = np.array([cx, cy, cz])

    # Volume of the unit cell in Cartesian
    volume = np.dot(a1, np.cross(a2, a3))

    # Reciprocal lattice vectors (b1, b2, b3)
    # Each has a factor of 2π
    b1 = np.cross(a2, a3) / volume
    b2 = np.cross(a3, a1) / volume
    b3 = np.cross(a1, a2) / volume

    # Compute reciprocal coords (x, y, z) and d_star = 1/d for each reflection
    xs = []
    ys = []
    zs = []
    d_stars = []

    for idx, row in filtered_grouped.iterrows():
        hi = row['h_int']
        ki = row['k_int']
        li = row['l_int']
        # Reciprocal vector R = h*b1 + k*b2 + l*b3
        R = hi * b1 + ki * b2 + li * b3
        # x, y, z in reciprocal space
        xs.append(R[0])
        ys.append(R[1])
        zs.append(R[2])
        # d_star = |R| / 2π, where |R|=2π/d
        magR = np.linalg.norm(R)
        d_stars.append(magR)

    filtered_grouped['x'] = xs
    filtered_grouped['y'] = ys
    filtered_grouped['z'] = zs
    filtered_grouped['d_star'] = d_stars

    # Final arrangement
    merged_df = filtered_grouped[[
        'h', 'k', 'l', 'I_avg', 'x', 'y', 'z',
        'h_int', 'k_int', 'l_int', 'd_star'
    ]].copy()

    # Convert to NumPy array
    merged_data = merged_df.to_numpy()

    return unit_cell, merged_data


# noinspection PyTypeChecker
def extract_cell_GPRAM(xds_path: str, file_name: str) -> Dict[str, Any]:
    """
    Parses XPARM.XDS or GXPARM.XDS and extracts diffraction parameters.

    Parameters:
        xds_path (str): Directory path where the file is located.
        file_name (str): Name of the file (XPARM.XDS or GXPARM.XDS).
    Returns:
        Dict[str, Any]: A dictionary containing extracted parameters.
    """
    file_path = os.path.join(xds_path, file_name)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File '{file_name}' does not exist in '{xds_path}'.")

    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    if not lines:
        raise ValueError(f"The file '{file_name}' is empty.")

    keyword = lines[0].split()[0]
    if keyword not in {'XPARM.XDS', 'GXPARM.XDS'}:
        raise ValueError(f"File '{file_name}' does not start with 'XPARM.XDS' or 'GXPARM.XDS' keyword.")

    data = {'keyword': keyword}
    if len(lines) < 12:
        raise ValueError(f"File '{file_name}' does not contain the required number of header lines (12).")

    def to_floats(s: str) -> List[float]:
        return list(map(float, s.split()))

    try:
        # Line 2
        line2 = to_floats(lines[1])
        if len(line2) < 6:
            raise ValueError("Line 2 does not contain enough parameters.")
        data.update({
            'start_frame': line2[0],
            'phi_0': line2[1],
            'phi_osc': line2[2],
            'rotation_axis': line2[3:6]
        })

        # Line 3
        line3 = to_floats(lines[2])
        if len(line3) < 4:
            raise ValueError("Line 3 does not contain enough parameters.")
        data.update({
            'wavelength': line3[0],
            'INCIDENT_BEAM_WAVEVECTOR': line3[1:4]
        })

        # Line 4
        line4 = to_floats(lines[3])
        if len(line4) < 7:
            raise ValueError("Line 4 does not contain enough parameters.")
        data['sg_no'] = int(line4[0])
        data['unit_cell'] = (float(line4[1]), float(line4[2]), float(line4[3]),
                             float(line4[4]), float(line4[5]), float(line4[6]))

        # Lines 5-7: Unit cell axes
        axes_names = ['a_axis', 'b_axis', 'c_axis']
        for i, axis in enumerate(axes_names, start=4):
            axis_line = to_floats(lines[i])
            if len(axis_line) < 3:
                raise ValueError(f"Line {i + 1} does not contain enough parameters for {axis}.")
            data[axis] = axis_line[:3]

        # Line 8: Detector info
        line8 = to_floats(lines[7])
        if len(line8) < 5:
            raise ValueError("Line 8 does not contain enough parameters.")
        data.update({
            'NUMBER_OF_DETECTOR_SEGMENTS': int(line8[0]),
            'pixel_no_x': int(line8[1]),
            'pixel_no_y': int(line8[2]),
            'pixel_size_x': line8[3],
            'pixel_size_y': line8[4]
        })

        # Line 9: Origin
        line9 = to_floats(lines[8])
        if len(line9) < 3:
            raise ValueError("Line 9 does not contain enough parameters.")
        data.update({
            'ORGX': line9[0],
            'ORGY': line9[1],
            'cl': line9[2]
        })

        # Lines 10-12: Detector axes and normal
        detector_axes = ['DETECTOR_X_AXIS', 'DETECTOR_Y_AXIS', 'DETECTOR_NORMAL']
        for i, axis in enumerate(detector_axes, start=9):
            axis_line = to_floats(lines[i])
            if len(axis_line) < 3:
                raise ValueError(f"Line {i + 1} does not contain enough parameters for {axis}.")
            data[axis] = axis_line[:3]

        # Detector segments
        num_segments = data['NUMBER_OF_DETECTOR_SEGMENTS']
        expected_segment_lines = num_segments * 2
        actual_segment_lines = len(lines) - 12
        if actual_segment_lines != expected_segment_lines:
            raise ValueError(
                f"Expected {expected_segment_lines} lines for detector segments, found {actual_segment_lines}."
            )

        detector_segments: List[Dict[str, Any]] = []
        for seg_idx in range(num_segments):
            base = 12 + seg_idx * 2
            # First line: iseg, x1, x2, y1, y2
            seg_line1 = to_floats(lines[base])
            if len(seg_line1) < 5:
                raise ValueError(f"Detector segment {seg_idx + 1} line 1 does not contain enough parameters.")
            seg_info = {
                'iseg': int(seg_line1[0]),
                'x1': int(seg_line1[1]),
                'x2': int(seg_line1[2]),
                'y1': int(seg_line1[3]),
                'y2': int(seg_line1[4])
            }

            # Second line: ORGXS, ORGYS, FS, EDS (6 components expected)
            seg_line2 = to_floats(lines[base + 1])
            if len(seg_line2) < 9:
                raise ValueError(f"Detector segment {seg_idx + 1} line 2 does not contain enough parameters.")
            seg_info.update({
                'ORGXS': seg_line2[0],
                'ORGYS': seg_line2[1],
                'FS': seg_line2[2],
                'EDS': seg_line2[3:9]
            })

            detector_segments.append(seg_info)

        data['DETECTOR_SEGMENTS'] = detector_segments

    except ValueError as ve:
        raise ValueError(f"Error parsing file '{file_name}': {ve}")

    return data


def parse_xds_inp(file_path: str) -> Dict[str, Any]:
    """
    Parses XDS.INP file to extract relevant parameters.

    Parameters:
        file_path (str): Path to the directory containing XDS.INP.

    Returns:
        dict: A dictionary containing extracted parameters.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is incorrect or missing required parameters.
    """
    fn = os.path.join(file_path, "XDS.INP")
    try:
        with open(fn, "r") as f:
            params = extract_keywords(f.readlines())
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {fn} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading {fn}: {e}")

    rotx, roty, rotz = map(float, params["ROTATION_AXIS"][0].split()[:3])

    metainfo = {
        "ORGX": float(params["ORGX"][0]),
        "ORGY": float(params["ORGY"][0]),
        "phi_osc": float(params["OSCILLATION_RANGE"][0]),
        "pixel_size_x": float(params["X-RAY_WAVELENGTH"][0]),
        "wavelength": float(params["X-RAY_WAVELENGTH"][0]),
        "cl": float(params["DETECTOR_DISTANCE"][0]),
        "phi_0": float(params.get("OSCILLATION_RANGE", [0.0])[0]),
        "rotation_axis": np.array([rotx, roty, rotz])
    }

    return metainfo


def merge_two_reflection_files(
        ascii_hkl: np.ndarray, spot: np.ndarray, xy_error: float = 2.0, z_error: float = 10.0
) -> np.ndarray:
    """
    Scales and adds new reflections from 'spot' to 'ascii_hkl' using a global scaling factor.
    Existing reflections in 'ascii_hkl' are not modified.

    Parameters:
    - ascii_hkl (np.ndarray): Existing ASCII HKL data with columns [h, k, l, I, x, y, z].
    - spot (np.ndarray): Spot reflections with columns [h, k, l, I_spot, x, y, z].
    - xy_error (float): Tolerance for matching in x and y dimensions.
    - z_error (float): Tolerance for matching in the z dimension.

    Returns:
    - np.ndarray: Updated 'ascii_hkl' with additional scaled reflections from 'spot'.
    """
    # Step 1: Filter out reflections with non-positive intensities
    ascii_hkl = ascii_hkl[ascii_hkl[:, 3] >= 0]
    spot = spot[spot[:, 3] >= 0]

    if ascii_hkl.size == 0:
        raise ValueError("ascii_hkl is empty after filtering negative intensities.")

    if spot.size == 0:
        # No spot reflections to merge; return ascii_hkl as is
        return ascii_hkl

    # Step 2: Build a cKDTree for efficient spatial queries
    tree = cKDTree(ascii_hkl[:, 4:7])  # Columns [x, y, z]

    # Step 3: Define the maximum Euclidean distance corresponding to the box tolerances
    max_radius = np.sqrt(xy_error ** 2 + xy_error ** 2 + z_error ** 2)

    # Step 4: Query the tree for potential matches within the max_radius
    spot_coords = spot[:, 4:7]  # Columns [x, y, z]
    candidate_indices = tree.query_ball_point(spot_coords, r=max_radius)

    # Initialize lists to store matched intensities
    matched_I_ascii = []
    matched_I_spot = []

    # Initialize a mask to identify matched spots
    matched_spots_mask = np.zeros(len(spot), dtype=bool)

    # Step 5: Iterate through each spot reflection and find matches
    for i, candidates in enumerate(candidate_indices):
        if not candidates:
            continue  # No candidates found for this spot

        # Compute absolute differences between spot and candidate ascii_hkl reflections
        diffs = np.abs(ascii_hkl[candidates, 4:7] - spot_coords[i])

        # Determine which candidates are within the specified tolerances
        within_tolerance = np.all(diffs < np.array([xy_error, xy_error, z_error]), axis=1)

        if np.any(within_tolerance):
            # Select the first matching ascii_hkl reflection
            first_match_idx = candidates[np.argmax(within_tolerance)]
            matched_I_ascii.append(ascii_hkl[first_match_idx, 3])  # I from ascii_hkl
            matched_I_spot.append(spot[i, 3])  # I_spot from spot
            matched_spots_mask[i] = True

    if len(matched_I_ascii) == 0:
        raise ValueError("No matching reflections found within the specified tolerances.")

    # Convert lists to NumPy arrays for efficient computation
    matched_I_ascii = np.array(matched_I_ascii)
    matched_I_spot = np.array(matched_I_spot)

    # Step 6: Compute the scaling factor analytically (Least Squares Solution)
    # scale = sum(I_ascii * I_spot) / sum(I_ascii^2)
    numerator = np.sum(matched_I_ascii * matched_I_spot)
    denominator = np.sum(matched_I_ascii ** 2)

    if denominator == 0:
        raise ZeroDivisionError("Denominator in scaling factor calculation is zero.")

    global_scale = numerator / denominator

    # Step 7: Identify unmatched spot reflections
    unmatched_spots = spot[~matched_spots_mask]

    # Step 8: Scale unmatched spot intensities and set hkl to [0, 0, 0]
    if unmatched_spots.size > 0:
        # Ensure unmatched_spots is 2D for consistent stacking
        if unmatched_spots.ndim == 1:
            unmatched_spots = unmatched_spots.reshape(1, -1)

        scaled_new_reflections = unmatched_spots.copy()

        # Scale the intensities
        # Original logic: scaled_I = I_spot / (5 * global_scale)
        scaled_new_reflections[:, 3] /= (5 * global_scale)

        # Set hkl to [0, 0, 0]
        scaled_new_reflections[:, 0:3] = 0

        # Append the scaled new reflections to ascii_hkl
        ascii_hkl = np.vstack([ascii_hkl, scaled_new_reflections])

    return ascii_hkl


def cell_to_matrix(a: float, b: float, c: float, alpha: float, beta: float, gamma: float) -> tuple:
    """Converts unit cell parameters to matrix form.

    Args:
        a (float): Unit cell parameter a.
        b (float): Unit cell parameter b.
        c (float): Unit cell parameter c.
        alpha (float): Unit cell angle alpha in degrees.
        beta (float): Unit cell angle beta in degrees.
        gamma (float): Unit cell angle gamma in degrees.

    Returns:
        np.ndarray: Matrix representation of the unit cell.
    """
    alpha_rad, beta_rad, gamma_rad = np.radians([alpha, beta, gamma])
    cos_alpha, cos_beta, cos_gamma = np.cos([alpha_rad, beta_rad, gamma_rad])
    sin_gamma = np.sin(gamma_rad)

    v_a = np.array([a, 0, 0])
    v_b = np.array([b * cos_gamma, b * sin_gamma, 0])
    v_c_x = c * cos_beta
    v_c_y = c * (cos_alpha - cos_beta * cos_gamma) / sin_gamma
    v_c_z = c * np.sqrt(1 - cos_beta ** 2 - ((cos_alpha - cos_beta * cos_gamma) / sin_gamma) ** 2)
    v_c = np.array([v_c_x, v_c_y, v_c_z])

    return (v_a, v_b, v_c)


def read_hkl(folder_path: str, mode: str = None) -> tuple:
    """
    Reads reflection data and cell info from specified folder.
    """
    if os.path.exists(os.path.join(folder_path, "XDS_ASCII.HKL")) and mode in [None, "Index&&HKL"]:
        ascii_hkl = read_hkl_from_xds_ascii(folder_path)
        spot = read_hkl_from_spot_xds(folder_path)
        cell_info = extract_cell_GPRAM(folder_path, "GXPARM.XDS")
        return cell_info, merge_two_reflection_files(ascii_hkl, spot), "xds_ascii"
    elif os.path.exists(os.path.join(folder_path, "XPARM.XDS")):
        cell_info = extract_cell_GPRAM(folder_path, "XPARM.XDS")
        return cell_info, read_hkl_from_spot_xds(folder_path), "index"
    elif os.path.exists(os.path.join(folder_path, "all.HKL")):
        unit_cell, ascii_hkl = read_hkl_merged(folder_path)
        cell_matrix = cell_to_matrix(*tuple(map(float, unit_cell)))
        cell_info = {
            "unit_cell": tuple(map(float, unit_cell)),
            "a_axis": cell_matrix[0],
            "b_axis": cell_matrix[1],
            "c_axis": cell_matrix[2]
        }
        return cell_info, ascii_hkl, "merged"
    elif os.path.exists(os.path.join(folder_path, "SPOT.XDS")):
        return parse_xds_inp(folder_path), read_hkl_from_spot_xds(folder_path), "index"
    else:
        raise ValueError("Folder does not contain SPOT.XDS or XDS_ASCII.HKL.")


def rotate_vector(vec: np.ndarray, axis: np.ndarray, angle_deg: float) -> np.ndarray:
    """
    Rotate vector 'vec' about 'axis' by 'angle_deg' degrees using Rodrigues' rotation formula.
    The axis should be a normalized vector.
    """
    angle = np.radians(angle_deg)
    k = axis / np.linalg.norm(axis)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    return vec * cos_a + np.cross(k, vec) * sin_a + k * np.dot(k, vec) * (1 - cos_a)


def reflections_to_reciprocal_space(
        reflections: np.ndarray,
        wavelength: float,
        phi_0: float,
        phi_osc: float,
        rotation_axis: List[float],
        pixel_size: float,
        x0: float,
        y0: float,
        CL: float
) -> ndarray:
    """
    Convert (x, y, z) reflections to reciprocal space coordinates.

    Parameters:
    - reflections: (N,3) array [x_pix, y_pix, z_frame]
    - wavelength: float (Å)
    - phi_0: starting angle (deg)
    - phi_osc: oscillation range per frame (deg)
    - rotation_axis: axis of rotation (3,)
    - pixel_size: pixel size (mm)
    - x0, y0: beam center (pixels)
    - CL: detector distance (mm)

    Returns:
    - s_crystal: (N,3) scattering vectors in crystal frame (Å^-1).
    """
    mm_to_A = 1e7
    pixel_size_A = pixel_size * mm_to_A
    CL_A = CL * mm_to_A
    k_scale = 1 / wavelength

    rotation_axis = np.array(rotation_axis, dtype=float) / np.linalg.norm(rotation_axis)
    s_crystal = np.zeros((len(reflections), 3))

    for i, (x_pix, y_pix, z_frame) in enumerate(reflections):
        phi = phi_0 + z_frame * phi_osc

        X = (x_pix - x0) * pixel_size_A
        Y = (y_pix - y0) * pixel_size_A

        denom = np.sqrt(X ** 2 + Y ** 2 + CL_A ** 2)
        k_out_dir = np.array([X / denom, Y / denom, CL_A / denom])

        k_in = np.array([0, 0, k_scale])
        k_out = k_scale * k_out_dir
        s_lab = k_out - k_in
        s_crys = rotate_vector(s_lab, rotation_axis, -phi)
        s_crystal[i] = s_crys

    return s_crystal


def convert_cartesian_to_hkl(points, a_vec, b_vec, c_vec):
    """
    Converts Cartesian coordinates to (h,k,l) given reciprocal basis vectors.

    Parameters:
    - points: Nx3 array [x, y, z]
    - a_vec, b_vec, c_vec: reciprocal lattice vectors

    Returns:
    - Nx3 array of (h, k, l)
    """
    basis_matrix = np.column_stack((a_vec, b_vec, c_vec))
    det = np.linalg.det(basis_matrix)
    if np.isclose(det, 0):
        raise ValueError("Basis matrix is singular.")

    inv_basis = np.linalg.inv(basis_matrix)
    abc_list = [inv_basis @ np.array(p) for p in points]
    return np.array(abc_list)


def transform_points(
        refls: np.ndarray,
        cell_info: dict,
        a_star: np.ndarray,
        b_star: np.ndarray,
        c_star: np.ndarray
) -> np.ndarray:
    """
    Transforms reflection points from detector coordinates to reciprocal space (hkl).
    Filters reflections to include only those within a distance of 0.03 from the origin in reciprocal space.
    """
    # Extract necessary parameters
    x0, y0 = cell_info["ORGX"], cell_info["ORGY"]
    phi_osc = cell_info["phi_osc"]
    pixel_size = cell_info["pixel_size_x"]
    wavelength = cell_info["wavelength"]
    CL = cell_info["cl"]
    phi_0 = cell_info["phi_0"]
    rotation_axis = np.array(cell_info["rotation_axis"])
    rotation_axis /= np.linalg.norm(rotation_axis)

    # Extract reflection data
    x_pix = refls[:, 4]
    y_pix = refls[:, 5]
    z_frame = refls[:, 6]

    # Compute phi angles for each frame
    phi = phi_0 + z_frame * phi_osc

    # Convert pixel coordinates to Å
    pixel_size_A = pixel_size * 1e7
    CL_A = CL * 1e7
    X = (x_pix - x0) * pixel_size_A
    Y = (y_pix - y0) * pixel_size_A

    # Scattered beam direction
    denom = np.sqrt(X ** 2 + Y ** 2 + CL_A ** 2)
    k_out_dir = np.vstack((X / denom, Y / denom, CL_A / denom)).T

    # Scattering vectors in lab frame
    k_scale = 1 / wavelength
    s_lab = k_scale * k_out_dir - np.array([0, 0, k_scale])

    # Rotation matrices via Rodrigues' formula
    cos_phi = np.cos(np.radians(-phi))
    sin_phi = np.sin(np.radians(-phi))
    ux, uy, uz = rotation_axis
    R = np.empty((len(phi), 3, 3))
    R[:, 0, 0] = cos_phi + ux * ux * (1 - cos_phi)
    R[:, 0, 1] = ux * uy * (1 - cos_phi) - uz * sin_phi
    R[:, 0, 2] = ux * uz * (1 - cos_phi) + uy * sin_phi
    R[:, 1, 0] = uy * ux * (1 - cos_phi) + uz * sin_phi
    R[:, 1, 1] = cos_phi + uy * uy * (1 - cos_phi)
    R[:, 1, 2] = uy * uz * (1 - cos_phi) - ux * sin_phi
    R[:, 2, 0] = uz * ux * (1 - cos_phi) - uy * sin_phi
    R[:, 2, 1] = uz * uy * (1 - cos_phi) + ux * sin_phi
    R[:, 2, 2] = cos_phi + uz * uz * (1 - cos_phi)

    # Apply rotation to get crystal-frame vectors
    s_crystal = np.einsum('ijk,ik->ij', R, s_lab)
    norms = np.linalg.norm(s_crystal, axis=1)

    # Prepare transformed array
    if np.all(a_star == 0) or np.all(b_star == 0) or np.all(c_star == 0):
        transformed = np.hstack((refls[:, :4], s_crystal, refls[:, :3], norms[:, None]))
    else:
        hkl = convert_cartesian_to_hkl(s_crystal, a_star, b_star, c_star)
        # adjust shift
        h_orig = refls[:, 0].astype(float)
        k_orig = refls[:, 1].astype(float)
        l_orig = refls[:, 2].astype(float)
        mask_orig = (h_orig != 0) | (k_orig != 0) | (l_orig != 0)
        if np.any(mask_orig):
            hkl_orig = np.vstack((h_orig, k_orig, l_orig)).T
            shift = hkl[mask_orig] - hkl_orig[mask_orig]
            mean_shift = np.mean(shift, axis=0)
            hkl = hkl - mean_shift
        transformed = np.hstack((refls[:, :4], s_crystal, hkl, norms[:, None]))

    # Filter reflections within 0.03 of origin
    mask = norms >= 0.02
    return transformed[mask]


def filter_scattering_vectors(s_vectors, min_distance, max_distance):
    """
    Filter scattering vectors based on their Euclidean distance from the origin.

    Parameters:
        s_vectors (np.ndarray): Nx10 array containing [h, k, l, I, x, y, z, ...].
        min_distance (float): Minimum allowed distance from the origin. Points closer than this are removed.
        max_distance (float): Maximum allowed distance from the origin. Points farther than this are removed.

    Returns:
        filtered_vectors (np.ndarray): Array of scattering vectors that lie within the specified distance range.
    """
    # Compute Euclidean distance from the origin
    distances = s_vectors[:, 10]
    # Create a boolean mask for points within the specified range
    mask = (distances >= min_distance) & (distances <= max_distance)
    return s_vectors[mask]


def plot_reciprocal_space_3D(
        s_vectors,
        a_star,
        b_star,
        c_star,
        show_intensity: bool = False,
        show_points: str = "all",
        spot_size: float = 20.0,
        min_reso: float = 0.1,
        max_reso: float = 30,
        view_direction: str | None = None,
        ax=None,
        *,
        arrow_linewidth: float = 3.0,
        arrow_head_ratio: float = 0.05,
        arrow_head_width_scale: float = 0.005,
):
    """Plot a 3‑D reciprocal‑space map with basis‑vector arrows.

    *Head height* scales with the vector length (`arrow_head_ratio`).
    *Head width* now scales with the **line width** (``arrow_head_width_scale × arrow_linewidth``),
    ensuring consistent proportions irrespective of arrow length.
    """

    # ---------------------------------------------------------------
    # Filter by resolution
    s_vectors = filter_scattering_vectors(s_vectors, 1 / max_reso, 1 / min_reso)

    # Unpack columns
    hkl = s_vectors[:, 0:3]
    intens = s_vectors[:, 3]
    X, Y, Z = s_vectors[:, 4:7].T

    # ------------------------ marker sizes ------------------------
    if show_intensity:
        sizes = np.sqrt(intens)
        sizes = spot_size * 3 * (sizes / np.max(sizes))
    else:
        sizes = spot_size

    # ------------------------- colours ---------------------------
    if show_points == "indexed":
        mask = (hkl != 0).any(axis=1)
        colours = np.where(mask, "k", "none")
    elif show_points == "unindexed":
        mask = (hkl == 0).all(axis=1)
        colours = np.where(mask, "r", "none")
    else:
        mask = (hkl != 0).any(axis=1)
        colours = np.where(mask, "k", "r")

    # ----------------------- figure/axes -------------------------
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d", proj_type="ortho")
    else:
        fig = ax.figure
        ax.cla()

    ax.scatter(X, Y, Z, c=colours, s=sizes)

    # ---------------------- axis limits --------------------------
    max_range = min(0.616 / min_reso, np.max(np.abs([X, Y, Z])))
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])

    ax.set_xlabel("X (rotated)")
    ax.set_ylabel("Y (rotated)")
    ax.set_zlabel("Z (rotated)")
    ax.set_title("Reciprocal‑space 3‑D view")

    # -------------------------------------------------------------
    # Helper: draw a 3‑D arrow (shaft line + pyramid head)
    # -------------------------------------------------------------
    def _draw_arrow(vector, colour, label):
        vec = np.asarray(vector, dtype=float)
        vec_len = np.linalg.norm(vec)
        if vec_len == 0:
            return

        # Head dimensions
        head_len = arrow_head_ratio * vec_len  # scales with arrow length
        head_half_width = arrow_head_width_scale * arrow_linewidth / 2  # scales with line width

        direction = vec / vec_len
        shaft_end = vec - head_len * direction

        # Shaft
        ax.plot([0, shaft_end[0]], [0, shaft_end[1]], [0, shaft_end[2]],
                color=colour, linewidth=arrow_linewidth)

        # Create orthonormal basis {u, v, w}
        w = direction
        tmp = np.array([0, 0, 1]) if abs(w[2]) < 0.9 else np.array([0, 1, 0])
        u = np.cross(w, tmp)
        u /= np.linalg.norm(u)
        v = np.cross(w, u)

        base_centre = shaft_end
        p1 = base_centre + head_half_width * (u + v)
        p2 = base_centre + head_half_width * (u - v)
        p3 = base_centre + head_half_width * (-u - v)
        p4 = base_centre + head_half_width * (-u + v)
        apex = vec

        faces = [[apex, p1, p2],
                 [apex, p2, p3],
                 [apex, p3, p4],
                 [apex, p4, p1]]
        poly = Poly3DCollection(faces, color=colour, alpha=1.0, linewidths=0)
        ax.add_collection3d(poly)

        ax.text(*(apex * 1.25), label, color=colour,
                ha="center", va="center")

    # ------------------- draw basis vectors -----------------------
    if not (np.all(a_star == 0) or np.all(b_star == 0) or np.all(c_star == 0)):
        _draw_arrow(a_star, "red", "a*")
        _draw_arrow(b_star, "green", "b*")
        _draw_arrow(c_star, "blue", "c*")

    # ----------------------- view dir ----------------------------
    def _set_view(vec):
        x, y, z = vec
        r = np.hypot(x, y)
        elev = np.degrees(np.arctan2(z, r))
        azim = np.degrees(np.arctan2(y, x))
        ax.view_init(elev, azim)

    if view_direction:
        vd = view_direction.lower()
        if vd == "a":
            _set_view(a_star)
        elif vd == "b":
            _set_view(b_star)
        elif vd == "c":
            _set_view(c_star)

    # Cosmetic
    ax.set_box_aspect([1, 1, 1])
    ax.grid(False)
    ax.set_axis_off()
    fig.tight_layout()
    return fig, ax


slice_rule_dict = {
    "hk0": ("l", 0),
    "h0l": ("k", 0),
    "0kl": ("h", 0),
    "hk1": ("l", 1),
    "h1l": ("k", 1),
    "1kl": ("h", 1),
    "hhl": ("h", "k"),
    "h-hl": ("h", "-k"),
    "hll": ("k", "l"),
    "hl-l": ("k", "-l"),
    "hkh": ("h", "l"),
    "hk-h": ("h", "-l"),
    "h-2hl": ("k", "-2h"),
    "-2kkl": ("h", "-2k")
}

slice_rule_axis = {
    "hk0": {"h": (1, 0, 0), "k": (0, 1, 0)},
    "h0l": {"h": (1, 0, 0), "l": (0, 0, 1)},
    "0kl": {"k": (0, 1, 0), "l": (0, 0, 1)},
    "hk1": {"h": (1, 0, 0), "k": (0, 1, 0)},
    "h1l": {"h": (1, 0, 0), "l": (0, 0, 1)},
    "1kl": {"k": (0, 1, 0), "l": (0, 0, 1)},
    "hhl": {"h": (1, 1, 0), "l": (0, 0, 1)},
    "h-hl": {"h": (1, -1, 0), "l": (0, 0, 1)},
    "hll": {"h": (1, 0, 0), "l": (0, 1, 1)},
    "hl-l": {"h": (1, 0, 0), "l": (0, -1, 1)},
    "hkh": {"h": (1, 0, 1), "k": (0, 1, 0)},
    "hk-h": {"h": (1, 0, -1), "k": (0, 1, 0)},
    "h-2hl": {"h": (1, -2, 0), "l": (0, 0, 1)},
    "-2kkl": {"k": (-2, 1, 0), "l": (0, 0, 1)}
}

laue_groups = {
    range(1, 3): [],
    range(3, 16): ["hk0", "h0l", "0kl"],
    range(16, 75): ["hk0", "h0l", "0kl", "hk1", "h1l", "1kl"],
    range(75, 143): ["hk0", "h0l", "0kl", "hhl", "h-hl"],
    range(143, 195): ["hk0", "hhl", "h-2hl", "-2kkl", "h-hl", "h0l", "0kl"],
    range(195, 231): ["hk0", "h0l", "0kl", "hhl", "h-hl", "hl-l", "hll", "hk-h", "hkh", "hk1", "h1l", "1kl"],
}

AXIS_MAP = {'h': 7, 'k': 8, 'l': 9}
AXIS_MAP_INT = {'h': 0, 'k': 1, 'l': 2}

# Fixed patterns (no relative relationships)
FIXED_PATTERNS = {
    "hk0": ("l", 0),
    "h0l": ("k", 0),
    "0kl": ("h", 0),
    "hk1": ("l", 1),
    "h1l": ("k", 1),
    "1kl": ("h", 1),
}


def _apply_avg(refls, mask, axis1, axis2):
    i1, i2 = AXIS_MAP[axis1], AXIS_MAP[axis2]
    avg = (refls[:, i1] + refls[:, i2]) / 2
    refls[mask, i1] = np.round(avg[mask], 2)
    refls[mask, i2] = np.round(avg[mask], 2)


def _apply_relation(refls, mask, axis_out, axis_in, func):
    i_out, i_in = AXIS_MAP[axis_out], AXIS_MAP[axis_in]
    refls[mask, i_out] = np.round(func(refls[mask, i_in]), 2)


def filter_refls(refls, pattern, err=0.05):
    if pattern in FIXED_PATTERNS:
        axis, val = FIXED_PATTERNS[pattern]
        idx = AXIS_MAP[axis]
        mask = np.abs(refls[:, idx] - val) < err
        refls[mask, idx] = val
        return refls[mask]

    if pattern not in slice_rule_dict:
        return refls

    condition_axis, condition_value = slice_rule_dict[pattern]
    idx_axis = AXIS_MAP.get(condition_axis)
    idx_axis_int = AXIS_MAP_INT.get(condition_axis)
    if idx_axis is None:
        return refls

    match = re.match(r'^([+-]?[\d.]*)([hkl])$', str(condition_value))
    if not match:
        return refls

    coeff_str, rel_axis = match.groups()
    rel_idx = AXIS_MAP.get(rel_axis)
    rel_idx_int = AXIS_MAP_INT.get(rel_axis)
    if rel_idx is None:
        return refls

    # Determine coefficient
    if coeff_str in ['', '+']:
        coeff = 1.0
    elif coeff_str == '-':
        coeff = -1.0
    else:
        coeff = float(coeff_str)

    mask1 = np.abs(refls[:, idx_axis] - coeff * refls[:, rel_idx]) < err
    mask2 = np.abs(refls[:, idx_axis_int] - coeff * refls[:, rel_idx_int]) < err
    hkl_condition = np.any(refls[:, :3] != 0, axis=1)

    combined_mask = mask1 | (mask2 & hkl_condition)

    if not np.any(combined_mask):
        return refls[combined_mask]

    TRANSFORMATIONS = {
        "hhl": lambda r, m: _apply_avg(r, m, 'h', 'k'),
        "h-hl": lambda r, m: _apply_relation(r, m, 'h', 'k', lambda x: -x),
        "hll": lambda r, m: _apply_avg(r, m, 'k', 'l'),
        "hl-l": lambda r, m: _apply_relation(r, m, 'k', 'l', lambda x: -x),
        "hkh": lambda r, m: _apply_avg(r, m, 'h', 'l'),
        "hk-h": lambda r, m: _apply_relation(r, m, 'h', 'l', lambda x: -x),
        "h-2hl": lambda r, m: _apply_relation(r, m, 'k', 'h', lambda x: -2 * x),
        "-2kkl": lambda r, m: _apply_relation(r, m, 'h', 'k', lambda x: -2 * x),
    }

    if pattern in TRANSFORMATIONS:
        TRANSFORMATIONS[pattern](refls, combined_mask)

    return refls[combined_mask]


def flat_reflections(refls, pattern):
    """
    Projects reflections into a plane defined by `pattern`.
    """
    axis = slice_rule_axis[pattern]
    vec_a, vec_b = axis.values()
    hkl = refls[:, 7:10]
    I = refls[:, 3]

    # Project onto vec_a and vec_b
    a_index = np.dot(hkl, vec_a) / np.sum(np.power(vec_a, 2))
    b_index = np.dot(hkl, vec_b) / np.sum(np.power(vec_b, 2))

    return np.column_stack((a_index, b_index, I))


def _grayscale(intensity_norm: float, bkg_black: bool) -> tuple:
    """Return an RGB tuple representing *intensity_norm* (0‒1) on a gray scale.

    The mapping is inverted on a black background so that bright points remain
    visible against the dark canvas.
    """
    v = (1.0 - intensity_norm) if not bkg_black else intensity_norm
    return v, v, v, intensity_norm


def plot_slice_reciprocal_space(
        refls,
        pattern,
        basis_sets,
        filter_weak_refls: bool = True,
        radius: float = 1.25,
        show_grid: bool = True,
        spot_size: float = 5.5,
        linewidth: float = 0.3,
        intensity_percentile: float = 30,
        bkg_black: bool = False,
        show_label: bool = True,
        show_axes: bool = True,
        show_colour: bool = True,
        save_path: str | None = None,
        ax: plt.Axes | None = None,
):
    """Plot a slice of reciprocal space defined by *pattern*.

    When ``show_colour`` is **True** the rendering is changed as follows:

    • reflections with intensities **≥ intensity_percentile** behave exactly as
      before – their marker size scales with :math:`\sqrt{I}` and the colour is
      uniform (white or black, depending on the background);

    • reflections with intensities **< intensity_percentile** are *not
      discarded*. Instead they are plotted using

        – a **constant** marker size (``spot_size · 0.6``) and
        – a **gray-scale colour** proportional to their intensity (mapping is
          inverted on a dark background to ensure visibility).
    """

    # ------------------------------------------------------------------
    # 1. Prepare basis and projection
    # ------------------------------------------------------------------
    a_star, b_star, c_star = basis_sets
    basis_matrix = np.column_stack((a_star, b_star, c_star))

    plot_mode = ax is None
    if plot_mode:
        fig, ax = plt.subplots(figsize=(8, 8))
    else:
        fig = ax.figure
        ax.clear()

    # NOTE: *slice_rule_axis* as well as *filter_refls* and *flat_reflections*
    # must be defined in the calling scope – they are part of the original
    # code base and are left untouched here.
    vec_a, vec_b = slice_rule_axis[pattern].values()
    vec_a, vec_b = map(lambda v: np.asarray(v, float), (vec_a, vec_b))

    vec_a_3d = basis_matrix @ vec_a
    vec_b_3d = basis_matrix @ vec_b

    # --- convert to 2-D -------------------------------------------------
    vec_a_norm = np.linalg.norm(vec_a_3d)
    vec_a_2d = np.array([vec_a_norm, 0.0])

    projection_length = np.dot(vec_b_3d, vec_a_3d) / vec_a_norm
    vec_b_norm = np.linalg.norm(vec_b_3d)
    perp_length = np.sqrt(vec_b_norm ** 2 - projection_length ** 2)
    vec_b_2d = np.array([projection_length, perp_length])

    # --- determine grid range -----------------------------------------
    max_steps_a = int(np.ceil(radius / np.linalg.norm(vec_a_2d)))
    max_steps_b = int(np.ceil(radius / np.linalg.norm(vec_b_2d)))
    grid_range = np.arange(-int(max(max_steps_a, max_steps_b) * 1.45),
                           int(max(max_steps_a, max_steps_b) * 1.45) + 1)

    # ------------------------------------------------------------------
    # 2. Set up appearance parameters
    # ------------------------------------------------------------------
    if bkg_black:
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        grid_color = 'white'
        scatter_color = 'white'
        text_color = 'white'
        light_alpha = 0.8
        colour_dict = {"h": ('h', '#fd6161'), "k": ('k', '#8ed973'), "l": ('l', '#4e95d9')}
    else:
        ax.set_facecolor('white')
        fig.patch.set_facecolor('white')
        grid_color = 'black'
        scatter_color = 'black'
        text_color = 'black'
        light_alpha = 0.5
        colour_dict = {"h": ('h', '#c00000'), "k": ('k', '#196b24'), "l": ('l', '#215f9a')}

    clip_circle = Circle((0, 0), radius, transform=ax.transData)

    # ------------------------------------------------------------------
    # 3. Draw grid (optional)
    # ------------------------------------------------------------------
    if show_grid:
        line_length = max(max_steps_a, max_steps_b) * 1.2

        # lines parallel to *a*
        grid_shift_a = grid_range[:, None] * vec_b_2d
        grid_start_a = grid_shift_a - vec_a_2d * line_length
        grid_end_a = grid_shift_a + vec_a_2d * line_length
        grid_segments_a = np.hstack([grid_start_a, grid_end_a]).reshape(-1, 2, 2)

        # lines parallel to *b*
        grid_shift_b = grid_range[:, None] * vec_a_2d
        grid_start_b = grid_shift_b - vec_b_2d * line_length
        grid_end_b = grid_shift_b + vec_b_2d * line_length
        grid_segments_b = np.hstack([grid_start_b, grid_end_b]).reshape(-1, 2, 2)

        major_shifts = grid_range % 5 == 0
        minor_shifts = ~major_shifts

        major_segments = np.concatenate([grid_segments_a[major_shifts],
                                         grid_segments_b[major_shifts]])
        minor_segments = np.concatenate([grid_segments_a[minor_shifts],
                                         grid_segments_b[minor_shifts]])

        major_line_collection = LineCollection(major_segments, colors=grid_color,
                                               linestyles='-', linewidths=linewidth * 2,
                                               alpha=0.9)
        minor_line_collection = LineCollection(minor_segments, colors=grid_color,
                                               linestyles='--', linewidths=linewidth,
                                               alpha=light_alpha)
        major_line_collection.set_clip_path(clip_circle)
        minor_line_collection.set_clip_path(clip_circle)
        ax.add_collection(major_line_collection)
        ax.add_collection(minor_line_collection)

    # ------------------------------------------------------------------
    # 4. Process reflections
    # ------------------------------------------------------------------
    flat_refl = flat_reflections(filter_refls(refls, pattern), pattern)
    if flat_refl.size == 0:
        ax.text(0.5, 0.5, "No reflections", color=text_color, fontsize=16,
                ha='center', va='center', transform=ax.transAxes)
        ax.set_xlim(-radius - 0.01, radius + 0.01)
        ax.set_ylim(-radius - 0.01, radius + 0.01)
        ax.set_aspect('equal')
        ax.axis('off')
        # plt.title(f"{pattern} Slice Within Radius {1 / radius:.2f} Å", pad=30,
        #           color=grid_color)
        if save_path:
            plt.savefig(os.path.join(save_path, f"{pattern}.png"), dpi=300,
                        bbox_inches='tight')
        elif plot_mode:
            plt.show()
        return

    intensities = flat_refl[:, 2]
    intensity_threshold = np.percentile(intensities, intensity_percentile)

    # transformed coordinates for **all** reflections -------------------
    transformed_refl = (flat_refl[:, 0, None] * vec_a_2d +
                        flat_refl[:, 1, None] * vec_b_2d)
    final_refl = np.hstack((transformed_refl, intensities[:, None]))
    norm_int = (final_refl[:, 2] / final_refl[:, 2].max()).astype(float) * 100.0

    above_mask = intensities >= intensity_threshold
    below_mask = ~above_mask

    # ------------------------------------------------------------------
    # 5. Draw axes (optional)
    # ------------------------------------------------------------------
    if show_axes:
        vec_a_scaled = vec_a_2d / np.linalg.norm(vec_a_2d) * radius
        vec_b_scaled = vec_b_2d / np.linalg.norm(vec_b_2d) * radius
        key_a, key_b = slice_rule_axis[pattern].keys()

        ax.arrow(0, 0, *vec_a_scaled, head_width=radius * 0.03,
                 head_length=radius * 0.05, fc=colour_dict[key_a][1],
                 ec=colour_dict[key_a][1], zorder=10, clip_on=False)
        ax.arrow(0, 0, *vec_b_scaled, head_width=radius * 0.03,
                 head_length=radius * 0.05, fc=colour_dict[key_b][1],
                 ec=colour_dict[key_b][1], zorder=10, clip_on=False)

        ax.text(vec_a_scaled[0] * 1.05, 0.02 * radius, colour_dict[key_a][0],
                color=colour_dict[key_a][1], fontsize=14, zorder=15,
                fontstyle='italic', clip_on=False)
        ax.text(vec_b_scaled[0] * 1.05 + 0.02 * radius,
                vec_b_scaled[1] * 1.05, colour_dict[key_b][0],
                color=colour_dict[key_b][1], fontsize=14, zorder=15,
                fontstyle='italic', clip_on=False)

    # ------------------------------------------------------------------
    # 6. Plot reflections ------------------------------------------------
    # ------------------------------------------------------------------
    if not show_colour:
        # --- legacy behaviour (discard weak reflections) ----------------
        keep = above_mask
        sizes = np.sqrt(norm_int[keep]) * spot_size
        sizes[sizes < 1.0] = 0.0
        ax.scatter(final_refl[keep, 0], final_refl[keep, 1], s=sizes,
                   c=scatter_color, clip_path=clip_circle, zorder=10)
    else:
        # --- enhanced colour mapping -----------------------------------
        # strong reflections
        sizes_strong = np.sqrt(norm_int[above_mask]) * spot_size
        sizes_strong[sizes_strong < 1.0] = 0.0
        ax.scatter(final_refl[above_mask, 0], final_refl[above_mask, 1],
                   s=sizes_strong, c=scatter_color, clip_path=clip_circle,
                   zorder=11)
        norm_int_thresh = np.min(norm_int[above_mask])
        # weak reflections – constant size, grey scale colour
        sizes_weak = np.full(below_mask.sum(), np.sqrt(norm_int_thresh) * spot_size)
        colors_weak = [_grayscale((i / norm_int_thresh), bkg_black)
                       for i in norm_int[below_mask]]
        ax.scatter(final_refl[below_mask, 0], final_refl[below_mask, 1],
                   s=sizes_weak, c=colors_weak, clip_path=clip_circle,
                   zorder=10)

    # ------------------------------------------------------------------
    # 7. Finalise
    # ------------------------------------------------------------------
    ax.set_xlim(-radius - 0.01, radius + 0.01)
    ax.set_ylim(-radius - 0.01, radius + 0.01)
    ax.set_aspect('equal')
    ax.axis('off')

    # grid labels
    if show_grid and show_label:
        for shift in grid_range:
            if shift % 5 == 0 and shift != 0:
                ax.text(shift * vec_a_2d[0], shift * vec_a_2d[1] - 0.04 * radius,
                        str(shift), color=grid_color, fontsize=8, ha='center',
                        va='center', clip_on=True)
                ax.text(shift * vec_b_2d[0] + 0.03 * radius,
                        shift * vec_b_2d[1] - 0.03 * radius, str(shift),
                        color=grid_color, fontsize=8, ha='center', va='center',
                        clip_on=True)

    # plt.title(f"{pattern} Slice Within Radius {1 / radius:.2f} Å", pad=30,
    #           color=grid_color)

    if save_path:
        plt.savefig(os.path.join(save_path, f"{pattern}.png"), dpi=300,
                    bbox_inches='tight')
    elif plot_mode:
        plt.show()


def save_single_slice(args):
    """
    Plots and saves a single reciprocal space slice.

    Parameters:
    - refls (np.ndarray): Reflection data.
    - pattern (str): The pattern to plot.
    - basis_sets (tuple): Tuple of reciprocal lattice vectors (a_star, b_star, c_star).
    - radius (float): Radius for plotting.
    - intensity_percentile (float): Percentile for intensity thresholding.
    - save_path (str): Directory path to save the plot.
    """
    refls, pattern, basis_sets, radius, intensity_percentile, save_path = args

    try:
        plot_slice_reciprocal_space(
            refls=refls,
            pattern=pattern,
            basis_sets=basis_sets,
            show_grid=True,
            radius=radius,
            intensity_percentile=intensity_percentile,
            save_path=save_path
        )
    except Exception as e:
        print(f"Error plotting {pattern} slice: {e}")


def generate_slice_on_path(xds_path: str, resolution: float = 0.8, max_workers: int = None) -> None:
    """
    Generates reciprocal space slices for a given path using parallel processing.

    Parameters:
    - xds_path (str): Path to the directory containing XDS output files.
    - resolution (float, optional): Determines the radius for plotting. Default is 0.8.
    - max_workers (int, optional): The maximum number of worker processes to use.
                                   Defaults to the number of processors on the machine.
    """
    # Read cell information and reflection data
    cell_info, reflection = read_hkl(xds_path)

    # Retrieve space group number
    sg_no = cell_info.get("sg_no")
    if sg_no is None:
        raise ValueError("Space group number 'sg_no' not found in cell_info.")

    # Extract unit cell axes and compute reciprocal lattice vectors
    try:
        a = np.array(cell_info["a_axis"])
        b = np.array(cell_info["b_axis"])
        c = np.array(cell_info["c_axis"])
        V = np.dot(a, np.cross(b, c))  # Unit cell volume
        a_star = np.cross(b, c) / V
        b_star = np.cross(c, a) / V
        c_star = np.cross(a, b) / V
    except KeyError as e:
        raise KeyError(f"Missing required axis information in cell_info: {e}")
    except Exception as e:
        raise RuntimeError(f"Error computing reciprocal lattice vectors: {e}")

    # Transform reflection points to reciprocal space
    refls = transform_points(reflection, cell_info, a_star, b_star, c_star)

    # Precompute the list of patterns relevant to the given space group number
    patterns = []
    for group_range, group_patterns in laue_groups.items():
        if sg_no in group_range:
            patterns.extend(group_patterns)

    # If no patterns are found, exit early
    if not patterns:
        print(f"No patterns found for space group number {sg_no}.")
        return

    # Prepare arguments for each plot
    plot_args = [
        (
            refls,
            pattern,
            (a_star, b_star, c_star),
            1 / resolution,
            50,
            xds_path
        )
        for pattern in patterns
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(save_single_slice, arg) for arg in plot_args]


if __name__ == "__main__":
    pass
