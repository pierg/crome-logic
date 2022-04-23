from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from crome_logic.patterns import Pattern


@dataclass(kw_only=True)
class Robotic(Pattern):
    class Kind(Enum):
        TRIGGER = auto()
        CORE_MOVEMENT = auto()

    formula: str = ""
    kind: Pattern.Kind

    def __str__(self):
        return str(self.formula)
