from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


@dataclass(kw_only=True)
class Pattern:
    class Kind(Enum):
        ROBOTIC_MOVEMENT = auto()
        ROBOTIC_TRIGGER = auto()
        DWYER = auto()
        BASIC = auto()

    formula: str = ""
    description: str = ""
    kind: Pattern.Kind

    def __str__(self):
        return str(self.formula)
