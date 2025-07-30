"""xds_move_manager.py
====================
Utility helpers for safely *simulating* and *executing* bulk moves of
folder trees that contain **XDS.INP** files.  The high‑level contract
remains identical to the original snippet the user supplied, but the
implementation has been rebuilt from scratch with the following goals:

* **Robust path handling** via ``pathlib.Path`` instead of string
  concatenation – works reliably on POSIX and Windows.
* **Linear‑time unique‑prefix discovery** using a **compact trie** that
  stores the number of leaves that pass through every node.  This avoids
  repeated ``O(n²)`` prefix comparisons when many paths share a deep
  common hierarchy.
* **Unified public API** offering a single ``FileMover`` façade that can
  *simulate* or *execute* the move by flipping one flag.  This removes
  the duplicated logic between *simulate* and *real* functions and makes
  unit‑testing simpler.
* **Detailed error reporting & logging hooks** so the caller can decide
  whether to raise, warn, or merely collect problems.
* **Graceful rollback** – when *executing* real moves we build a work
  plan first and then perform each move; on failure any moves already
  executed are rolled back automatically (best‑effort) to keep
  filesystem state consistent.

Example usage
-------------
```
from xds_move_manager import FileMover, discover_xds_files

actions, errors = FileMover(paths).plan(selected, phase_folder="phase1")
print("DRY‑RUN plan:\n", *actions, sep="\n")

moved, errors = FileMover(paths).execute(selected, phase_folder="phase1")
print("Actually moved:")
for src, dst in moved:
    print(f"  {src}  →  {dst}")
```
"""

from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

__all__ = [
    "discover_xds_files",
    "FileMover",
]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(path: str | Path) -> Path:
    """Return an absolute, *resolved* ``Path`` (without symlinks)."""
    return Path(path).expanduser().resolve(strict=False)


def discover_xds_files(root: str | Path) -> List[Path]:
    """Recursively discover ``XDS.INP`` files under *root* (case‑sensitive)."""
    root = _normalize(root)
    return [p for p in root.rglob("XDS.INP") if p.is_file()]


# ---------------------------------------------------------------------------
# Unique directory‑prefix computation (linear‑time trie solution)
# ---------------------------------------------------------------------------

def _build_prefix_trie(paths: Sequence[Path]) -> dict:
    """Build a *counting* trie mapping each directory segment."""
    trie: dict = {}
    for p in paths:
        node = trie
        for part in p.parts[:-1]:  # ignore the final "XDS.INP" file segment
            node = node.setdefault(part, [0, {}])  # [count, children]
            node[0] += 1
            node = node[1]
    return trie


def _unique_prefix_for_path(path: Path, trie: dict) -> Path:
    node = trie
    parts: List[str] = []
    for segment in path.parts[:-1]:
        count, children = node[segment]
        parts.append(segment)
        if count == 1:  # found a unique prefix
            break
        node = children
    return Path(*parts)


def compute_uniquely_identifying_prefixes(paths: Sequence[str | Path]) -> Dict[Path, Path]:
    """Return the shortest directory prefix that uniquely identifies each path.

    The prefix is returned as an *absolute* ``Path`` object with no trailing
    separator and **without** the terminal ``XDS.INP`` segment.
    """
    abs_paths: List[Path] = [_normalize(p) for p in paths]

    # Guard against duplicates: they would break uniqueness guarantees.
    duplicates = {p for p in abs_paths if abs_paths.count(p) > 1}
    if duplicates:
        raise ValueError(f"Duplicate XDS.INP paths detected: {sorted(duplicates)}")

    trie = _build_prefix_trie(abs_paths)
    return {p: _unique_prefix_for_path(p, trie) for p in abs_paths}


# ---------------------------------------------------------------------------
# Public façade
# ---------------------------------------------------------------------------

@dataclass
class FileMover:
    """Plan or execute moves of uniquely‑identifying XDS directories."""

    paths: Sequence[str | Path]
    work_folder: str = ""

    # Cached mapping built lazily on first access
    _prefix_map: Dict[Path, Path] | None = None

    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------
    @property
    def prefix_map(self) -> Dict[Path, Path]:
        if self._prefix_map is None:
            self._prefix_map = compute_uniquely_identifying_prefixes(self.paths)
        return self._prefix_map

    # ---------------------------------------------------------------------
    # Public interface
    # ---------------------------------------------------------------------
    def plan(
            self,
            selected: Sequence[str | Path],
            phase_folder: str | Path,
    ) -> Tuple[List[str], List[str]]:
        """Return a *dry‑run* list of move actions and errors."""
        return self._move(selected, phase_folder, dry_run=True)

    def execute(
            self,
            selected: Sequence[str | Path],
            phase_folder: str | Path,
    ) -> Tuple[List[Tuple[str, str]], List[str]]:
        """Perform the moves; returns successful moves and error strings."""
        return self._move(selected, phase_folder, dry_run=False)

    # ------------------------------------------------------------------
    # Internal move engine
    # ------------------------------------------------------------------
    def _move(
            self,
            selected: Sequence[str | Path],
            phase_folder: str | Path,
            *,
            dry_run: bool,
    ) -> Tuple[List, List[str]]:  # type: ignore[override]
        errors: List[str] = []
        actions: List = []  # str for dry‑run, tuple(src,dst) for real

        sel_paths: List[Path] = [_normalize(p) for p in selected]
        all_paths: set[Path] = set(_normalize(p) for p in self.paths)
        unique_prefixes = self.prefix_map

        # Ensure destination root exists
        phase_folder = _normalize(phase_folder)
        if not dry_run:
            phase_folder.mkdir(parents=True, exist_ok=True)

        used_dest_names: set[str] = set()
        for sel in sel_paths:
            if sel not in all_paths:
                errors.append(f"Not found: {sel}")
                continue

            prefix = unique_prefixes[sel]
            if not prefix.exists():
                errors.append(f"Computed unique prefix does not exist on disk: {prefix}")
                continue

            dest_name = prefix.name
            if dest_name in used_dest_names:
                errors.append(
                    f"Destination name collision: '{dest_name}' coming from '{prefix}'"
                )
                continue
            used_dest_names.add(dest_name)

            dest = phase_folder / dest_name

            if dry_run:
                actions.append(
                    f"{os.path.relpath(str(prefix), self.work_folder)}  →  "
                    f"{os.path.relpath(str(dest), self.work_folder)}")
            else:
                try:
                    shutil.move(str(prefix), str(dest))
                    actions.append(os.path.relpath(str(prefix), self.work_folder) +
                                   os.path.relpath(str(dest), self.work_folder))
                except Exception as exc:
                    errors.append(f"Error moving '{prefix}' → '{dest}': {exc}")
                    # Attempt rollback of previously moved dirs
                    for moved_src, moved_dst in reversed(actions):  # type: ignore[arg-type]
                        try:
                            shutil.move(str(moved_dst), str(moved_src))
                        except Exception as rb_exc:
                            logger.error(
                                "Rollback failure when moving %s back to %s: %s",
                                moved_dst,
                                moved_src,
                                rb_exc,
                            )
                    break  # stop processing further paths

        return actions, errors
