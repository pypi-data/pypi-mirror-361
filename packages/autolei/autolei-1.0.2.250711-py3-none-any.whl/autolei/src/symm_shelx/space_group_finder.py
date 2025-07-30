# spacegroup.py — May 2025
"""
Helper module for normalising Hermann–Mauguin symbols and mapping them
into Hall and International space group numbers using spglib.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Final, List, Union

try:
    import spglib
except ImportError as exc:
    raise ImportError("spacegroup requires the 'spglib' package") from exc

# ─────────────────────────────────────────────────────────────────────────────
# Constants for Hermann–Mauguin normalization
_MINUS: Final = "−"
_RE_CLEAN: Final = re.compile(r"[ _()]")
_SCREWS_ALWAYS: Final = {"31", "32", "41", "43", "61", "63", "65", "66"}
_SCREWS_MAYBE: Final = {"21", "42", "62", "64"}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Symbol normalizer

class HMNormalizer:
    """Normalize Hermann–Mauguin labels to a canonical spaced form."""

    @classmethod
    @lru_cache(maxsize=None)
    def to_full_hm(cls, label: str) -> str:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("label must be a non-empty string")
        s = cls._clean(label)
        if not s[0].isalpha():
            raise ValueError("HM symbols must start with a lattice letter")
        tokens = cls._tokenize(s[1:])
        return s[0].upper() + " " + " ".join(tokens)

    @staticmethod
    def _clean(text: str) -> str:
        return _RE_CLEAN.sub("", text.strip().replace(_MINUS, "-"))

    @classmethod
    def _tokenize(cls, body: str) -> List[str]:
        parts: List[str] = []
        i = 0
        while i < len(body):
            c = body[i]
            # barred axis
            if c == '-':
                j = i + 1
                while j < len(body) and body[j].isdigit():
                    j += 1
                parts.append(body[i:j])
                i = j
                continue
            # digits and screws
            if c.isdigit():
                pair = body[i:i + 2]
                remain = len(body) - (i + 2)
                if pair in _SCREWS_ALWAYS or (pair in _SCREWS_MAYBE and remain >= 2):
                    parts.append(pair)
                    i += 2
                    continue
                parts.append(c)
                i += 1
                continue
            # glide
            if c == '/' and i + 1 < len(body) and body[i + 1].isalpha():
                if parts:
                    parts[-1] += '/' + body[i + 1]
                else:
                    parts.append('/' + body[i + 1])
                i += 2
                continue
            # lattice letter
            if c.isalpha():
                parts.append(c)
                i += 1
                continue
            i += 1
        return parts


# ─────────────────────────────────────────────────────────────────────────────
# 2. Data model

@dataclass(frozen=True)
class SpaceGroupInfo:
    hall_number: int
    international_number: int
    hall_symbol: str
    int_short: str
    int_spaced: str

    @classmethod
    def from_spglib(cls, raw) -> SpaceGroupInfo:
        try:
            return cls(
                hall_number=raw.hall_number,
                international_number=raw.number,
                hall_symbol=raw.hall_symbol.strip(),
                int_short=raw.international_short.strip(),
                int_spaced=raw.international.strip(),
            )
        except AttributeError:
            return cls(
                hall_number=raw.get("hall_number"),
                international_number=raw.get("number"),
                hall_symbol=raw.get("hall_symbol").strip(),
                int_short=raw.get("international_short").strip(),
                int_spaced=raw.get("international").strip(),
            )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Registry and search

class SpaceGroupRegistry:
    """In-memory registry of space groups for fast lookup."""

    def __init__(self):
        self._by_hall: Dict[str, List[SpaceGroupInfo]] = {}
        self._by_int: Dict[str, List[SpaceGroupInfo]] = {}
        self._by_number: Dict[int, List[SpaceGroupInfo]] = {}
        self._load()

    def _load(self) -> None:
        for hall_id in range(1, 531):
            try:
                raw = spglib.get_spacegroup_type(hall_id)
            except ValueError:
                break
            info = SpaceGroupInfo.from_spglib(raw)
            self._register(info)

    def _register(self, sg: SpaceGroupInfo) -> None:
        self._by_hall.setdefault(sg.hall_symbol, []).append(sg)
        self._by_int.setdefault(sg.int_short, []).append(sg)
        # include spaced and cleaned forms
        spaced = sg.int_spaced.split('=')[-1].strip()
        self._by_int.setdefault(spaced, []).append(sg)
        self._by_int.setdefault(spaced.replace(' 1', ''), []).append(sg)
        self._by_int.setdefault(HMNormalizer.to_full_hm(sg.int_short), []).append(sg)
        self._by_number.setdefault(sg.international_number, []).append(sg)

    def find(self, key: Union[int, str]) -> list[SpaceGroupInfo] | None:
        # 1) If it’s already an int, go straight to _by_number
        if isinstance(key, int):
            return self._by_number.get(key, [])

        # 2) If it’s a str, strip whitespace and see if it converts to int
        if isinstance(key, str):
            k = key.strip()
            try:
                num = int(k)
            except ValueError:
                pass
            else:
                return self._by_number.get(num, [])

            # 3) Otherwise fall back to the original “string” lookups
            return (
                    self._by_hall.get(k)
                    or self._by_int.get(k)
                    or self._by_int.get(HMNormalizer.to_full_hm(k), [])
            )
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 4. Container with disambiguation rules

class SpaceGroupContainer:
    """Select single preferred Hall or International number from candidates."""
    _AXIS_PREF: Final = ('b1', 'b', 'c1', 'c', 'a1', 'a')
    _ABC_PREF: Final = ('abc',)
    _HR_PREF: Final = ('H', 'R')

    def __init__(self, registry: SpaceGroupRegistry | None = None):
        self._registry = registry or SpaceGroupRegistry()

    def get_hall_number(self, identifier: Union[int, str]) -> int | None:
        infos = self._registry.find(identifier)
        chosen = self._select(infos)
        return chosen.hall_number if chosen else None

    def get_int_number(self, identifier: Union[int, str]) -> int | None:
        infos = self._registry.find(identifier)
        chosen = self._select(infos)
        return chosen.international_number if chosen else None

    def get_int_short(self, identifier: Union[int, str]) -> str | None:
        infos = self._registry.find(identifier)
        chosen = self._select(infos)
        return chosen.int_short if chosen else None

    def list_candidates(self, identifier: Union[int, str]) -> List[SpaceGroupInfo]:
        return self._registry.find(identifier)

    def _select(self, cands: List[SpaceGroupInfo]) -> SpaceGroupInfo | None:
        if not cands:
            return None
        if len(cands) == 1:
            return cands[0]
        # Apply tie-break rules:
        for tag in self._HR_PREF:
            subset = [sg for sg in cands if sg.hall_symbol.startswith(tag)]
            if subset:
                cands = subset
                break
        for axis in self._AXIS_PREF:
            subset = [sg for sg in cands if f" {axis}" in sg.hall_symbol]
            if subset:
                cands = subset
                break
        for tag in self._ABC_PREF:
            subset = [sg for sg in cands if tag in sg.hall_symbol]
            if subset:
                cands = subset
                break
        return min(cands, key=lambda sg: sg.hall_number)


# Default singleton for easy imports
DEFAULT_SGC: Final = SpaceGroupContainer()

if __name__ == "__main__":
    # Example usage and simple smoke-test
    examples = ['P6_3/mmc', 'R-3m', 166, 'P212121', 'C121']
    for e in examples:
        print(e, '→ Hall#', DEFAULT_SGC.get_hall_number(e))
