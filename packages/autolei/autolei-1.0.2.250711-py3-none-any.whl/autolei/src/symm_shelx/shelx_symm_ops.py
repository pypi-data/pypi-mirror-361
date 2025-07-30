"""
SpaceGroup class
=================
A lightweight wrapper around *spglib* space‑group data.
It provides an interface to access space group information, including
Hermann–Mauguin symbols, Hall symbols, symmetry operations, and SHELX
instructions.
"""

from __future__ import annotations

import itertools
import re
from fractions import Fraction
from typing import Dict, List, Tuple, Optional, Union, Set

import numpy as np
import spglib

# Import renamed for clarity
from .space_group_finder import DEFAULT_SGC

# ─── Constants and Shared Resources ─────────────────────────────────────────────

# Centering translations (fractional) - used by both SpaceGroup and find_sg_from_line
CENTERING_VECTORS = {
    "P": [(0, 0, 0)],
    "I": [(0, 0, 0), (0.5, 0.5, 0.5)],
    "F": [(0, 0, 0), (0, 0.5, 0.5), (0.5, 0, 0.5), (0.5, 0.5, 0)],
    "A": [(0, 0, 0), (0, 0.5, 0.5)],
    "B": [(0, 0, 0), (0.5, 0, 0.5)],
    "C": [(0, 0, 0), (0.5, 0.5, 0)],
    "R": [(0, 0, 0), (2 / 3, 1 / 3, 1 / 3), (1 / 3, 2 / 3, 2 / 3)],
}

# Mapping from SHELX LATT numbers to centerings
LATT_TO_CENTERING = {
    1: "P", 2: "I", 3: "R", 4: "F", 5: "A", 6: "B", 7: "C",
    -1: "P", -2: "I", -3: "R", -4: "F", -5: "A", -6: "B", -7: "C"
}

# Regex patterns for SYMM parsing
FRAC_PATTERN = re.compile(r'([+\-])?(\d+)/(\d+)')  # e.g. +1/2
VAR_PATTERN = re.compile(r'([+\-]?)(x|y|z)')

# Type aliases for clarity
RotMatrix = np.ndarray  # 3x3 int array
Translation = np.ndarray  # 3-vector float array
SymOp = Tuple[RotMatrix, Translation]


class SpaceGroup:
    """
    Lightweight wrapper around *spglib* space‑group data.

    Public attributes
    -----------------
    hall_number : int
    international_number : int
    international_symbol : str
    hall_symbol : str
    lattice_type : str
    symops : list[tuple[np.ndarray, np.ndarray]]
    point_group : str
    crystal_system : str
    centrosymmetric : bool
    """

    __slots__ = ("_hall", "_symops", "_sg_type")

    # Class-wide cache for HM symbol to Hall number mapping
    _HM2HALL: Dict[str, int] = {}

    def __init__(self, identifier: Union[int, str, None] = None) -> None:
        """
        Initialize a SpaceGroup object.
        
        Args:
            identifier: International number (1-230), Hall number (1-530), 
                       or Hermann-Mauguin symbol
        """
        self._hall = self._sg_type = None
        self._symops: List[SymOp] = []

        if identifier is not None:
            self.set(identifier)

    def set(self, identifier: Union[int, str], /) -> "SpaceGroup":
        """(Re‑)initialise from number, HM symbol, or Hall number."""
        self._hall = self._resolve_identifier(identifier)
        self._sg_type = spglib.get_spacegroup_type(self._hall)
        self._symops = self._noncentred_symops(self._hall)
        return self

    @classmethod
    def _resolve_identifier(cls, ident: Union[int, str]) -> int:
        """Return Hall number (1‑530) from any allowed identifier."""
        if isinstance(ident, int):
            if 1 <= ident <= 230:  # international number
                return spglib.get_spacegroup_type(ident).hall_number
            if 1 <= ident <= 530:  # Hall number
                return ident
            raise ValueError(f"Invalid space‑group number: {ident}")

        # Hermann–Mauguin string
        if not cls._HM2HALL:
            cls._build_hm_to_hall_cache()

        key = ident.replace(" ", "")
        try:
            return cls._HM2HALL[key]
        except KeyError:
            raise ValueError(f"Unknown space‑group symbol: {ident}") from None

    @classmethod
    def _build_hm_to_hall_cache(cls) -> None:
        """Build cache mapping Hermann-Mauguin symbols to Hall numbers."""
        for h in range(1, 531):
            sg = spglib.get_spacegroup_type(h)
            cls._HM2HALL[sg.international_short.replace(" ", "")] = sg.hall_number

    def _noncentred_symops(self, hall: int) -> List[SymOp]:
        """Get symmetry operations without pure-centring shifts."""
        raw = spglib.get_symmetry_from_database(hall)
        Rs, ts = raw["rotations"], raw["translations"]
        centres = self._get_centering_vectors(self.lattice_type)

        I3 = np.eye(3, dtype=int)
        kept: Dict[Tuple[bytes, bytes], SymOp] = {}

        for R, t in zip(Rs, ts):
            # vectorised canonisation over all centring shifts
            t_cands = np.mod(t - centres, 1.0)
            t_canon = t_cands[np.lexsort(t_cands.T)][0]

            if np.array_equal(R, I3) and not np.allclose(t_canon, 0.0):
                continue  # drop pure‑translation centres

            key = (R.tobytes(), np.round(t_canon, 6).tobytes())
            kept.setdefault(key, (R, t_canon))

        return list(kept.values())

    @staticmethod
    def _get_centering_vectors(letter: Optional[str]) -> np.ndarray:
        """Get centering vectors as a numpy array."""
        if letter is None:
            letter = "P"
        return np.array(CENTERING_VECTORS[letter], dtype=np.float64)

    @staticmethod
    def _frac(val: float) -> str:
        """Format a floating point value as a fraction string."""
        if abs(val) < 1e-6:
            return "0"
        frac = Fraction(val).limit_denominator(12)  # exact for 2,3,4,6, …
        if frac.denominator == 1:
            return "-" if frac.numerator == -1 else ""
        return f"{frac.numerator}/{frac.denominator}"

    def _op_to_shelx(self, R: np.ndarray, t: np.ndarray) -> str:
        """Convert a symmetry operation to SHELX format."""
        axes = "XYZ"
        terms = []
        for i in range(3):
            parts = []
            for j, coef in enumerate(R[i]):
                if coef:
                    sign = "-" if coef < 0 else "+"
                    prefix = "" if abs(coef) == 1 else str(abs(coef))
                    parts.append(f"{sign}{prefix}{axes[j]}")
            if abs(t[i]) > 1e-6:
                sign = "+" if t[i] > 0 else ""
                parts.append(f"{sign}{self._frac(abs(t[i]))}")
            terms.append("".join(parts)[1:] if parts and parts[0].startswith("+") else "".join(parts))
        return ",".join(terms)

    # Properties
    @property
    def hall_number(self) -> Optional[int]:
        """Return the Hall number (1-530) of the space group."""
        return self._hall

    @property
    def international_number(self) -> Optional[int]:
        """Return the international number (1-230) of the space group."""
        return getattr(self._sg_type, "number", None)

    @property
    def international_symbol(self) -> Optional[str]:
        """Return the Hermann–Mauguin symbol of the space group."""
        return getattr(self._sg_type, "international_short", None)

    @property
    def hall_symbol(self) -> Optional[str]:
        """Return the Hall symbol of the space group."""
        return getattr(self._sg_type, "hall_symbol", None)

    @property
    def lattice_type(self) -> Optional[str]:
        """Return the lattice type of the space group."""
        if not self.hall_symbol:
            return None
        return self.hall_symbol[0] if self.hall_symbol[0] != '-' else self.hall_symbol[1]

    @property
    def symops(self) -> List[SymOp]:
        """Return the symmetry operations of the space group."""
        return self._symops

    @property
    def point_group(self) -> Optional[str]:
        """Return the point group symbol of the space group."""
        return getattr(self._sg_type, "pointgroup_symbol", None)

    @property
    def crystal_system(self) -> Optional[str]:
        """Return the crystal system of the space group."""
        return getattr(self._sg_type, "international", None)

    @property
    def centrosymmetric(self) -> bool:
        """Return True if the space group is centrosymmetric."""
        i3 = np.eye(3, dtype=int)
        return any(np.array_equal(R, -i3) for R, _ in self._symops)

    @property
    def international_full(self) -> Optional[str]:
        """Return the full Hermann–Mauguin symbol of the space group."""
        return getattr(self._sg_type, "international_full", None)

    @property
    def shelx_latt_number(self) -> int:
        """Return SHELX LATT card for the space group."""
        code = {
            "P": 1, "I": 2, "R": 3, "F": 4, "A": 5, "B": 6, "C": 7
        }.get(self.lattice_type or "P", 1)
        return code if self.centrosymmetric else -code

    @property
    def shelx_symm_list(self) -> list[str]:
        """Return the list of SHELX symmetry operations."""
        if not self._symops:
            raise ValueError("space group not initialised")

        I3 = np.eye(3, dtype=int)
        seen: Set[Tuple[bytes, bytes]] = set()
        lines: List[str] = []

        for R, t in self._symops[1:]:  # skip identity
            if self.centrosymmetric:
                # 1) drop the pure inversion itself
                if np.array_equal(R, -I3):
                    continue

                # 2) keep only one representative of each {op, −op} pair
                key = (R.tobytes(), np.round(t % 1.0, 6).tobytes())
                inv_key = ((-R).tobytes(), np.round((-t) % 1.0, 6).tobytes())
                if inv_key in seen:  # already have its partner
                    continue
                seen.add(key)

            lines.append(f"{self._op_to_shelx(R, t)}")
        return lines

    # SHELX Utility Methods
    def shelx_latt(self) -> str:
        """Return SHELX LATT card for the space group."""
        return f"LATT {self.shelx_latt_number}"

    def shelx_symm(self) -> list[str]:
        """Return the list of SHELX-SYMM cards."""
        return [f"SYMM {line}" for line in self.shelx_symm_list]

    def __repr__(self) -> str:
        """String representation of the SpaceGroup."""
        return f"SpaceGroup({self.hall_number}, {self.international_full})"


# SYMM parsing functions
def parse_component(comp: str) -> Tuple[List[int], float]:
    """Parse one component of a SYMM operation."""
    row = [0, 0, 0]  # coefficients in front of x,y,z
    # variables with sign
    for sign, xyz in VAR_PATTERN.findall(comp):
        idx = 'xyz'.index(xyz)
        row[idx] += -1 if sign == '-' else +1

    # strip variables and evaluate remaining fraction/decimal
    rest = VAR_PATTERN.sub('', comp)
    rest = FRAC_PATTERN.sub(lambda m:
                            str(float(f'{m.group(1) or ""}{int(m.group(2)) / int(m.group(3))}')),
                            rest)
    trans = float(rest) if rest else 0.0
    return row, trans


def parse_symm_line(text: str) -> SymOp:
    """Parse a SYMM line into rotation matrix and translation vector."""
    comps = [c.strip().lower() for c in text.split(',')]
    if len(comps) != 3:
        raise ValueError(f"Bad SYMM triplet: {text}")

    rot, tr = [], []
    for comp in comps:
        r, t = parse_component(comp)
        rot.append(r)
        tr.append(t)

    return np.array(rot, dtype=int), np.array(tr, dtype=float)


def find_sg_from_line(text: str) -> SpaceGroup | None:
    """Deduce Hall symbol directly from LATT/SYMM cards."""
    latt, symm_ops, symm_lines = None, [], []

    for line in text.splitlines():
        tokens = line.split(maxsplit=1)
        if not tokens:
            continue
        tag = tokens[0].upper()
        if tag == 'LATT':
            latt = int(tokens[1])
        elif tag == 'SYMM':
            rot, tr = parse_symm_line(tokens[1])
            symm_lines.append(tokens[1])
            symm_ops.append((rot, tr))

    if latt is None:
        raise ValueError("Missing LATT card")

    # identity is implicit
    identity = (np.eye(3, dtype=int), np.zeros(3))
    base = [identity, *symm_ops]

    # inversion at origin if LATT > 0 (centrosymmetric)
    if latt > 0:
        inv = (-np.eye(3, dtype=int), np.zeros(3))
        base += [(inv[0] @ r, -inv[0] @ t + inv[1]) for r, t in base]

    # apply centring shifts
    centering_type = LATT_TO_CENTERING[latt]
    full_rot, full_tr = [], []

    for (r, t), shift in itertools.product(base, CENTERING_VECTORS[centering_type]):
        full_rot.append(r)
        full_tr.append((t + shift) % 1.0)  # keep in [0,1)

    rotations = np.array(full_rot, dtype=int)
    translations = np.array(full_tr, dtype=float)

    # spglib does the matching
    sgt = spglib.get_spacegroup_type_from_symmetry(rotations, translations)
    spg_finder = DEFAULT_SGC
    if sgt:
        available_sgs = spg_finder.list_candidates(sgt.number)
        for sg in available_sgs:
            sg = SpaceGroup(sg.hall_number)
            if latt == sg.shelx_latt_number and symm_lines == sg.shelx_symm_list:
                return sg
    return None


if __name__ == "__main__":
    # Example of finding space group from SHELX instructions
    snip = """
    LATT 2
    SYMM -X+1/2,Y,-Z
    """
    print(find_sg_from_line(snip))
