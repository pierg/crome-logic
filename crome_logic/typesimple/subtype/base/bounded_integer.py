from __future__ import annotations

from crome_logic.typesimple import CromeType


class BoundedInteger(CromeType):
    def __init__(self, name: str, kind: CromeType.Kind, min_value: int, max_value: int):
        self._min = min_value
        self._max = max_value
        super().__init__(name, kind)

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int:
        return self._max

    def __eq__(self, other):
        if self.name == other.name and type(self).__name__ == type(other).__name__:
            if self.min == other.min and self.max == other.max:
                return True
        return False
