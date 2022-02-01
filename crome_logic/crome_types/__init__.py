from __future__ import annotations

from abc import ABC
from enum import Enum, auto


class CTypes(ABC):
    """Base class fo the types of CROME."""

    class Kind(Enum):
        """Kinds of CTypes."""

        SENSOR = auto()
        LOCATION = auto()
        ACTION = auto()
        ACTIVE = auto()
        CONTEXT = auto()

    def __init__(self, name: str, kind: CTypes.Kind):
        self._name: str = name
        self._kind: CTypes.Kind = kind

    def __str__(self):
        return self._name

    def __le__(self, other: CTypes):
        return isinstance(self, type(other))

    def __eq__(self, other):
        if self.name == other.name and type(self).__name__ == type(other).__name__:
            if isinstance(self, BoundedInteger):
                if (self.min == other.min) and (self.max == other.max):
                    return True
                else:
                    return False
            return True
        return False

    def __hash__(self):
        return hash(self.name + type(self).__name__)

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> CTypes.Kind:
        return self._kind

    @property
    def controllable(self) -> bool:
        if (
            self.kind == CTypes.Kind.SENSOR
            or self.kind == CTypes.Kind.CONTEXT
            or self.kind == CTypes.Kind.ACTIVE
        ):
            return False
        return True


class Boolean(CTypes):
    def __init__(self, name: str, kind: CTypes.Kind):
        super().__init__(name, kind)
        self._mutex_group: str = ""

    @property
    def mutex_group(self) -> str:
        return self._mutex_group


class BoundedInteger(CTypes):
    def __init__(self, name: str, kind: CTypes.Kind, min_value: int, max_value: int):
        self._min = min_value
        self._max = max_value
        super().__init__(name, kind)

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max
