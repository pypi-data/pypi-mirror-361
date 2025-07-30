import numpy as np


def lll_reduction(basis: np.ndarray, delta: float = 0.75) -> np.ndarray:
    """Performs LLL reduction on a lattice basis.

    Args:
        basis (np.ndarray): Lattice basis vectors (rows of the matrix).
        delta (float, optional): Reduction parameter. Defaults to 0.75.

    Returns:
        np.ndarray: LLL-reduced lattice basis.
    """
    n = basis.shape[0]
    basis = basis.copy()
    # Gram-Schmidt Orthogonalization
    B = np.zeros_like(basis)
    mu = np.zeros((n, n))
    norm_B = np.zeros(n)
    for i in range(n):
        B[i] = basis[i]
        for j in range(i):
            denom = np.dot(B[j], B[j])
            if denom == 0:
                raise ValueError(f"Zero norm encountered in B[{j}]; basis vectors may be linearly dependent.")
            mu[i, j] = np.dot(B[i], B[j]) / denom
        for j in range(i):
            B[i] -= mu[i, j] * B[j]
        norm_B[i] = np.dot(B[i], B[i])
        if norm_B[i] == 0:
            raise ValueError(f"Vector B[{i}] has zero norm; basis vectors may be linearly dependent.")

    k = 1
    while k < n:
        # Size reduction
        for j in range(k - 1, -1, -1):
            q = round(mu[k, j])
            if q != 0:
                basis[k] -= q * basis[j]
                mu[k, j] -= q
        # Recompute B[k] and norm_B[k] after size reduction
        B[k] = basis[k]
        for j in range(k):
            mu[k, j] = np.dot(B[k], B[j]) / np.dot(B[j], B[j])
            B[k] -= mu[k, j] * B[j]
        norm_B[k] = np.dot(B[k], B[k])
        if norm_B[k] == 0:
            raise ValueError(
                f"Vector B[{k}] has zero norm after size reduction; basis vectors may be linearly dependent.")
        # Lovász condition
        if norm_B[k] >= (delta - mu[k, k - 1] ** 2) * norm_B[k - 1]:
            k += 1
        else:
            # Swap basis vectors
            basis[[k, k - 1]] = basis[[k - 1, k]]
            # Recompute Gram-Schmidt coefficients and norms
            for i in range(k - 1, n):
                B[i] = basis[i]
                for j in range(i):
                    denom = np.dot(B[j], B[j])
                    if denom == 0:
                        raise ValueError(
                            f"Zero norm encountered in B[{j}] after swapping; basis vectors may be linearly dependent.")
                    mu[i, j] = np.dot(B[i], B[j]) / denom
                for j in range(i):
                    B[i] -= mu[i, j] * B[j]
                norm_B[i] = np.dot(B[i], B[i])
                if norm_B[i] == 0:
                    raise ValueError(
                        f"Vector B[{i}] has zero norm after swapping; basis vectors may be linearly dependent.")
            k = max(k - 1, 1)
    return basis


def niggli_reduce_cell(a: float, b: float, c: float, alpha: float, beta: float, gamma: float,
                       tol: float = 1e-5) -> tuple:
    """
    Get the Niggli reduced lattice using the numerically stable algorithm
    proposed by R. W. Grosse-Kunstleve, N. K. Sauter, & P. D. Adams,
    Acta Crystallographica Section A Foundations of Crystallography, 2003,
    60(1), 1-6. doi:10.1107/S010876730302186X.

    Args:
        a (float): Unit cell parameter a.
        b (float): Unit cell parameter b.
        c (float): Unit cell parameter c.
        alpha (float): Unit cell angle alpha in degrees.
        beta (float): Unit cell angle beta in degrees.
        gamma (float): Unit cell angle gamma in degrees.
        tol (float, optional): Numerical tolerance. Defaults to 1e-5.

    Returns:
        tuple: Niggli-reduced unit cell parameters.
    """
    # Convert angles from degrees to radians
    alpha_rad = np.radians(alpha)
    beta_rad = np.radians(beta)
    gamma_rad = np.radians(gamma)

    # Compute the lattice vectors in Cartesian coordinates
    v_a = np.array([a, 0.0, 0.0])
    v_b = np.array([b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0.0])
    c_x = c * np.cos(beta_rad)
    sin_gamma = np.sin(gamma_rad)
    if sin_gamma == 0:
        raise ValueError("Invalid gamma angle resulting in division by zero.")
    c_y = c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / sin_gamma
    c_z_sq = c ** 2 - c_x ** 2 - c_y ** 2
    if c_z_sq < 0:
        c_z_sq = 0.0  # Correct for numerical errors
    c_z = np.sqrt(c_z_sq)
    v_c = np.array([c_x, c_y, c_z])

    # Lattice matrix
    matrix = np.array([v_a, v_b, v_c])
    matrix = lll_reduction(matrix)

    # Compute the volume of the unit cell
    volume = np.dot(v_a, np.cross(v_b, v_c))
    if volume <= 0:
        raise ValueError("Invalid unit cell parameters resulting in non-positive volume.")

    e = tol * volume ** (1 / 3)

    # Define metric tensor
    G = np.dot(matrix, matrix.T)
    G = (G + G.T) / 2  # Ensure symmetry

    # This sets an upper limit on the number of iterations.

    for _ in range(100):
        # The steps are labelled as Ax as per the labelling scheme in the
        # paper.
        A, B, C, E, N, Y = (
            G[0, 0], G[1, 1], G[2, 2],
            2 * G[1, 2], 2 * G[0, 2], 2 * G[0, 1]
        )

        if B + e < A or (abs(A - B) < e and abs(E) > abs(N) + e):
            # A1
            M = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, -1]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            A, B, C, E, N, Y = (
                G[0, 0],
                G[1, 1],
                G[2, 2],
                2 * G[1, 2],
                2 * G[0, 2],
                2 * G[0, 1],
            )

        if (C + e < B) or (abs(B - C) < e and abs(N) > abs(Y) + e):
            # A2
            M = np.array([[-1, 0, 0], [0, 0, -1], [0, -1, 0]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            continue

        ll = 0 if abs(E) < e else E / abs(E)
        m = 0 if abs(N) < e else N / abs(N)
        n = 0 if abs(Y) < e else Y / abs(Y)
        if ll * m * n == 1:
            # A3
            i = -1 if ll == -1 else 1
            j = -1 if m == -1 else 1
            k = -1 if n == -1 else 1
            M = np.diag((i, j, k))
            G = np.dot(np.transpose(M), np.dot(G, M))
        elif ll * m * n in (0, -1):
            # A4
            i = -1 if ll == 1 else 1
            j = -1 if m == 1 else 1
            k = -1 if n == 1 else 1

            if i * j * k == -1:
                if n == 0:
                    k = -1
                elif m == 0:
                    j = -1
                elif ll == 0:
                    i = -1
            M = np.diag((i, j, k))
            G = np.dot(np.transpose(M), np.dot(G, M))

        A, B, C, E, N, Y = (
            G[0, 0],
            G[1, 1],
            G[2, 2],
            2 * G[1, 2],
            2 * G[0, 2],
            2 * G[0, 1],
        )

        # A5
        if abs(E) > B + e or (abs(E - B) < e and Y - e > 2 * N) or (abs(E + B) < e and -e > Y):
            M = np.array([[1, 0, 0], [0, 1, -E / abs(E)], [0, 0, 1]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            continue

        # A6
        if abs(N) > A + e or (abs(A - N) < e and Y - e > 2 * E) or (abs(A + N) < e and -e > Y):
            M = np.array([[1, 0, -N / abs(N)], [0, 1, 0], [0, 0, 1]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            continue

        # A7
        if abs(Y) > A + e or (abs(A - Y) < e and N - e > 2 * E) or (abs(A + Y) < e and -e > N):
            M = np.array([[1, -Y / abs(Y), 0], [0, 1, 0], [0, 0, 1]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            continue

        # A8
        if -e > E + N + Y + A + B or (abs(E + N + Y + A + B) < e < Y + (A + N) * 2):
            M = np.array([[1, 0, 1], [0, 1, 1], [0, 0, 1]])
            G = np.dot(np.transpose(M), np.dot(G, M))
            continue

        break

    # Extract reduced lattice parameters from G
    A, B, C = G[0, 0], G[1, 1], G[2, 2]
    E, N, Y = 2 * G[1, 2], 2 * G[0, 2], 2 * G[0, 1]

    a_r = np.sqrt(A)
    b_r = np.sqrt(B)
    c_r = np.sqrt(C)

    cos_alpha_r = E / (2 * b_r * c_r)
    cos_beta_r = N / (2 * a_r * c_r)
    cos_gamma_r = Y / (2 * a_r * b_r)

    # Ensure cosine values are within valid range due to numerical errors
    cos_alpha_r = max(min(cos_alpha_r, 1.0), -1.0)
    cos_beta_r = max(min(cos_beta_r, 1.0), -1.0)
    cos_gamma_r = max(min(cos_gamma_r, 1.0), -1.0)

    alpha_r = np.degrees(np.arccos(cos_alpha_r))
    beta_r = np.degrees(np.arccos(cos_beta_r))
    gamma_r = np.degrees(np.arccos(cos_gamma_r))

    return a_r, b_r, c_r, alpha_r, beta_r, gamma_r