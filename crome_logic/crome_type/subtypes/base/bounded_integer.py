from __future__ import annotations

from crome_logic.crome_type.crome_type import CromeType


class BoundedInteger(CromeType):
    def __init__(self, name: str, kind: CromeType.Kind, min_value: int, max_value: int):
        self.__min = min_value
        self.__max = max_value
        super().__init__(name, kind)

    @property
    def min(self) -> int:
        return self.__min

    @property
    def max(self) -> int:
        return self.__max
