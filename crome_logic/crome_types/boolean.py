from __future__ import annotations

from crome_logic.crome_types import CTypes


class Boolean(CTypes):
    def __init__(self, name: str, kind: CTypes.Kind):
        super().__init__(name, kind)
        self.__mutex_group: str = ""

    @property
    def mutex_group(self) -> str:
        return self.__mutex_group
