from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from aenum import Enum, auto, skip

from crome_logic.src.crome_logic.specification.string_logic import and_, or_
from crome_logic.src.crome_logic.typeset import Typeset


class Specification(ABC):
    """Base class representing a specification

    Attributes:
        formula (str): A string representation of the specification in a syntax compatible with spot
        typeset (Typeset)
    """

    _init_formula: str
    _typeset: Typeset | None = None

    @property
    def init_formula(self) -> str:
        if isinstance(self._init_formula, str):
            return self._init_formula
        else:
            raise AttributeError

    @property
    def typeset(self) -> Typeset:
        if isinstance(self._typeset, Typeset):
            return self._typeset
        else:
            raise AttributeError


    @property
    def formula(self) -> str:
        pass

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

    @property
    @abstractmethod
    def cnf(self) -> Cnf:
        pass

    @property
    @abstractmethod
    def dnf(self) -> Dnf:
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
    @abstractmethod
    def is_true_expression(self) -> bool:
        pass

    @abstractmethod
    def __and__(self: Specification, other: Specification) -> Specification:
        pass

    @abstractmethod
    def __or__(self: Specification, other: Specification) -> Specification:
        pass

    @abstractmethod
    def __invert__(self: Specification) -> Specification:
        pass

    @abstractmethod
    def __rshift__(self: Specification, other: Specification) -> Specification:
        pass

    @abstractmethod
    def __iand__(self: Specification, other: Specification) -> Specification:
        pass

    @abstractmethod
    def __ior__(self: Specification, other: Specification) -> Specification:
        pass


@dataclass
class Cnf:
    clauses: list[set[Specification]]

    @property
    def to_str(self) -> str:
        return " & ".join(self.to_str_list)

    @property
    def to_str_list(self) -> list[str]:
        return [or_([str(e) for e in elem]) for elem in self.clauses]

    @property
    def to_set(self) -> set[Specification]:
        and_clauses: set[Specification] = set()
        for or_clause in self.clauses:
            or_clause_list = list(or_clause)
            clause = or_clause_list[0]
            for elem in or_clause_list[1:]:
                clause |= elem
            and_clauses.add(clause)
        return and_clauses

    def __str__(self):
        return self.to_str


@dataclass
class Dnf:
    clauses: list[set[Specification]]

    @property
    def to_str(self) -> str:
        return " | ".join(self.to_str_list)

    @property
    def to_str_list(self) -> list[str]:
        return [and_([str(e) for e in elem], brackets=True) for elem in self.clauses]


    @property
    def to_set(self) -> set[Specification]:
        or_clauses: set[Specification] = set()
        for and_clause in self.clauses:
            and_clause_list = list(and_clause)
            clause = and_clause_list[0]
            for elem in and_clause_list[1:]:
                clause &= elem
            or_clauses.add(clause)
        return or_clauses

    def __str__(self):
        return self.to_str
