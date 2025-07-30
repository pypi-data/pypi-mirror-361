import numpy as np
from scipy.spatial import procrustes

from .cell_reduction import niggli_reduce_cell
from .util import cell_to_matrix, real_to_reciprocal, jordan_form, unit_cell_metric_tensor


def unit_cell_distance_procrustes(cell_a: tuple, cell_b: tuple) -> float:
    """Calculates the distance between two unit cells using Procrustes analysis.

    Args:
        cell_a (tuple): Unit cell parameters for the first cell.
        cell_b (tuple): Unit cell parameters for the second cell.

    Returns:
        float: Distance between the two unit cells.
    """
    A_real = cell_to_matrix(*niggli_reduce_cell(*cell_a))
    B_real = cell_to_matrix(*niggli_reduce_cell(*cell_b))

    A_recip, vol_A = real_to_reciprocal(A_real)
    B_recip, vol_B = real_to_reciprocal(B_real)

    A_recip[np.abs(A_recip) < 1e-10] = 0
    B_recip[np.abs(B_recip) < 1e-10] = 0

    try:
        A_jordan = jordan_form(A_recip)
        B_jordan = jordan_form(B_recip)
        _, _, disparity_jordan = procrustes(A_jordan, B_jordan)
    except Exception:
        disparity_jordan = float('inf')

    _, _, disparity_original = procrustes(A_recip, B_recip)
    disparity = min(disparity_jordan, disparity_original)
    rmsd_affine = disparity ** 0.25
    volume_ratio = max(vol_A / vol_B, vol_B / vol_A)

    return round(rmsd_affine * min(np.exp(volume_ratio - 1), 100), 3)




def unit_cell_distance_niggli(cell_a: tuple, cell_b: tuple) -> float:
    """Calculates the distance between two Niggli-reduced unit cells.

    Args:
        cell_a (tuple): Unit cell parameters for the first cell.
        cell_b (tuple): Unit cell parameters for the second cell.

    Returns:
        float: Distance between the two reduced unit cells.
    """
    a_r1, b_r1, c_r1, alpha_r1, beta_r1, gamma_r1 = niggli_reduce_cell(*cell_a)
    cell_a_reduced = (a_r1, b_r1, c_r1, alpha_r1, beta_r1, gamma_r1)

    a_r2, b_r2, c_r2, alpha_r2, beta_r2, gamma_r2 = niggli_reduce_cell(*cell_b)
    cell_b_reduced = (a_r2, b_r2, c_r2, alpha_r2, beta_r2, gamma_r2)

    # Compute metric tensors of the reduced cells
    G_a = unit_cell_metric_tensor(*cell_a_reduced)
    G_b = unit_cell_metric_tensor(*cell_b_reduced)

    # Compute the difference between the metric tensors
    delta_G = G_a - G_b

    # Compute the Frobenius norm of the difference
    distance = np.linalg.norm(delta_G, ord='fro')

    return distance