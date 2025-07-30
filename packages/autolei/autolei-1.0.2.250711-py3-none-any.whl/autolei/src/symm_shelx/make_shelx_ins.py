from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Union, TextIO, Optional, List, Tuple, Literal

from autolei.src.symm_shelx.shelx_symm_ops import SpaceGroup
from autolei.src.symm_shelx.space_group_finder import DEFAULT_SGC

# Constants for SHELX file generation
X_RAY_WAVELENGTH = 0.71073
ZERR_VALUE = 52.00

# Regular expressions for parsing
_FLOAT_PATTERN = r"[+\-]?(?:\d*\.\d+|\d+)(?:[Ee][+\-]?\d+)?"
_CELL_PATTERN = re.compile(rf"^CELL\s+(({_FLOAT_PATTERN}\s+){{5}}{_FLOAT_PATTERN})$", re.MULTILINE)
_CELLSD_PATTERN = re.compile(rf"^CELLSD\s+(({_FLOAT_PATTERN}\s+){{5}}{_FLOAT_PATTERN})$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class UnitCell:
    """Crystallographic unit cell with optional standard uncertainties."""
    a: float
    b: float
    c: float
    alpha: float
    beta: float
    gamma: float
    sd_a: Optional[float] = None
    sd_b: Optional[float] = None
    sd_c: Optional[float] = None
    sd_alpha: Optional[float] = None
    sd_beta: Optional[float] = None
    sd_gamma: Optional[float] = None

    def parameters(self) -> Tuple[float, float, float, float, float, float]:
        return self.a, self.b, self.c, self.alpha, self.beta, self.gamma

    def uncertainties(self) -> Tuple[
        Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
        return self.sd_a, self.sd_b, self.sd_c, self.sd_alpha, self.sd_beta, self.sd_gamma


# Parsing function
def parse_p4p_unit_cells(source: Union[Path, TextIO, str]) -> List[UnitCell]:
    """Extract unit-cell parameters and uncertainties from a P4P file or text."""
    if hasattr(source, 'read'):
        content = source.read()
    else:
        path = Path(source)
        content = path.read_text(encoding='utf-8', errors='ignore') if path.exists() else str(source)

    cell_matches = [tuple(map(float, m.group(1).split())) for m in _CELL_PATTERN.finditer(content)]
    sd_matches = [tuple(map(float, m.group(1).split())) for m in _CELLSD_PATTERN.finditer(content)]

    cells: List[UnitCell] = []
    for i, (a, b, c, alpha, beta, gamma) in enumerate(cell_matches):
        sd = sd_matches[i] if i < len(sd_matches) else ()
        sd_full = list(sd) + [None] * (6 - len(sd))
        cells.append(UnitCell(a, b, c, alpha, beta, gamma, *sd_full))
    return cells


# Card generator functions
def _card_title(stem: str, full_sym: str) -> str:
    return f"TITL {stem} in {full_sym}"


def _card_cell(cell: UnitCell) -> str:
    a, b, c, alpha, beta, gamma = cell.parameters()
    return (f"CELL {X_RAY_WAVELENGTH:.5f}  "
            f"{a:8.4f}  {b:8.4f}  {c:8.4f}  "
            f"{alpha:7.3f}  {beta:7.3f}  {gamma:7.3f}")


def _card_zerr(cell: UnitCell) -> str:
    sa, sb, sc, salp, sbet, sgam = cell.uncertainties()

    def fmt_len(x: Optional[float]) -> str:
        return f"{x:7.4f}" if x is not None else " 0.0000"

    def fmt_ang(x: Optional[float]) -> str:
        return f"{x:6.3f}" if x is not None else " 0.000"

    return (f"ZERR {ZERR_VALUE:6.2f}  "
            f"{fmt_len(sa)}  {fmt_len(sb)}  {fmt_len(sc)}  "
            f"{fmt_ang(salp)}  {fmt_ang(sbet)}  {fmt_ang(sgam)}")


def _card_sfac_unit(composition: str) -> List[str]:
    if not composition:
        return [f"SFAC C", f"UNIT 1"]
    elems = re.findall(r'([A-Z][a-z]*)(\d*)', composition)
    sfac = " ".join(el for el, _ in elems)
    units = [str(int(cnt) if cnt else 1) for _, cnt in elems]
    return [f"SFAC {sfac}", f"UNIT {' '.join(units)}"]


def _card_method(instruction: str) -> str:
    return instruction.upper()


def _card_hklf(value: int = 4) -> str:
    return f"HKLF {value}"


def _card_end() -> str:
    return "END"


def add_custom_card(keyword: str, args: str) -> str:
    """Create a generic SHELX card from keyword and arguments."""
    return f"{keyword.upper()} {args}"


# Main writer using card functions

def write_shelxt_ins(
        space_group: str,
        p4p_file: Path,
        unit_cell: UnitCell,
        composition: str = "C",
        index: Optional[int] = None,
        extra_cards: Optional[List[Tuple[str, str]]] = None,
        *,
        instruction: Literal["TREF", "PATT", "TEXP"] | str = "TREF",
) -> Path:
    """
    Generate a SHELX .ins file with modular card generation.

    Args:
        space_group: Hall or Hermann–Mauguin symbol.
        p4p_file: Path to source .p4p file for naming.
        unit_cell: Parsed unit-cell information.
        composition: Empirical formula (e.g., 'Zn3Si4O10(OH)2').
        index: Optional index to append to filename.
        extra_cards: List of (keyword, args) for additional cards.
        instruction: SHELXT instruction before HKLF (default 'TREF').

    Returns:
        Path to the created .ins file.
    """
    # Prepare space group and paths
    hall = DEFAULT_SGC.get_hall_number(space_group)
    sg = SpaceGroup(hall)
    stem = p4p_file.stem if index is None else f"{p4p_file.stem}_{index}"
    ins_path = p4p_file.with_name(f"{stem}.ins")

    # Build lines
    lines: List[str] = [_card_title(stem, sg.international_full), _card_cell(unit_cell), _card_zerr(unit_cell),
                        sg.shelx_latt()]
    lines.extend(sg.shelx_symm())
    lines.extend(_card_sfac_unit(composition))

    # Insert any extra cards
    if extra_cards:
        for key, args in extra_cards:
            lines.append(add_custom_card(key, args))

    lines.append(_card_method(instruction))
    lines.append(_card_hklf())
    lines.append(_card_end())

    # Write file
    ins_text = "\n".join(lines) + "\n"
    ins_path.write_text(ins_text, encoding="utf-8", newline="\n")
    return ins_path
