from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class PatternKind(Enum):
    ROBOTIC_MOVEMENT = auto()
    ROBOTIC_TRIGGER = auto()
    DWYER = auto()
    BASIC = auto()
    UNKNOWN = auto()


@dataclass
class Pattern:
    formula: str = field(init=False, default="")
    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    arguments: list[dict[str, str]] = field(init=False, default=list)
    kind: PatternKind = field(init=False, default=PatternKind.UNKNOWN)

    def __str__(self):
        return str(self.formula)
