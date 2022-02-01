from __future__ import annotations

from crome_logic.crome_types import CTypes


class BoundedInteger(CTypes):
    def __init__(self, name: str, kind: CTypes.Kind, min_value: int, max_value: int):
        self.__min = min_value
        self.__max = max_value
        super().__init__(name, kind)

    @property
    def min(self) -> int:
        return self.__min

    @property
    def max(self) -> int:
        return self.__max
