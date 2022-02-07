from __future__ import annotations

from copy import copy, deepcopy
from itertools import combinations

from crome_logic.crome_type.crome_type import CromeType
from crome_logic.crome_type.subtype.base.boolean import Boolean


class Typeset(dict[str, CromeType]):
    """set of identifier -> CromeType."""

    def __init__(self, types: set[CromeType] | None = None):
        """Indicates the supertypes relationships for each crometypes in the
        typeset."""
        self._super_types: dict[CromeType, set[CromeType]] = {}
        """Indicates the mutex relationships for the crometypes in the typeset"""
        self._mutex_types: set[frozenset[Boolean]] = set()
        """Indicates the adjacency relationships for the crometypes in the typeset"""
        self._adjacent_types: dict[Boolean, set[Boolean]] = {}

        if types is not None:
            self._add_elements(types)
        else:
            super().__init__()

    def __setitem__(self, name, elem):
        self._add_elements({elem})

    def __deepcopy__(self: Typeset, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v))
        """Do not perform a deepcopy of the variables"""
        for k, v in self.items():
            result[k] = v
        return result

    def __str__(self):
        ret = ""
        for (key, elem) in self.items():
            ret += f"{key}:\t{elem.name}"
            if elem in self.super_types:
                ret += " -> "
                for supertypes in self.super_types[elem]:
                    ret += supertypes.name
            ret += "\n"
        return ret[:-1]

    def __add__(self, element: Typeset | CromeType) -> Typeset:
        """Returns self + element.
        WARNING: violates Liskov Substitution Principle"""
        if isinstance(element, CromeType):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        new_dict.__iadd__(element)
        return new_dict

    def __sub__(self, element: Typeset | CromeType) -> Typeset:
        """Returns self - element"""
        if isinstance(element, CromeType):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        for key in element.keys():
            if key in new_dict:
                del new_dict[key]
        return new_dict

    def __iadd__(self, element: Typeset | CromeType):
        """Updates self with self += element."""
        if isinstance(element, CromeType):
            element = Typeset({element})
        for key, value in element.items():
            if key in self:
                if type(value).__name__ != type(self[key]).__name__:
                    print(
                        f"Trying to add an element with key '{key}' and value of crometypes '{type(value).__name__}'"
                    )
                    print(
                        f"ERROR:\n"
                        f"There is already en element with key '{key}' and value of crometypes '{type(self[key]).__name__}'"
                    )
                    raise Exception("Type Mismatch")
            if key not in self:
                self._add_elements({value})
        return self

    @property
    def size(self) -> int:
        return len(list(self.keys()))

    def _add_elements(self, types: set[CromeType]):
        if types is not None:
            for elem in types:
                super().__setitem__(elem.name, elem)

        self._update_extensions()
        self._update_mutex()
        self._update_adjacency()

    def _update_extensions(self) -> None:
        """Updates the extension relationships in the typeset"""
        if len(self.values()) > 1:
            for (a, b) in combinations(self.values(), 2):
                """If they are not base variables"""
                if isinstance(a, type(b)):
                    if a in self._super_types:
                        self._super_types[a].add(b)
                    else:
                        self._super_types[a] = {b}
                if isinstance(b, type(a)):
                    if b in self._super_types:
                        self._super_types[b].add(a)
                    else:
                        self._super_types[b] = {a}

    def _update_mutex(self) -> None:
        """Updates the mutually exclusion relationships in the typeset"""
        if len(self.values()) > 1:
            self._mutex_types = set()
            mutex_vars_dict: dict[str, set[Boolean]] = {}
            for variable in self.values():
                if isinstance(variable, Boolean):
                    if variable.mutex_group != "":
                        if variable.mutex_group in mutex_vars_dict:
                            mutex_vars_dict[variable.mutex_group].add(variable)
                        else:
                            mutex_vars_dict[variable.mutex_group] = set()
                            mutex_vars_dict[variable.mutex_group].add(variable)
            for vars in mutex_vars_dict.values():
                self._mutex_types.add(frozenset(vars))

    def _update_adjacency(self) -> None:
        """Updates the adjacency relationships in the typeset"""
        if len(self.values()) > 1:
            self._adjacent_types = {}
            for variable in self.values():
                if isinstance(variable, Boolean):
                    """Adding 'self' as adjacent as well i.e. the robot can
                    stay still."""
                    if len(list(variable.adjacency_set)) != 0:
                        self._adjacent_types[variable] = {variable}
                    for adjacent_class in variable.adjacency_set:
                        for variable_candidate in filter(
                            lambda x: isinstance(x, Boolean), self.values()
                        ):
                            if (
                                variable_candidate.__class__.__name__ == adjacent_class
                                and isinstance(variable_candidate, Boolean)
                            ):
                                self._adjacent_types[variable].add(variable_candidate)

    @property
    def super_types(self) -> dict[CromeType, set[CromeType]]:
        return self._super_types

    @property
    def mutex_types(self) -> set[frozenset[Boolean]]:
        return self._mutex_types

    @property
    def adjacent_types(self) -> dict[Boolean, set[Boolean]]:
        return self._adjacent_types