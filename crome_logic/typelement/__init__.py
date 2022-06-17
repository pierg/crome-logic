from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeVar


class TypeKind(Enum):
    """Kinds of CromeType."""

    UNKNOWN = auto()
    SENSOR = auto()
    LOCATION = auto()
    ACTION = auto()
    ACTIVE = auto()
    CONTEXT = auto()
    SENSOR_LOCATION = auto()
    SENSOR_ACTION = auto()


@dataclass(kw_only=True)
class CromeType:
    """Base class fo the types of CROME."""

    name: str
    description: str = ""
    kind: TypeKind = TypeKind.UNKNOWN
    refinement_of: set[AnyCromeType | str] = field(default_factory=set)

    controllable: bool = field(init=False, default=False)

    def __str__(self):
        return self.name

    def __le__(self, other: CromeType):
        if other.name in self.refinement_of:
            return True
        return other.name in self.refinement_of

    def __eq__(self, other):
        if isinstance(other, CromeType):
            if self.name == other.name and type(self).__name__ == type(other).__name__:
                return True
            return False
        else:
            raise AttributeError

    def __hash__(self):
        return hash(self.name + type(self).__name__)

    def is_similar_to(self, other: CromeType) -> bool:
        if self.name == other.name:
            return True
        for elem in self.refinement_of:
            if isinstance(elem, str):
                if other.name in elem:
                    return True
            else:
                if other.name in elem.name:
                    return True

        return False


AnyCromeType = TypeVar("AnyCromeType", bound=CromeType)
