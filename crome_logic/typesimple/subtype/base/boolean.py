from __future__ import annotations

from crome_logic.typesimple import CromeType


class Boolean(CromeType):
    def __init__(
        self,
        name: str,
        kind: CromeType.Kind = CromeType.Kind.UNKNOWN,
        mutex_group: str = "",
        adjacency: set[str] | None = None,
    ):
        super().__init__(name, kind)
        self._mutex_group: str = mutex_group
        if adjacency is None:
            self._adjacency: set[str] = set()
        else:
            self._adjacency = adjacency

    @property
    def mutex_group(self) -> str:
        return self._mutex_group

    @property
    def adjacency_set(self) -> set[str]:
        return self._adjacency
