import numpy as np
from numpy.linalg import solve, eig


def unit_cell_metric_tensor(a: float, b: float, c: float, alpha: float, beta: float, gamma: float) -> np.ndarray:
    """Calculates the metric tensor for a unit cell.

    Args:
        a (float): Unit cell parameter a.
        b (float): Unit cell parameter b.
        c (float): Unit cell parameter c.
        alpha (float): Unit cell angle alpha in degrees.
        beta (float): Unit cell angle beta in degrees.
        gamma (float): Unit cell angle gamma in degrees.

    Returns:
        np.ndarray: Metric tensor (3x3 matrix).
    """
    # Convert angles from degrees to radians
    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)
    gamma_rad = np.radians(gamma)

    # Compute cosines of the angles
    cos_alpha = np.cos(alpha_rad)
    cos_beta = np.cos(beta_rad)
    cos_gamma = np.cos(gamma_rad)

    # Compute metric tensor components
    G = np.array([
        [a ** 2, a * b * cos_gamma, a * c * cos_beta],
        [a * b * cos_gamma, b ** 2, b * c * cos_alpha],
        [a * c * cos_beta, b * c * cos_alpha, c ** 2]
    ])
    return G


# Reflection Data Operations
def unit_cell_volume(a: float, b: float, c: float, alpha: float, beta: float, gamma: float) -> float:
    """Calculates the unit cell volume.

    Args:
        a (float): Unit cell parameter a.
        b (float): Unit cell parameter b.
        c (float): Unit cell parameter c.
        alpha (float): Unit cell angle alpha in degrees.
        beta (float): Unit cell angle beta in degrees.
        gamma (float): Unit cell angle gamma in degrees.

    Returns:
        float: Volume of the unit cell.
    """
    alpha, beta, gamma = np.deg2rad([alpha, beta, gamma])
    return a * b * c * np.sqrt(1 - np.cos(alpha) ** 2 - np.cos(beta) ** 2 - np.cos(gamma) ** 2 +
                               2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma))


def interplanar_spacing(h: int, k: int, l: int, a_star: float, b_star: float, c_star: float,
                        cos_alpha_star: float, cos_beta_star: float, cos_gamma_star: float) -> float:
    """Calculates the interplanar spacing for given Miller indices.

    Args:
        h (int): Miller index h.
        k (int): Miller index k.
        l (int): Miller index l.
        a_star (float): Reciprocal lattice parameter a*.
        b_star (float): Reciprocal lattice parameter b*.
        c_star (float): Reciprocal lattice parameter c*.
        cos_alpha_star (float): Cosine of reciprocal angle alpha*.
        cos_beta_star (float): Cosine of reciprocal angle beta*.
        cos_gamma_star (float): Cosine of reciprocal angle gamma*.

    Returns:
        float: Interplanar spacing (d-spacing).
    """
    d_hkl_sq = 1 / (h ** 2 * a_star ** 2 + k ** 2 * b_star ** 2 + l ** 2 * c_star ** 2 +
                    2 * h * k * a_star * b_star * cos_gamma_star +
                    2 * h * l * a_star * c_star * cos_beta_star +
                    2 * k * l * b_star * c_star * cos_alpha_star)
    return np.sqrt(d_hkl_sq)


def transform_hkl(data_array: np.ndarray, REIDX: list, IDXV_value: int) -> np.ndarray:
    """Transforms HKL data using a transformation matrix and index vector.

    Args:
        data_array (np.ndarray): Array of HKL data.
        REIDX (list): Transformation matrix.
        IDXV_value (int): Lattice centre code.

    Returns:
        np.ndarray: Transformed HKL data.
    """
    transformation_matrix = np.array(REIDX).reshape(3, 4)
    hkl = data_array[:, :3].T  # Shape: (3, N)

    transformed_hkl = (transformation_matrix[:, :3] @ hkl + transformation_matrix[:, 3].reshape(3, 1)) / IDXV_value
    transformed_array = data_array.copy()
    transformed_array[:, :3] = transformed_hkl.T
    return transformed_array


def inverse_transform_hkl(transformed_array: np.ndarray, REIDX: list, IDXV_value: int) -> np.ndarray:
    """Inversely transforms HKL data to obtain the original.

    Args:
        transformed_array (np.ndarray): Transformed HKL data.
        REIDX (list): Transformation matrix.
        IDXV_value (int): Lattice centre code.

    Returns:
        np.ndarray: Original HKL data.
    """
    A = np.array(REIDX).reshape(3, 4)[:, :3]
    b = np.array(REIDX).reshape(3, 4)[:, 3]

    original_hkl = solve(A, (transformed_array[:, :3].T * IDXV_value) - b.reshape(3, 1))
    original_array = transformed_array.copy()
    original_array[:, :3] = original_hkl.T
    return original_array


def shape_cell_parameter_bravais(value_dict: dict, bravais_lattice: str) -> tuple:
    """Shapes cell parameters according to the Bravais lattice type.

    Args:
        value_dict (dict): Dictionary containing cell parameters.
        bravais_lattice (str): Bravais lattice type.

    Returns:
        tuple: Shaped cell parameters.
    """
    a, b, c, alpha, beta, gamma = value_dict["cell_parameters"]
    tolerance_angle = 3
    tolerance_length = 0.03

    def within(value, target, tol):
        return abs(value - target) <= tol

    if bravais_lattice.startswith("a"):  # Triclinic
        return a, b, c, alpha, beta, gamma
    elif bravais_lattice.startswith("h"):  # Hexagonal or Rhombohedral
        if not (within(gamma, 120, tolerance_angle) and
                within(alpha, 90, tolerance_angle) and
                within(beta, 90, tolerance_angle) and
                abs(a - b) <= tolerance_length * (a + b)):
            return ()
        avg_ab = np.mean([a, b])
        return avg_ab, avg_ab, c, 90, 90, 120
    elif bravais_lattice.startswith("m"):  # Monoclinic
        if not (within(gamma, 90, 3) and within(alpha, 90, 3)):
            return ()
        return a, b, c, 90, beta, 90
    elif bravais_lattice.startswith("o"):  # Orthorhombic
        if not all(within(angle, 90, 2) for angle in [alpha, beta, gamma]):
            return ()
        return a, b, c, 90, 90, 90
    elif bravais_lattice.startswith("t"):  # Tetragonal
        if not (within(gamma, 90, 3) and within(alpha, 90, 3) and
                within(beta, 90, 2) and abs(a - b) <= tolerance_length * (a + b)):
            return ()
        avg_ab = np.mean([a, b])
        return avg_ab, avg_ab, c, 90, 90, 90
    elif bravais_lattice.startswith("c"):  # Cubic
        if not (all(within(angle, 90, 3) for angle in [alpha, beta, gamma]) and
                abs(a - b) <= tolerance_length * (a + b) and
                abs(a - c) <= tolerance_length * (a + c)):
            return ()
        avg_abc = np.mean([a, b, c])
        return avg_abc, avg_abc, avg_abc, 90, 90, 90
    return ()


def jordan_form(A: np.ndarray) -> np.ndarray:
    """Calculates the Jordan form of a matrix.

    Args:
        A (np.ndarray): Input matrix.

    Returns:
        np.ndarray: Jordan form of the matrix.
    """
    eigenvalues, _ = eig(A)
    n = A.shape[0]
    J = np.zeros((n, n), dtype=complex)

    eigen_counts = {}
    for val in eigenvalues:
        eigen_counts[np.round(val, decimals=10)] = eigen_counts.get(np.round(val, decimals=10), 0) + 1

    idx = 0
    for eigval, count in eigen_counts.items():
        for _ in range(count):
            J[idx, idx] = eigval
            if idx < n - 1 and count > 1:
                J[idx, idx + 1] = 1
            idx += 1
    return J


def cell_to_matrix(a: float, b: float, c: float, alpha: float, beta: float, gamma: float) -> np.ndarray:
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

    return np.vstack([v_a, v_b, v_c])


def real_to_reciprocal(lattice: np.ndarray) -> tuple:
    """Converts real space lattice to reciprocal space lattice.

    Args:
        lattice (np.ndarray): Real space lattice matrix.

    Returns:
        tuple: Reciprocal space lattice matrix and volume of the real lattice.
    """
    volume = np.dot(lattice[0], np.cross(lattice[1], lattice[2]))
    reciprocal_lattice = np.array([
        np.cross(lattice[1], lattice[2]),
        np.cross(lattice[2], lattice[0]),
        np.cross(lattice[0], lattice[1])
    ]) / volume
    return reciprocal_lattice, volume
