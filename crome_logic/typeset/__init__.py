from __future__ import annotations

from copy import copy, deepcopy

from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.typelement import AnyCromeType, TypeKind
from crome_logic.typelement.basic import (
    Boolean,
    BooleanControllable,
    BooleanUncontrollable,
    BoundedInteger,
)
from crome_logic.typelement.robotic import BooleanSensor

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
    """set of identifier -> Boolean."""

    def __init__(self, types: set[AnyCromeType] | None = None):
        """Indicates the supertypes relationships for each typelement in the
        typeset."""
        self._super_types: dict[AnyCromeType, set[AnyCromeType]] = {}
        """Indicates the mutex relationships for the typelement in the typeset"""
        self._mutex_types: set[frozenset[Boolean]] = set()
        """Indicates the adjacency relationships for the typelement in the typeset"""
        self._adjacent_types: dict[Boolean, set[Boolean]] = {}

        if types is not None and len(types) > 0:
            self._add_elements(types)
        else:
            super().__init__()

    @classmethod
    def from_aps(
        cls,
        controllable: set[str] | None = None,
        uncontrollable: set[str] | None = None,
    ) -> Typeset:

        crome_types: set[Boolean] = set()
        if controllable is not None:
            for ap in controllable:
                crome_types.add(BooleanControllable(name=ap))

        if uncontrollable is not None:
            for ap in uncontrollable:
                crome_types.add(BooleanUncontrollable(name=ap))

        return cls(crome_types)  # type: ignore

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

    def __add__(self, element: Typeset | Boolean) -> Typeset:
        """Returns self + element.

        WARNING: violates Liskov Substitution Principle
        """
        if isinstance(element, Boolean):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        new_dict.__iadd__(element)
        return new_dict

    def __sub__(self, element: Typeset | Boolean) -> Typeset:
        """Returns self - element"""
        if isinstance(element, Boolean):
            element = Typeset({element})
        """Shallow copy"""
        new_dict = copy(self)
        for key in element.keys():
            if key in new_dict:
                del new_dict[key]
        return new_dict

    def __iadd__(self, element: Typeset | Boolean):
        """Updates self with self += element."""
        if isinstance(element, Boolean):
            element = Typeset({element})
        for key, value in element.items():
            if key in self:
                if type(value).__name__ != type(self[key]).__name__:
                    print(
                        f"Trying to add an element with key '{key}' and value of typelement '{type(value).__name__}'"
                    )
                    print(
                        f"ERROR:\n"
                        f"There is already en element with key '{key}' and value of typelement '{type(self[key]).__name__}'"
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

        self._update_refinements()
        self._update_mutex()
        self._update_adjacency()

    def _update_refinements(self) -> None:
        """Updates the refinement relationships in the typeset."""
        if len(self.values()) > 1:
            for element in self.values():
                for super_type in element.refinement_of:
                    if super_type in self.keys():
                        if element in self._super_types.keys():
                            self._super_types[element].add(self[super_type])
                        else:
                            self._super_types[element] = {self[super_type]}

    def _update_mutex(self) -> None:
        """Updates the mutually exclusion relationships in the typeset."""
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
        """Updates the adjacency relationships in the typeset."""
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

    def extract_inputs_outputs(
        self, string: bool = False
    ) -> tuple[set[Boolean], set[Boolean]] | tuple[set[str], set[str]]:
        """Returns a set of variables in the typeset that are not controllable
        and controllable."""
        i: set[Boolean] = set()
        i_str: set[str] = set()
        o: set[Boolean] = set()
        o_str: set[str] = set()
        if len(self.values()) > 0:
            for t in self.values():
                if isinstance(t, Boolean):
                    if not t.controllable:
                        if string:
                            i_str.add(t.name)
                        else:
                            i.add(t)
                    else:
                        if string:
                            o_str.add(t.name)
                        else:
                            o.add(t)
        if string:
            return i_str, o_str
        return i, o

    def extract_viewpoint(self):
        for v in self.values():
            if v.kind == TypeKind.LOCATION:
                return "location"
            elif v.kind == TypeKind.ACTION:
                return "action"
        return "other"
