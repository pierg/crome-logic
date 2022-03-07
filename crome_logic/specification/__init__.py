from __future__ import annotations

from abc import ABC, abstractmethod

from aenum import Enum, auto, skip
from treelib import Tree

from crome_logic.typeset import Typeset


class Specification(ABC):
    class Kind(Enum):
        UNDEFINED = auto()

        @skip
        class Atom(Enum):
            ACTION = auto()
            SENSOR = auto()
            LOCATION = auto()
            CONTEXT = auto()
            ACTIVE = auto()

        @skip
        class Rule(Enum):
            REFINEMENT = auto()
            MUTEX = auto()
            ADJACENCY = auto()
            LIVENESS = auto()

    class OutputStr(Enum):
        DEFAULT = auto()
        CNF = auto()
        DNF = auto()
        SUMMARY = auto()

    def __init__(self, formula: str, typeset: Typeset):
        self._formula = formula
        self._typeset = typeset

    def __str__(self: Specification):
        return self.represent()

    @property
    def typeset(self) -> Typeset:
        return self._typeset

    @abstractmethod
    def cnf(self) -> list[set[Specification]]:
        pass

    @abstractmethod
    def dnf(self) -> list[set[Specification]]:
        pass

    @abstractmethod
    def represent(self, output_type: OutputStr = OutputStr.DEFAULT) -> str:
        pass

    @property
    @abstractmethod
    def tree(self) -> Tree:
        pass

    @property
    @abstractmethod
    def is_satisfiable(self: Specification) -> bool:
        pass

    @property
    @abstractmethod
    def is_valid(self: Specification) -> bool:
        pass

    @property
    def is_true(self: Specification) -> bool:
        return self.is_valid

    @property
    def is_false(self: Specification) -> bool:
        return not self.is_satisfiable
