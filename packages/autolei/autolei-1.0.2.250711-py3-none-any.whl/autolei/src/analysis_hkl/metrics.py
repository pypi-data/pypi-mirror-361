import numpy as np
import pandas as pd
from scipy.stats import t

slice_list = [
                 80.0, 20.0, 15.0, 10.2, 7.70, 6.67, 5.30, 4.62, 4.20, 3.90, 3.70, 3.46, 3.30,
                 3.14, 3.00, 2.90, 2.82, 2.76, 2.70, 2.63, 2.56, 2.48, 2.40, 2.34, 2.27,
                 2.20, 2.14, 2.07, 2.00, 1.90, 1.80, 1.70, 1.60, 1.50, 1.42, 1.35, 1.28,
                 1.23, 1.18, 1.14, 1.10, 1.07, 1.04, 1.02, 1.00, 0.98, 0.96, 0.93, 0.90,
                 0.87, 0.84] + np.round(np.arange(0.82, 0.15, -0.01), 2).tolist()


def slice_reflections(refls: list, d_max: float, d_min: float) -> list:
    """Slices reflections based on a d-spacing range.

    Args:
        refls (list): List of reflection data.
        d_max (float): Maximum d-spacing.
        d_min (float): Minimum d-spacing.

    Returns:
        list: Reflections within the specified d-spacing range.
    """
    return [
        refl for refl in refls
        if (d_min < refl[3] <= d_max)
    ]


def generate_slice_d(df: pd.DataFrame, num_slices: int = 15) -> list:
    """Generates slicing points for reflections based on the number of slices.

    Args:
        df (pd.DataFrame): DataFrame containing reflection data.
        num_slices (int, optional): Number of slices. Defaults to 15.

    Returns:
        list: Slicing points for the reflection data.
    """

    sorted_df = df.sort_values(by='d')
    slice_size = len(df) // num_slices + 1
    if slice_size < 40:
        slice_size = len(df) // 12 + 1
    if slice_size < 40:
        slice_size = len(df) // 9 + 1
    if slice_size < 40:
        slice_size = len(df) // 6 + 1
    slices = []

    for i in range(num_slices):
        start = i * slice_size
        end = start + slice_size if i < num_slices - 1 else len(df)
        slice_df = sorted_df.iloc[start:end]
        slices.append(slice_df)

    slicing_points = [slices[i]['d'].min() for i in range(num_slices)]

    adjusted_slicing_points = sorted({min(slice_list, key=lambda x: x >= point) for point in slicing_points},
                                     reverse=True)
    if len(adjusted_slicing_points) <= 3:
        return []
    if 80.0 not in adjusted_slicing_points:
        adjusted_slicing_points = ([80.0] + adjusted_slicing_points[:-1] +
                                   ([round(min(slicing_points), 2)]
                                    if adjusted_slicing_points[-2] != round(min(slicing_points), 2) else []))
    else:
        adjusted_slicing_points = (adjusted_slicing_points[:-1] +
                                   ([round(min(slicing_points), 2)]
                                    if adjusted_slicing_points[-2] != round(min(slicing_points), 2) else []))
    if adjusted_slicing_points[1] < 0.90:
        adjusted_slicing_points = [80.0, 1.0] + adjusted_slicing_points[1:]
    elif adjusted_slicing_points[1] < 0.84:
        adjusted_slicing_points = [80.0, 1.0, 0.90] + adjusted_slicing_points[1:]
    elif adjusted_slicing_points[1] < 0.80:
        adjusted_slicing_points = [80.0, 1.0, 0.90, 0.94] + adjusted_slicing_points[1:]

    return adjusted_slicing_points


def generate_slice_report(ideal_refl: list, refls: list, half1: pd.DataFrame) -> list:
    """Generates a report of reflection data slices.

    Args:
        ideal_refl (list): List of ideal reflections.
        refls (list): List of observed reflections.
        half1 (pd.DataFrame): Data for the first half of reflections.

    Returns:
        list: Slice report containing statistics for each resolution slice.
    """
    result_list = []
    resolution_slices = generate_slice_d(half1)

    for i in range(len(resolution_slices) - 1):
        low_res, high_res = resolution_slices[i], resolution_slices[i + 1]
        temp_refls = slice_reflections(refls, low_res, high_res)
        temp_ideals = slice_reflections(ideal_refl, low_res, high_res)
        if temp_refls > temp_ideals:
            temp_refls = temp_refls

        I_values = [row[4] for row in temp_refls]
        total_count = sum(len(I) if isinstance(I, list) else 1 for I in I_values)

        rint, rmeas, rexp = calculate_r_factors(temp_refls)

        cc12, cc_crit = calculate_cc_half(temp_refls)

        # Create a dictionary for the current slice
        result = {
            "low_res": low_res,
            "high_res": high_res,
            "N_obs": total_count,
            "N_uni": len(temp_refls),
            "ideal_N": len(temp_ideals),
            "completeness": round(100 * len(temp_refls) / len(temp_ideals), 2),
            "multiplicity": round(total_count / len(temp_refls), 2),
            "Isa_meas": calculate_mean_i_over_sigma(temp_refls),
            "R_int": rint,
            "R_meas": rmeas,
            "R_exp": rexp,
            "CC1/2": cc12,
            "CC_crit": cc_crit
        }
        result_list.append(result)
    return result_list


def accumulate_statistics(refls: list, reso: float) -> tuple:
    """Accumulates statistical data for reflections within a resolution limit.

    Args:
        refls (list): List of reflections.
        reso (float): Resolution limit.

    Returns:
        tuple: Statistical metrics (number of reflections, mean intensity,
            R factors, CC1/2).
    """
    temp_refls = slice_reflections(refls, 999, reso)
    return (len(temp_refls), calculate_mean_i_over_sigma(temp_refls), calculate_r_factors(temp_refls),
            calculate_cc_half(temp_refls))


def calculate_resolution_limit(unique_refls: list, half1: pd.DataFrame, p: float = 0.005) -> float:
    """Calculates the resolution limit based on CC, Rmeas and I/S.

    Args:
        unique_refls (list): List of unique reflections.
        half1 (pd.DataFrame): Data for the first half of reflections.
        p (float, optional): p-value for the correlation test. Defaults to 0.01.

    Returns:
        float: Resolution limit.
    """
    _list = generate_slice_d(half1)
    if len(_list) <= 3:
        return 999
    reso = 999
    for i in range(1, len(_list) - 1):
        cc12, cc_crit = calculate_cc_half(slice_reflections(unique_refls, _list[i], _list[i + 1]), p)
        if cc12 >= cc_crit:
            reso = _list[i + 1]
        elif cc12 < cc_crit:
            break
        r_int, _, _ = calculate_r_factors(slice_reflections(unique_refls, _list[i], _list[i + 1]))
        if abs(r_int) > 180:
            break
        elif r_int > 100 or r_int < 0:
            isa = calculate_mean_i_over_sigma(slice_reflections(unique_refls, _list[i], _list[i + 1]))
            if isa < 0.5:
                break
    return reso


def calculate_cc_half(uniq_refls: list, p_value: float = 0.005) -> tuple:
    """
    Calculate CC1/2 based on the provided unique reflections.

    Parameters:
    - uniq_refls: List of tuples containing reflection data.
    - p_value: Statistical significance threshold (default is 0.005).

    Returns:
    - A tuple containing CC1/2, sigma_I, and sigma_e^2.
    """

    # Step 1: Filter reflections with len(element5) > 1
    filtered_refls = [refl for refl in uniq_refls if len(refl[4]) > 1]

    if not filtered_refls:
        raise ValueError("No reflections with more than one intensity measurement found.")

    # Extract mean intensities (element7) and sigma (element8)
    mean_intensities = [refl[6] for refl in filtered_refls]
    sigmas = [refl[7] for refl in filtered_refls]

    # Step 2: Calculate sigma_I (standard deviation of mean intensities)
    sigma_I = np.std(mean_intensities, ddof=1)  # Using sample standard deviation

    # Step 3: Calculate average sigma_e^2
    sigma_e_squared = np.mean([sigma ** 2 for sigma in sigmas])

    # Ensure denominator is not zero or negative
    denominator = sigma_I ** 2 + sigma_e_squared
    if denominator <= 0:
        raise ValueError("Denominator in CC1/2 calculation is non-positive.")

    # Step 4: Calculate CC1/2
    cc_half = (sigma_I ** 2 - sigma_e_squared) / denominator

    # Degrees of freedom
    df = len(filtered_refls) - 2
    # Get the critical t-value
    t_critical = t.ppf(1 - p_value / 2, df)
    # Convert t-value to critical correlation coefficient
    cc_critical = np.sqrt(t_critical ** 2 / (t_critical ** 2 + df))

    return np.round(100 * cc_half, 2), np.round(100 * cc_critical, 2)


def calculate_r_factors(refls: list) -> tuple:
    """Calculates R factors for reflection data.

    Args:
        refls (list): List of reflection data.

    Returns:
        tuple: R_int, R_meas, and R_exp values.
    """

    if not refls:
        return 100, 100, 100

    # Extract relevant data
    intensities_list = [np.array(reflection[4]) for reflection in refls]
    sigmas_list = [np.array(reflection[5]) for reflection in refls]
    mean_intensities = np.array([reflection[6] for reflection in refls])

    # Flatten lists for vectorized operations
    all_intensities = np.concatenate(intensities_list)
    all_sigmas = np.concatenate(sigmas_list)

    # Compute sums
    sum_sigma = np.sum(all_sigmas)
    sum_intensity = np.sum(all_intensities)

    # Filter reflections with more than one intensity
    lengths = np.array([len(intensities) for intensities in intensities_list])
    multiple_intensity_mask = lengths > 1

    if not multiple_intensity_mask.any():
        return None, None, None

    # Extract mult_intensities and their mean intensities
    mult_intensities_list = [intensities_list[i] for i in np.where(multiple_intensity_mask)[0]]
    mult_mean_intensities = mean_intensities[multiple_intensity_mask]
    mult_lengths = lengths[multiple_intensity_mask]

    # Flatten lists for vectorized operations
    mult_all_intensities = np.concatenate(mult_intensities_list)
    mult_mean_intensities_repeated = np.concatenate([np.full_like(intensities, mean_intensity)
                                                     for intensities, mean_intensity
                                                     in zip(mult_intensities_list, mult_mean_intensities)])

    # Compute intensity differences
    int_diff = np.abs(mult_all_intensities - mult_mean_intensities_repeated)
    sum_int_diff = np.sum(int_diff)

    # Compute the final sum_meas_diff using vectorized operations
    sqrt_factors = np.sqrt(mult_lengths / (mult_lengths - 1))
    starts = np.cumsum(np.concatenate(([0], mult_lengths[:-1])))
    sum_meas_diff = np.sum(sqrt_factors * np.add.reduceat(int_diff, starts))

    sum_meas_intensity = np.sum(mult_all_intensities)

    # Check for division by zero
    if sum_intensity == 0 or sum_meas_intensity == 0:
        return None, None, None

    # Compute R factors
    r_exp = np.round(100 * sum_sigma / sum_intensity, 2)
    r_meas = np.round(100 * sum_meas_diff / sum_meas_intensity, 2)
    r_int = np.round(100 * sum_int_diff / sum_intensity, 2)

    return r_int, r_meas, r_exp


def calculate_mean_i_over_sigma(refls: list) -> float:
    """Calculates the mean intensity over sigma for reflection data.

    Args:
        refls (list): List of reflection data.

    Returns:
        float: Mean intensity over sigma.
    """
    valid_entries = [
        mean_intensity / mean_sigma
        for _, _, _, _, intensities, sigmas, mean_intensity, _, mean_sigma in refls
        if len(sigmas) > 0 and mean_sigma > 0
    ]

    if not valid_entries:
        return 0.0

    return float(np.round(np.mean(valid_entries), 4))
