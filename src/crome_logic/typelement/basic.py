from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.src.crome_logic.typelement import CromeType


@dataclass(kw_only=True)
class Boolean(CromeType):
    mutex_group: str = ""
    adjacency_set: set[str] = field(default_factory=set)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanControllable(Boolean):
    def __post_init__(self):
        self.controllable = True

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanUncontrollable(Boolean):
    mutex_group: str = ""
    adjacency_set: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.controllable = False

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BoundedInteger(CromeType):
    min: int
    max: int

    def __eq__(self, other):
        if isinstance(other, BoundedInteger):
            if self.name == other.name and type(self).__name__ == type(other).__name__:
                if self.min == other.min and self.max == other.max:
                    return True
            return False
        else:
            raise AttributeError
