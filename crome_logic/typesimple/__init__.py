from __future__ import annotations

from abc import ABC
from enum import Enum, auto
from typing import TypeVar


class CromeType(ABC):
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

    def __init__(self, name: str, kind: CromeType.Kind):
        self._name: str = name
        self._kind: CromeType.Kind = kind

    def __str__(self):
        return self._name

    def __le__(self, other: CromeType):
        return isinstance(self, type(other))

    def __eq__(self, other):
        if self.name == other.name and type(self).__name__ == type(other).__name__:
            return True
        return False

    def __hash__(self):
        return hash(self.name + type(self).__name__)

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> CromeType.Kind:
        return self._kind

    @property
    def controllable(self) -> bool:
        if (
            self._kind == CromeType.Kind.SENSOR
            or self._kind == CromeType.Kind.CONTEXT
            or self._kind == CromeType.Kind.ACTIVE
        ):
            return False
        return True


AnyCromeType = TypeVar("AnyCromeType", bound=CromeType)
