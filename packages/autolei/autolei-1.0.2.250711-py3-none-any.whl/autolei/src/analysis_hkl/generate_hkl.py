import numpy as np


def generate_complete_reflection_list(uc: list, d_min: float = 0.79, MM: bool = False) -> list:
    """Generates a list of complete reflections up to a specified d-spacing.

    Args:
        uc (list): Unit cell parameters [a, b, c, alpha, beta, gamma].
        d_min (float, optional): Minimum d-spacing. Defaults to 0.79.
        MM (bool, optional): Macromolecular mode. Defaults to False.

    Returns:
        list: List of reflection indices (h, k, l).
    """
    a, b, c, alpha, beta, gamma = uc

    # Convert angles to radians
    alpha_r = np.radians(alpha)
    beta_r = np.radians(beta)
    gamma_r = np.radians(gamma)

    # Construct direct metric tensor G
    G = np.array([
        [a ** 2, a * b * np.cos(gamma_r), a * c * np.cos(beta_r)],
        [a * b * np.cos(gamma_r), b ** 2, b * c * np.cos(alpha_r)],
        [a * c * np.cos(beta_r), b * c * np.cos(alpha_r), c ** 2]
    ])

    # Invert G to get reciprocal metric tensor G*
    G_inv = np.linalg.inv(G)

    # Estimate initial bounds
    max_h = int(np.ceil(a / d_min))
    max_k = int(np.ceil(b / d_min))
    max_l = int(np.ceil(c / d_min))

    max_int = int(np.sqrt(3) * max(max_h, max_k, max_l)) + 1

    # Heuristic limit check
    if max_h + max_k + max_l > 250 and not MM:
        return []

    # Generate all possible h, k, l indices
    hs = np.arange(-max_h, max_h + 1)
    ks = np.arange(-max_k, max_k + 1)
    ls = np.arange(0, max_l + 1)

    # Create a meshgrid and then flatten
    H, K, L = np.meshgrid(hs, ks, ls, indexing='ij')
    H_flat = H.ravel()
    K_flat = K.ravel()
    L_flat = L.ravel()

    # Filter out (h, k, l) = (0, 0, 0)
    non_zero_mask = ~((H_flat == 0) & (K_flat == 0) & (L_flat == 0))

    # Filter based on the (h + k + l) < max_int condition
    sum_mask = (H_flat + K_flat + L_flat) < max_int

    # Combine masks
    combined_mask = non_zero_mask & sum_mask

    H_sel = H_flat[combined_mask]
    K_sel = K_flat[combined_mask]
    L_sel = L_flat[combined_mask]

    # Form the hkl matrix: shape (N, 3)
    hkl_matrix = np.stack((H_sel, K_sel, L_sel), axis=-1)
    inv_d2 = np.sum((hkl_matrix @ G_inv) * hkl_matrix, axis=1)

    # inv_d2 must be > 0 to have a valid d
    valid_mask = inv_d2 > 0

    hkl_matrix = hkl_matrix[valid_mask]
    inv_d2 = inv_d2[valid_mask]

    # Compute d and filter by d >= d_min
    d = 1.0 / np.sqrt(inv_d2)
    resolution_mask = d >= d_min

    hkl_matrix = hkl_matrix[resolution_mask]

    # Convert back to list of tuples
    refls = [tuple(row) for row in hkl_matrix]

    return refls
