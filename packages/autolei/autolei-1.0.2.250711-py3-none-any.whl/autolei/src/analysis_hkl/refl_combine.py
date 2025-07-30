from collections import defaultdict

import numpy as np
import pandas as pd
from ..xds_input import extract_keywords

from .util import unit_cell_volume, interplanar_spacing
from ..symm_shelx.laue_symm_ops import symmetry_operations
from ..symm_shelx.symm_function import get_laue_group


def mark_multiple_reflections(refls: list) -> pd.DataFrame:
    """
    Marks reflections that have multiple intensity measurements.

    Args:
        refls (list): List of reflection data, where each reflection is a tuple
                      containing (h, k, l, d, intensities, sigmas, mean_intensity,
                      weighted_sigma, mean_sigma).
    Returns:
        pd.DataFrame: DataFrame containing reflections with multiple intensities,
                      with columns ['h', 'k', 'l', 'd', 'I'].
    """
    half1 = []
    for reflection in refls:
        h, k, l, d, intensities, sigmas, _, _, _ = reflection
        if len(intensities) >= 2:
            half1.append([h, k, l, d, 0])

    half1_df = pd.DataFrame(half1, columns=['h', 'k', 'l', 'd', 'I'])
    return half1_df


def combine_hkl(refls: list, exclude: list = None) -> list:
    """Combines reflection data of same hkl by averaging intensities and sigmas.

    Args:
        refls (list): List of reflection data.
        exclude (list, optional): List of data sources to exclude.
            Defaults to None.

    Returns:
        list: Averaged reflection data for unique (h, k, l) combinations.
    """
    if exclude is None:
        exclude = []

    # Convert the input list to a numpy array for efficient processing
    data = np.array(refls)

    # Extract columns
    hkl = data[:, :3]
    I = data[:, 3]
    sigma = data[:, 4]
    data_source = data[:, 5]

    # Filter out reflections from the exclude list
    mask = np.isin(data_source, exclude, invert=True)
    hkl = hkl[mask]
    # After masking
    I = I[mask]
    sigma = sigma[mask]

    # Flatten and ensure numeric data types
    I = I.flatten().astype(float)
    sigma = sigma.flatten().astype(float)

    # Get unique (h, k, l) combinations and their indices
    unique_hkl, indices, inverse_indices, counts = np.unique(
        hkl, axis=0, return_index=True, return_inverse=True, return_counts=True)

    # Ensure inverse_indices is integer
    inverse_indices = inverse_indices.flatten().astype(int)

    # Sum intensities and sigma inverse squared
    sum_I = np.bincount(inverse_indices, weights=I)
    sum_sigma_inv_sq = np.bincount(inverse_indices, weights=1 / sigma ** 2)

    # Calculate average intensity
    avg_I = sum_I / counts
    # Calculate average sigma
    avg_sigma = 1 / np.sqrt(sum_sigma_inv_sq)

    # Combine results into a single array
    result = np.column_stack((unique_hkl, avg_I, avg_sigma)).tolist()

    return result


def generate_unique_reflections(refls: list, sg_no: int, uc: list) -> list:
    """Generates unique reflections considering symmetry operations.

    Args:
        refls (list): List of reflection data.
        sg_no (int): Space group number.
        uc (list): Unit cell parameters [a, b, c, alpha, beta, gamma].

    Returns:
        list: Unique reflections with interplanar spacings and intensities.
    """
    laue_group = get_laue_group(sg_no)
    symmetry_ops = symmetry_operations.get(laue_group, [])
    has_intensity_sigma = (len(refls[0]) > 3)
    use_intensity_sigma = has_intensity_sigma

    a, b, c, alpha, beta, gamma = uc
    V = unit_cell_volume(a, b, c, alpha, beta, gamma)

    alpha_r, beta_r, gamma_r = np.deg2rad([alpha, beta, gamma])
    sin_alpha, sin_beta, sin_gamma = np.sin([alpha_r, beta_r, gamma_r])
    cos_alpha, cos_beta, cos_gamma = np.cos([alpha_r, beta_r, gamma_r])

    a_star = b * c * sin_alpha / V
    b_star = a * c * sin_beta / V
    c_star = a * b * sin_gamma / V

    cos_alpha_star = (cos_beta * cos_gamma - cos_alpha) / (sin_beta * sin_gamma)
    cos_beta_star = (cos_alpha * cos_gamma - cos_beta) / (sin_alpha * sin_gamma)
    cos_gamma_star = (cos_alpha * cos_beta - cos_gamma) / (sin_alpha * sin_beta)

    unique_reflections_dict = defaultdict(lambda: ([], []))

    # Process all reflections without chunking
    if use_intensity_sigma:
        for reflection in refls:
            h, k, l, I, sig = reflection
            if symmetry_ops:
                # Apply symmetry operations and take minimum key
                key = min(op(h, k, l) for op in symmetry_ops)
            else:
                key = (h, k, l)
            unique_reflections_dict[key][0].append(I)
            unique_reflections_dict[key][1].append(sig)
    else:
        for reflection in refls:
            h, k, l = reflection[:3]
            if symmetry_ops:
                # Apply symmetry operations and take minimum key
                key = min(op(h, k, l) for op in symmetry_ops)
            else:
                key = (h, k, l)
            if key not in unique_reflections_dict:
                unique_reflections_dict[key] = ([], [])

    unique_reflections_keys = list(unique_reflections_dict.keys())

    # Compute final results
    results = []
    for r in unique_reflections_keys:
        h, k, l = r
        d = interplanar_spacing(h, k, l, a_star, b_star, c_star,
                                cos_alpha_star, cos_beta_star, cos_gamma_star)
        if has_intensity_sigma:
            intensities = np.array(unique_reflections_dict[r][0])
            sigmas = np.array(unique_reflections_dict[r][1])
            mean_sigma = np.sqrt(np.mean(np.square(sigmas)) / len(sigmas)) if sigmas.any() else 0.0
            if len(intensities) > 1:
                weights = 1 / np.square(sigmas)
                weighted_mean_intensity = np.sum(weights * intensities) / np.sum(weights)
                weighted_variance = np.sum(weights * (intensities - weighted_mean_intensity) ** 2) / np.sum(weights)
                weighted_sigma = np.sqrt(weighted_variance / (len(intensities) - 1))
            else:
                weighted_mean_intensity = intensities[0]
                weighted_sigma = sigmas[0]
            results.append((h, k, l, d, list(intensities),
                            list(sigmas), weighted_mean_intensity, weighted_sigma, mean_sigma))
        else:
            results.append((h, k, l, d))

    return sorted(results)


def load_refls_bravais(xds_hkl: str, reso_low: float, reso_high: float) -> tuple:
    """Loads reflections from XDS HKL file within specified resolution range.

    Args:
        xds_hkl (str): Path to the XDS ASCII HKL file.
        reso_low (float): Low resolution limit.
        reso_high (float): High resolution limit.

    Returns:
        tuple: Filtered reflection data (np.ndarray) and header information (dict).
    """
    with open(xds_hkl, 'r') as f:
        lines = f.readlines()

    header_lines = [line[1:].strip() for line in lines if line.startswith('!')]
    header_dict = extract_keywords(header_lines)

    try:
        data_start = lines.index('!END_OF_HEADER\n') + 1
    except ValueError:
        data_start = next(i for i, line in enumerate(lines) if line.strip() == '!END_OF_HEADER') + 1

    # Efficiently parse the data using NumPy
    data = []
    for line in lines[data_start:]:
        parts = line.split()
        if len(parts) < 5:
            continue
        sigma = float(parts[4])
        if sigma <= 0:
            continue
        h, k, l = map(int, parts[:3])
        intensity, sig_intensity, x, y = map(float, parts[3:7])
        data.append([h, k, l, intensity, sig_intensity, x, y])

    data_array = np.array(data)
    scale_factor = (float(header_dict["QX"][0]) / float(header_dict["DETECTOR_DISTANCE"][0]) /
                    float(header_dict["X-RAY_WAVELENGTH"][0]))
    min_distance = 1 / reso_low / scale_factor
    max_distance = 1 / reso_high / scale_factor
    X0, Y0 = float(header_dict["ORGX"][0]), float(header_dict["ORGY"][0])

    # Calculate distances using vectorized operations
    distances = np.sqrt((data_array[:, -2] - X0) ** 2 + (data_array[:, -1] - Y0) ** 2)

    # Apply all filters at once
    mask = (
            (distances >= min_distance) &
            (distances <= max_distance) &
            (data_array[:, 3] / data_array[:, 4] > 0)
    )
    filtered_data = data_array[mask]

    return filtered_data, (
        header_dict["SPACE_GROUP_NUMBER"],
        header_dict["UNIT_CELL_CONSTANTS"]
    )


def generate_unique_no_d(reflections: np.ndarray, symmetry_ops: list) -> list:
    """Generates unique reflections without considering d-spacing.

    Args:
        reflections (np.ndarray): List of reflection data.
        symmetry_ops (list): List of symmetry operations.

    Returns:
        list: Unique reflections.
    """
    unique_reflections = {}
    has_intensity_sigma = reflections.shape[1] > 4

    for reflection in reflections:
        h, k, l = reflection[:3]
        if has_intensity_sigma:
            intensity, sigma = reflection[3], reflection[4]
        else:
            intensity, sigma = None, None

        # Apply symmetry operations and find the minimum equivalent reflection
        sym_equivs = [tuple(op(h, k, l)) for op in symmetry_ops]
        min_sym_op = min(sym_equivs)

        if min_sym_op in unique_reflections:
            if has_intensity_sigma:
                unique_reflections[min_sym_op][0].append(intensity)
                unique_reflections[min_sym_op][1].append(sigma)
        else:
            if has_intensity_sigma:
                unique_reflections[min_sym_op] = ([intensity], [sigma])
            else:
                unique_reflections[min_sym_op] = ([], [])

    # Compile unique reflections
    unique_list = []
    for (h, k, l), (intensities, sigmas) in unique_reflections.items():
        if has_intensity_sigma and intensities:
            intensities = np.array(intensities)
            sigmas = np.array(sigmas)
            mean_sigma = np.sqrt(np.mean(np.square(sigmas)) / len(sigmas)) if sigmas.any() else 0.0
            if len(intensities) > 1:
                weights = 1 / np.square(sigmas)
                weighted_mean_intensity = np.sum(weights * intensities) / np.sum(weights)
                weighted_variance = np.sum(weights * (intensities - weighted_mean_intensity) ** 2) / np.sum(weights)
                weighted_sigma = np.sqrt(weighted_variance / (len(intensities) - 1))
            else:
                weighted_mean_intensity = intensities[0]
                weighted_sigma = sigmas[0]
            unique_list.append(
                (h, k, l, 0, list(intensities), list(sigmas), weighted_mean_intensity, weighted_sigma, mean_sigma))
        else:
            unique_list.append((h, k, l))
    return unique_list
