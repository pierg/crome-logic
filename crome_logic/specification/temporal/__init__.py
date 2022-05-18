from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, fields

import spot
from treelib import Tree

from crome_logic.patterns import Pattern
from crome_logic.specification import Cnf, Dnf, Specification
from crome_logic.specification.boolean import Bool
from crome_logic.specification.temporal.tools import transform_spot_tree
from crome_logic.specification.tools import is_true_string
from crome_logic.specification.trees import (
    boolean_tree_to_formula,
    extract_atoms_dictionary,
    gen_atoms_tree,
    gen_ltl_tree,
)
from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.tools.nuxmv import check_satisfiability, check_validity
from crome_logic.typelement.basic import Boolean
from crome_logic.typelement.robotic import BooleanSensor, BooleanLocation
from crome_logic.typeset import Typeset


@dataclass(frozen=True)
class LTL(Specification):
    _init_formula: str | Pattern
    _typeset: Typeset | None = None
    _boolean: Bool | None = None
    _kind: Specification.Kind = Specification.Kind.UNDEFINED
    _expression: spot.formula | None = None
    _tree: Tree | None = None

    @property
    def boolean(self) -> Bool:
        if isinstance(self._boolean, Bool):
            return self._boolean
        raise AttributeError

    @property
    def kind(self) -> Specification.Kind:
        return self._kind

    @property
    def expression(self) -> spot.formula:
        return self._expression

    @property
    def tree(self) -> Tree:
        return self._tree

    def __post_init__(self):
        if isinstance(self._init_formula, Pattern):
            object.__setattr__(self, "_init_formula", str(self._init_formula))
        self._initialize_external_libraries_objects(self._init_formula)

        if self._typeset is None:
            set_ap_str = extract_ap(self.expression)
            set_ap = set(map(lambda x: Boolean(name=x), set_ap_str))
            typeset = Typeset(set_ap)
        else:
            typeset = self.typeset.get_sub_typeset(str(self.expression))
        object.__setattr__(self, "_typeset", typeset)

    def _initialize_external_libraries_objects(self, formula: str):
        expression = transform_spot_tree(spot.formula(formula))
        object.__setattr__(self, "_expression", expression)
        if self._boolean is None:
            atom_tree = gen_atoms_tree(spot_f=self.expression)
            boolean = Bool(
                _init_formula=boolean_tree_to_formula(atom_tree), _tree=atom_tree
            )
            object.__setattr__(self, "_boolean", boolean)
        tree: Tree = gen_ltl_tree(spot_f=self.expression)
        object.__setattr__(self, "_tree", tree)

    @classmethod
    def from_pattern(cls, formula: Pattern, typeset: Typeset | None = None) -> LTL:
        return cls(_init_formula=str(formula), _typeset=typeset)

    def __hash__(self: LTL):
        return hash(str(self))

    @property
    def formula(self) -> str:
        return str(self.expression)

    def __str__(self):
        return self.formula

    def export_to_json(self):
        json_content = {}
        if self.formula == "1":
            json_content = {"ltl_value": "true",
                            "world_values": [[], [], []]}
        else:
            sensor = []
            location = []
            action = []
            typeset = self.typeset
            for keyType in typeset:
                if type(typeset[keyType]) == BooleanSensor:
                    sensor.append(keyType)
                elif type(typeset[keyType]) == BooleanLocation:
                    location.append(keyType)
                else:
                    action.append(keyType)
            json_content = {"ltl_value": self.formula,
                            "world_values": [sensor, action, location]}
        return json_content

    def __deepcopy__(self: LTL, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        for field in fields(cls):
            if not (
                    field.name == "_boolean"
                    or field.name == "_expression"
                    or field.name == "_tree"
            ):
                object.__setattr__(
                    result, field.name, deepcopy(getattr(self, field.name))
                )
        result._initialize_external_libraries_objects(result.init_formula)
        return result

    @property
    def print_summary(self) -> str:
        ret = (
            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
            f"LTL SIMPLIFIED\n"
            f"{str(self)}\n\n"
            f"BOOLEAN REPRESENTATION\n"
            f"{str(self.boolean)}\n\n"
            f"LTL CNF (from booleans)\n"
            f"{self.cnf.to_str}\n\n"
            f"LTL DNF (from booleans)\n"
            f"{self.dnf.to_str}\n"
            f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n"
        )
        return ret

    @property
    def cnf(self) -> Cnf:
        atoms_cnf = self.boolean.cnf.clauses
        cnf_list = []
        atoms_dictionary = extract_atoms_dictionary(self.boolean.tree)
        for clauses in atoms_cnf:
            atoms = set()
            for atom in clauses:
                atom_str: str = str(atom)
                if atom_str.startswith("!"):
                    ltl_formula = f"!{atoms_dictionary[atom_str[1:]]}"
                else:
                    ltl_formula = atoms_dictionary[str(atom)]
                ltl_object = LTL(
                    _init_formula=ltl_formula,
                    _typeset=self.typeset.get_sub_typeset(ltl_formula),
                )
                atoms.add(ltl_object)
            cnf_list.append(atoms)
        return Cnf(cnf_list)  # type: ignore

    @property
    def dnf(self) -> Dnf:
        atoms_dnf = self.boolean.dnf.clauses
        dnf_list = []
        atoms_dictionary = extract_atoms_dictionary(self.boolean.tree)
        for clauses in atoms_dnf:
            atoms = set()
            for atom in clauses:
                atom_str: str = str(atom)
                if atom_str.startswith("!"):
                    ltl_formula = f"!{atoms_dictionary[atom_str[1:]]}"
                else:
                    ltl_formula = atoms_dictionary[str(atom)]
                ltl_object = LTL(
                    _init_formula=ltl_formula,
                    _typeset=self.typeset.get_sub_typeset(ltl_formula),
                )
                atoms.add(ltl_object)
            dnf_list.append(atoms)
        return Dnf(dnf_list)  # type: ignore

    def __iand__(self: Specification, other: Specification) -> LTL:
        """self &= other Modifies self with the conjunction with other."""
        if not (isinstance(self, LTL) and isinstance(other, LTL)):
            raise AttributeError
        if self.is_true_expression:
            init_formula = deepcopy(other.formula)
            typeset = deepcopy(other.typeset)
            boolean = deepcopy(other.boolean)
            object.__setattr__(self, "_init_formula", init_formula)
            object.__setattr__(self, "_typeset", typeset)
            object.__setattr__(self, "_boolean", boolean)

            self.__post_init__()  # type: ignore

            return self

        if other.is_true_expression:
            return self

        init_formula = f"({str(self)}) & ({str(other)})"
        typeset = self.typeset + other.typeset
        boolean = self.boolean & other.boolean

        object.__setattr__(self, "_init_formula", init_formula)
        object.__setattr__(self, "_typeset", typeset)
        object.__setattr__(self, "_boolean", boolean)

        self.__post_init__()  # type: ignore

        return self

    def __ior__(self: Specification, other: Specification) -> LTL:
        """self |= other Modifies self with the disjunction with other."""
        if not (isinstance(self, LTL) and isinstance(other, LTL)):
            raise AttributeError
        if self.is_true_expression or other.is_true_expression:
            init_formula = f"TRUE"
        else:
            init_formula = f"({str(self)}) | ({str(other)})"

        typeset = self.typeset + other.typeset
        boolean = self.boolean | other.boolean
        object.__setattr__(self, "_init_formula", init_formula)
        object.__setattr__(self, "_typeset", typeset)
        object.__setattr__(self, "_boolean", boolean)

        self.__post_init__()  # type: ignore

        return self

    def __and__(self: Specification, other: Specification) -> LTL:
        """self & other Returns a new LTL with the conjunction with other."""
        if not (isinstance(self, LTL) and isinstance(other, LTL)):
            raise AttributeError
        if self.is_true_expression:
            return LTL(
                _init_formula=str(other),
                _boolean=other.boolean,
                _typeset=other.typeset,
            )

        if other.is_true_expression:
            return LTL(
                _init_formula=str(self),
                _boolean=self.boolean,
                _typeset=self.typeset,
            )

        return LTL(
            _init_formula=f"({str(self)}) & ({str(other)})",
            _boolean=self.boolean & other.boolean,
            _typeset=self.typeset + other.typeset,
        )

    def __or__(self: Specification, other: Specification) -> LTL:
        """self | other Returns a new LTL with the disjunction with other."""
        if not (isinstance(self, LTL) and isinstance(other, LTL)):
            raise AttributeError
        if self.is_true_expression or other.is_true_expression:
            return LTL("TRUE")

        return LTL(
            _init_formula=f"({str(self)}) | ({str(other)})",
            _boolean=self.boolean | other.boolean,
            _typeset=self.typeset + other.typeset,
        )

    def __invert__(self: Specification) -> LTL:
        """Returns a new LTL with the negation of self."""
        if not isinstance(self, LTL):
            raise AttributeError
        return LTL(
            _init_formula=f"!({self.expression})",
            _boolean=~self.boolean,
            _typeset=self.typeset,
        )

    def __rshift__(self: Specification, other: Specification) -> LTL:
        """>> Returns a new LTL that is the result of self -> other
        (implies)"""
        if not (isinstance(self, LTL) and isinstance(other, LTL)):
            raise AttributeError
        if self.is_true_expression:
            return LTL(
                _init_formula=str(other),
                _boolean=other.boolean,
                _typeset=other.typeset,
            )

        return LTL(
            _init_formula=f"({self.expression}) -> ({other.expression})",
            _boolean=self.boolean >> other.boolean,
            _typeset=self.typeset + other.typeset,
        )

    @property
    def is_satisfiable(self: LTL) -> bool:
        from crome_logic.specification.rules_extractors import (
            extract_adjacency_rules,
            extract_mutex_rules,
            extract_refinement_rules,
        )

        mtx_rules = extract_mutex_rules(self.typeset)
        new_f = self

        if isinstance(mtx_rules, LTL):
            new_f = self & mtx_rules

        adj_rules = extract_adjacency_rules(self.typeset)
        if isinstance(adj_rules, LTL):
            new_f = new_f & adj_rules

        # ref_rules = extract_refinement_rules(self.typeset)
        # if isinstance(ref_rules, LTL):
        #     new_f = ref_rules >> new_f

        return check_satisfiability(str(new_f), new_f.typeset.to_str_nuxmv())

    @property
    def is_valid(self: LTL) -> bool:
        from crome_logic.specification.rules_extractors import extract_refinement_rules

        if isinstance(self.kind, LTL.Kind.Rule):
            return check_validity(str(self), self.typeset.to_str_nuxmv())

        ref_rules = extract_refinement_rules(self.typeset)

        if isinstance(ref_rules, LTL):
            new_f = ref_rules >> self
        else:
            new_f = self

        return check_validity(str(new_f), new_f.typeset.to_str_nuxmv())

    @property
    def is_true_expression(self) -> bool:
        if is_true_string(str(self)):
            return True

    def __lt__(self, other: LTL):
        """self < other.

        True if self is a refinement but not equal to other
        """
        return self.__le__(other) and self.__ne__(other)

    def __le__(self: LTL, other: LTL):
        """self <= other.

        True if self is a refinement of other
        """
        """Check if (self -> other) is valid"""
        return (self >> other).is_valid

    def __gt__(self, other: LTL):
        """self > other.

        True if self is an abstraction but not equal to other
        """
        return self.__ge__(other) and self.__ne__(other)

    def __ge__(self, other: LTL):
        """self >= other.

        True if self is an abstraction of other
        """
        """Check if (other -> self) is valid"""
        return (other >> self).is_valid

    def __eq__(self, other: object):
        """Check if self == other."""
        if not isinstance(other, LTL):
            return NotImplemented
        if str(self) == str(other):
            return True
        else:
            not_self = ~self
            if str(not_self) == str(other):
                return False
            return self.__le__(other) and self.__ge__(other)

    def __ne__(self, other: object):
        """Check if self != other."""
        if not isinstance(other, LTL):
            return NotImplemented
        return not self.__eq__(other)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_tree"]
        state["_expression"] = str(self.expression)
        state["_boolean"] = str(self.boolean)
        state["_boolean_typeset"] = self.boolean.typeset

        return state

    def __setstate__(self, state):
        expression = state["_expression"]
        boolean = state["_boolean"]
        boolean_typeset = state["_boolean_typeset"]
        del state["_expression"]
        del state["_boolean"]
        del state["_boolean_typeset"]
        self.__dict__.update(state)
        init_formula = expression
        boolean = Bool(_init_formula=boolean, _typeset=boolean_typeset)
        object.__setattr__(self, "_init_formula", init_formula)
        object.__setattr__(self, "_boolean", boolean)
        self.__post_init__()  # type: ignore


if __name__ == '__main__':
    tre = LTL("TRUE")
    print(tre)
