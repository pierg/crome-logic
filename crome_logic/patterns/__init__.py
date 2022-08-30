from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, auto

from crome_logic.specification import and_


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

    def __iand__(self, other: Pattern):
        if isinstance(other, Pattern):
            self.formula = and_([self.formula, other.formula])
            return self
        else:
            raise AttributeError

    def __and__(self, other: Pattern):
        if isinstance(other, Pattern):
            new = deepcopy(self)
            return new.__iand__(other)
        else:
            raise AttributeError
