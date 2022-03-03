from __future__ import annotations

from copy import copy, deepcopy
from itertools import combinations

from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.typesimple import AnyCromeType, CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean
from crome_logic.typesimple.subtype.base.bounded_integer import BoundedInteger

BASE_CLASS_TYPES = [
    "Boolean",
    "BoundedInteger",
    "BooleanAction",
    "IntegerAction",
    "Active",
    "ContextTime",
    "ContextBooleanTime",
    "ContextLocation",
    "ContextIdentity",
    "ReachLocation",
    "IntegerSensor",
    "BooleanSensor",
]


class Typeset(dict[str, AnyCromeType]):
    """set of identifier -> CromeType."""

    def __init__(self, types: set[AnyCromeType] | None = None):
        """Indicates the supertypes relationships for each crometypes in the
        typeset."""
        self._super_types: dict[AnyCromeType, set[AnyCromeType]] = {}
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

    def __add__(self, element: Typeset | AnyCromeType) -> Typeset:
        """Returns self + element.
        WARNING: violates Liskov Substitution Principle"""
        if isinstance(element, CromeType):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        new_dict.__iadd__(element)
        return new_dict

    def __sub__(self, element: Typeset | AnyCromeType) -> Typeset:
        """Returns self - element"""
        if isinstance(element, CromeType):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        for key in element.keys():  # type: ignore
            if key in new_dict:
                del new_dict[key]
        return new_dict

    def __iadd__(self, element: Typeset | AnyCromeType):
        """Updates self with self += element."""
        if isinstance(element, CromeType):
            element = Typeset({element})
        for key, value in element.items():  # type: ignore
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

    def to_str_nuxmv(self) -> list[str]:
        tuple_vars = []
        for k, v in self.items():
            if isinstance(v, Boolean):
                tuple_vars.append(f"{k}: boolean")
            elif isinstance(v, BoundedInteger):
                tuple_vars.append(f"{k}: {v.min}..{v.max}")
        return tuple_vars

    def get_sub_typeset(self, formula: str):
        set_ap_str = extract_ap(formula)
        set_of_types = set(filter((lambda x: x.name in set_ap_str), self.values()))
        return Typeset(set_of_types)

    def _add_elements(self, types: set[AnyCromeType]):
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
                if (
                    a.__class__.__name__ in BASE_CLASS_TYPES
                    or b.__class__.__name__ in BASE_CLASS_TYPES
                ):
                    continue
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
    def super_types(self) -> dict[AnyCromeType, set[AnyCromeType]]:
        return self._super_types

    @property
    def mutex_types(self) -> set[frozenset[Boolean]]:
        return self._mutex_types

    @property
    def adjacent_types(self) -> dict[Boolean, set[Boolean]]:
        return self._adjacent_types

    def extract_inputs_outputs(self) -> tuple[set[AnyCromeType], set[AnyCromeType]]:
        """Returns a set of variables in the typeset that are not controllable
        and controllable."""
        i = set()
        o = set()
        if len(self.values()) > 0:
            for t in self.values():
                if not t.controllable:
                    i.add(t)
                else:
                    o.add(t)
        return i, o
