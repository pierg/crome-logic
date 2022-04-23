from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeVar


@dataclass(kw_only=True)
class CromeType:
    """Base class fo the types of CROME."""

    class Kind(Enum):
        """Kinds of CTypes."""

        UNKNOWN = auto()
        SENSOR = auto()
        LOCATION = auto()
        ACTION = auto()
        ACTIVE = auto()
        CONTEXT = auto()
        SENSOR_LOCATION = auto()
        SENSOR_ACTION = auto()

    name: str
    kind: Kind = Kind.UNKNOWN
    refinement_of: set[str] = field(init=False, default_factory=set)

    def __str__(self):
        return self.name

    def __le__(self, other: CromeType):
        return isinstance(self, type(other))

    def __eq__(self, other):
        if isinstance(other, CromeType):
            if self.name == other.name and type(self).__name__ == type(other).__name__:
                return True
            return False
        else:
            raise AttributeError

    def __hash__(self):
        return hash(self.name + type(self).__name__)

    @property
    def controllable(self) -> bool:
        if (
            self.kind == CromeType.Kind.SENSOR
            or self.kind == CromeType.Kind.CONTEXT
            or self.kind == CromeType.Kind.ACTIVE
        ):
            return False
        return True


AnyCromeType = TypeVar("AnyCromeType", bound=CromeType)
