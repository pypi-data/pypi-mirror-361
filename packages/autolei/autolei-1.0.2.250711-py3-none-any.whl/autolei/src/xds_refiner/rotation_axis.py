from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

import numpy as np
from numba import njit, prange, get_thread_id, get_num_threads

# ----------------------------------------------------------------------------
# External helpers from your code base
# ----------------------------------------------------------------------------
from ..xds_input import replace_value, extract_keywords

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
_DEFAULT_HIST_BINS: Tuple[int, int] = (1000, 500)
_MAX_SAMPLE_PAIRS: int = 2_000_000


# ----------------------------------------------------------------------------
# Small helper functions (unchanged from original, but tidied)
# ----------------------------------------------------------------------------
def parse_xds_inp(fn: str) -> tuple:
    """
    Parses the XDS.INP file to extract key parameters.

    Args:
        fn (str): Path to the XDS.INP file.

    Returns:
        tuple: A tuple containing:
            - beam_center (tuple): (ORGX, ORGY) coordinates.
            - osc_angle (float): Oscillation angle in degrees.
            - pixelsize (float): Pixel size in mm.
            - wavelength (float): X-ray wavelength in Å.
            - omega_current (float): Current omega angle in degrees.
    """
    with open(fn, "r") as f:
        params = extract_keywords(f.readlines())

    rotx, roty, rotz = map(float, params["ROTATION_AXIS"][0].split()[:3])
    omega_current = np.degrees(np.arctan2(roty, rotx))
    pixelsize = float(params["QX"][0]) / (float(params["DETECTOR_DISTANCE"][0]) * float(params["X-RAY_WAVELENGTH"][0]))

    return (
        (float(params["ORGX"][0]), float(params["ORGY"][0])),
        float(params["OSCILLATION_RANGE"][0]),
        pixelsize,
        float(params["X-RAY_WAVELENGTH"][0]),
        omega_current,
    )


def change_axis(xds_dir: str, axis_angle: float) -> None:
    """Rewrite *XDS.INP* with a new ROTATION_AXIS* line."""
    xds_path = os.path.join(xds_dir, "XDS.INP")
    with open(xds_path, "r+", encoding="utf‑8") as fh:
        lines = fh.readlines()
        axis_str = f"{np.cos(np.radians(axis_angle)):.4f} {np.sin(np.radians(axis_angle)):.4f} 0"
        lines = replace_value(lines, "ROTATION_AXIS", [axis_str], comment=False)
        fh.seek(0)
        fh.writelines(lines)
        fh.truncate()


# ---------------- coordinate transforms -------------------------------------
def make_2d_rotmat(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]], dtype=np.float32)


def make(arr: np.ndarray, omega: float, wavelength: float) -> np.ndarray:
    """Convert 2‑D spot coords + angle into reciprocal‑space XYZ."""
    reflections = arr[:, :2]
    angle = arr[:, 2]

    rotated = reflections @ make_2d_rotmat(np.radians(omega))
    y, x = rotated.T

    R = 1.0 / wavelength
    sqrt_val = np.sqrt(np.clip(R ** 2 - x ** 2 - y ** 2, 0.0, None))
    C = (R - sqrt_val)[:, None]

    sin_a = np.sin(angle)
    cos_a = np.cos(angle)

    xyz = np.column_stack(
        (
            x * cos_a,
            y,
            -x * sin_a,
        )
    ) + C * np.column_stack((-sin_a, np.zeros_like(angle), -cos_a))

    return xyz.astype(np.float32)


# ----------------------------------------------------------------------------
# Fast pair‑orientation histogram (Numba)
# ----------------------------------------------------------------------------


@njit(fastmath=True, inline="always")
def _xyz_to_cyl(sx: float, sy: float, sz: float) -> Tuple[float, float]:
    phi = np.arctan2(sy, sx)
    theta = np.arctan2(sz, np.hypot(sx, sy))
    return phi, theta


@njit(parallel=True, fastmath=True)
def _hist_kernel(xyz: np.ndarray, edges_phi: np.ndarray, edges_theta: np.ndarray) -> np.ndarray:
    n = xyz.shape[0]
    bins_phi = edges_phi.size - 1
    bins_theta = edges_theta.size - 1

    min_phi = edges_phi[0]
    min_theta = edges_theta[0]
    inv_dphi = 1.0 / (edges_phi[1] - edges_phi[0])
    inv_dtheta = 1.0 / (edges_theta[1] - edges_theta[0])

    # Determine number of threads at runtime
    nthreads = get_num_threads()
    # Allocate per-thread local histograms to avoid atomic operations
    local_hists = np.zeros((nthreads, bins_phi, bins_theta), dtype=np.int64)

    for i in prange(n - 1):
        tid = get_thread_id()
        xi, yi, zi = xyz[i]
        for j in range(i + 1, n):
            sx = xi - xyz[j, 0]
            sy = yi - xyz[j, 1]
            sz = zi - xyz[j, 2]

            phi, theta = _xyz_to_cyl(sx, sy, sz)
            bp = int((phi - min_phi) * inv_dphi)
            bt = int((theta - min_theta) * inv_dtheta)
            if 0 <= bp < bins_phi and 0 <= bt < bins_theta:
                local_hists[tid, bp, bt] += 1

    # Merge local histograms into final global histogram
    hist = np.zeros((bins_phi, bins_theta), dtype=np.int64)
    for t in range(nthreads):
        for p in range(bins_phi):
            for q in range(bins_theta):
                hist[p, q] += local_hists[t, p, q]

    return hist


def _hist_exact(xyz: np.ndarray, bins: Tuple[int, int]) -> np.ndarray:
    edges_phi = np.linspace(-np.pi, np.pi, bins[0] + 1, dtype=np.float32)
    edges_theta = np.linspace(-np.pi / 2, np.pi / 2, bins[1] + 1, dtype=np.float32)
    return _hist_kernel(xyz.astype(np.float32), edges_phi, edges_theta)


def _hist_sample(xyz: np.ndarray, bins: Tuple[int, int], max_pairs: int) -> np.ndarray:
    n = len(xyz)
    total_pairs = n * (n - 1) // 2
    if total_pairs <= max_pairs:
        return _hist_exact(xyz, bins)

    rng = np.random.default_rng()
    i = rng.integers(0, n, size=max_pairs, dtype=np.int64)
    j = rng.integers(0, n, size=max_pairs, dtype=np.int64)
    keep = i != j
    i, j = i[keep], j[keep]

    sx = xyz[i, 0] - xyz[j, 0]
    sy = xyz[i, 1] - xyz[j, 1]
    sz = xyz[i, 2] - xyz[j, 2]

    phi = np.arctan2(sy, sx)
    theta = np.arctan2(sz, np.hypot(sx, sy))

    H, _, _ = np.histogram2d(
        phi,
        theta,
        bins=bins,
        range=[[-np.pi, np.pi], [-np.pi / 2, np.pi / 2]],
    )
    return H.astype(np.int64)


def cylinder_histo(
        xyz: np.ndarray,
        bins: Tuple[int, int] = _DEFAULT_HIST_BINS,
        *,
        method: str = "auto",
        max_pairs: int = _MAX_SAMPLE_PAIRS,
) -> np.ndarray:
    if method == "exact":
        return _hist_exact(xyz, bins)
    if method == "sample":
        return _hist_sample(xyz, bins, max_pairs)
    n = len(xyz)
    return _hist_exact(xyz, bins) if n * (n - 1) // 2 <= max_pairs else _hist_sample(xyz, bins, max_pairs)


# ----------------------------------------------------------------------------
# omega‑search helpers
# ----------------------------------------------------------------------------
def _evaluate_omega(omega: float, arr: np.ndarray, wavelength: float, bins: Tuple[int, int], sample: bool) -> Tuple[
    float, float]:
    xyz = make(arr, omega, wavelength)
    H = cylinder_histo(xyz, bins=bins, method="sample" if sample else "auto")
    return float(np.var(H, ddof=1)), omega


def find_optimised_axis(
        arr: np.ndarray,
        omega_start: float,
        wavelength: float,
        plusminus: float,
        step: float,
        bins: Tuple[int, int] = _DEFAULT_HIST_BINS,
        *,
        sampling: bool = True,
        max_workers: int | None = None,
) -> float:
    values = np.arange(omega_start - plusminus, omega_start + plusminus + step, step)
    best_var, best_omega = -np.inf, omega_start
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = [pool.submit(_evaluate_omega, omega, arr, wavelength, bins, sampling) for omega in values]
        for fut in futs:
            var, omega = fut.result()
            if var > best_var:
                best_var, best_omega = var, omega
    return best_omega


# ----------------------------------------------------------------------------
# I/O helpers (unchanged logic)
# ----------------------------------------------------------------------------

def load_spot_xds(fn: str, beam_center: Tuple[float, float], osc_angle: float, pixelsize: float) -> np.ndarray | None:
    try:
        arr = np.loadtxt(fn)
    except OSError:
        return None
    if arr.size == 0:
        return None
    refl = arr[:, :2] - np.asarray(beam_center)
    angle = arr[:, 2] * np.radians(osc_angle)
    refl *= pixelsize
    return np.column_stack((refl, angle))


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# Top‑level driver
# ----------------------------------------------------------------------------

def refine_axis(xds_dir: str) -> bool:
    xds_inp = os.path.join(xds_dir, "XDS.INP")
    spot_xds = os.path.join(xds_dir, "SPOT.XDS")

    beam_center, osc_angle, pixelsize, wavelength, omega_current = parse_xds_inp(xds_inp)
    if omega_current > 180.0:
        omega_current -= 360.0

    arr = load_spot_xds(spot_xds, beam_center, osc_angle, pixelsize)
    if arr is None:
        print("No SPOT.XDS data – axis not refined.")
        return False

    # coarse scan ±10° in 1° steps
    omega_coarse = find_optimised_axis(
        arr,
        omega_current,
        wavelength,
        plusminus=10.0,
        step=1.0,
        bins=_DEFAULT_HIST_BINS,
        sampling=True,
    )
    print(f"Best omega (coarse): {-omega_coarse:.3f}°")

    # fine scan ±1° in 0.1° steps around coarse optimum
    omega_fine = find_optimised_axis(
        arr,
        omega_coarse,
        wavelength,
        plusminus=1.0,
        step=0.1,
        bins=_DEFAULT_HIST_BINS,
        sampling=True,
    )
    print(f"Best omega (fine): {-omega_fine:.3f}°")
    print(f"Rotation axis found: {-omega_fine:.2f}° / {np.radians(-omega_fine):.3f} rad")

    # update XDS.INP if change is modest (safety)
    if abs(omega_fine - omega_current) < 10.0:
        change_axis(xds_dir, omega_fine)
        print("Correct rotation axis … OK")
        return True

    print("Large deviation – not writing XDS.INP.")
    return False


# -----------------------------------------------------------------------------
# __main__  – simple CLI ------------------------------------------------------
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import cProfile

    cProfile.run(
        "refine_axis(\"/mnt/c/Work/ED/dbb01444/Tessa-2205-6/Tessa-2205-6_10/xds\")",
        sort="tottime")
