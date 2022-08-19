from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, fields

import spot
from treelib import Tree

from src.crome_logic.patterns import Pattern
from src.crome_logic.specification import Cnf, Dnf, Specification
from src.crome_logic.specification.boolean import Bool
from src.crome_logic.specification.temporal.tools import transform_spot_tree
from src.crome_logic.specification.tools import is_true_string
from src.crome_logic.specification.trees import (
    boolean_tree_to_formula,
    extract_atoms_dictionary,
    gen_atoms_tree,
    gen_ltl_tree,
)
from src.crome_logic.tools.atomic_propositions import extract_ap
from src.crome_logic.tools.nuxmv import check_satisfiability, check_validity
from src.crome_logic.typelement.basic import Boolean, BooleanUncontrollable, BooleanControllable
from src.crome_logic.typelement.robotic import BooleanSensor, BooleanLocation
from src.crome_logic.typeset import Typeset


@dataclass(frozen=True)
class LTL(Specification):
    _init_formula: str | Pattern
    _typeset: Typeset | None = None
    _boolean: Bool | None = None
    _kind: Specification.Kind = Specification.Kind.UNDEFINED
    _expression: spot.formula | None = None
    _tree: Tree | None = None
    _parse_env_systems: bool = False

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
            if self._parse_env_systems:
                set_ap_str_s = list(filter(lambda x: x.startswith('s'), set_ap_str))
                set_ap_str_e = list(filter(lambda x: x.startswith('e'), set_ap_str))
                set_ap_s = set(map(lambda x: BooleanControllable(name=x), set_ap_str_s))
                set_ap_e = set(map(lambda x: BooleanUncontrollable(name=x), set_ap_str_e))
                typeset = Typeset(set_ap_s | set_ap_e)
            else:
                set_ap = set(map(lambda x: Boolean(name=x), set_ap_str))
                typeset = Typeset(set_ap)
        else:
            # typeset = self.typeset.get_sub_typeset(str(self.expression))
            typeset = self._typeset
            # TODO: introduce the world
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

    @property
    def typeset_complete(self) -> Typeset:
        return self.typeset + self.refinement_rules.typeset + self.adjacency_and_mutex_rules.typeset

    def __str__(self):
        return self.formula

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
    def summary(self) -> str:
        cnf_list = "\n".join(self.cnf.to_str_list)
        dnf_list = "\n".join(self.dnf.to_str_list)
        ret = (
            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
            f"LTL SIMPLIFIED\n"
            f"{str(self)}\n\n"
            f"BOOLEAN REPRESENTATION\n"
            f"{str(self.boolean)}\n\n"
            f"LTL CNF (from booleans)\n"
            f"{self.cnf.to_str}\n"
            f"LTL CNF (list)\n"
            f"{cnf_list}\n\n"
            f"LTL DNF (from booleans)\n"
            f"{self.dnf.to_str}\n"
            f"LTL DNF (list)\n"
            f"{dnf_list}\n"
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
    def adjacency_and_mutex_rules(self) -> LTL:
        return self.adjacency_rules & self.mutex_rules

    @property
    def adjacency_rules(self) -> LTL:
        from src.crome_logic.specification.rules_extractors import (
            extract_adjacency_rules
        )

        return extract_adjacency_rules(self.typeset)

    @property
    def mutex_rules(self) -> LTL:
        from src.crome_logic.specification.rules_extractors import (
            extract_mutex_rules
        )

        return extract_mutex_rules(self.typeset)

    @property
    def refinement_rules(self) -> LTL:
        from src.crome_logic.specification.rules_extractors import (
            extract_refinement_rules
        )

        return extract_refinement_rules(self.typeset)

    @property
    def is_satisfiable(self: LTL) -> bool:
        # print("CHECKSATNOW")
        # print(self)
        #
        # adj = self.adjacency_rules
        # print(adj)
        #
        # mtx = self.mutex_rules
        # # print(mtx)

        new_f = self & self.adjacency_and_mutex_rules
        # print(new_f)

        return check_satisfiability(str(new_f), new_f.typeset.to_str_nuxmv())

    @property
    def is_valid(self: LTL) -> bool:

        if isinstance(self.kind, LTL.Kind.Rule):
            return check_validity(str(self), self.typeset.to_str_nuxmv())

        # print(f"EXT:\n{self.refinement_rules}")
        # print(f"ADJ:\n{self.adjacency_rules}")
        # print(f"MTX:\n{self.mutex_rules}")
        # print(f"VAL:\n{self}")
        #
        # new_f = (self.refinement_rules & self.adjacency_and_mutex_rules) >> self

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

        # print(f"REFCHECK\n{str(self)}\n{str(other)}")
        if not self.is_satisfiable:
            return False
        if not other.is_satisfiable:
            return False

        s = self
        s_r = self.refinement_rules
        s_a = self.adjacency_rules
        s_m = self.mutex_rules
        o = other
        o_r = other.refinement_rules
        o_a = other.adjacency_rules
        o_m = other.mutex_rules
        #
        # print(f"sPHI:\n{s}")
        # print(f"sEXT:\n{s_r}")
        # print(f"sADJ:\n{s_a}")
        # print(f"sMTX:\n{s_m}")
        # print(f"oPHI:\n{o}")
        # print(f"oEXT:\n{o_r}")
        # print(f"oADJ:\n{o_a}")
        # print(f"oMTX:\n{o_m}")

        # new_f = (s_r & s_a & s_m & s) >> o
        # new_f = (s_r & s_a & s_m & s) >> (o_r & o_a & o_m & o)
        # new_f = (s_r & s_a & s_m & o_m & o_a & o_r) >> s >> o

        # new_f = (s_r & s_a & s_m & o_m & o_a & o_r & s) >> o
        # new_f = (s_r & s_a & s_m & o_m & o_a & s) >> o
        new_f = (s_r & s_a & s_m & s) >> o



        # new_f = (s_r & s_a & s_m & o_m & o_a & o_r & s) >> o
        # new_f = (s_r & s_a & s_m & s) >> o
        # new_f = (s_r & s_a & s_m & s) >> o

        # new_f = s_r >> s >> o
        # new_f = (((s_r & s_m) & (o_r & o_m) & s) >> o)

        # new_f = ((s_r & s_m & s) >> o)
        #
        # new_f = (((s_r & s_m) >> s) >> ((s_r & s_m) >> o))

        # new_f = (self.refinement_rules & self.adjacency_and_mutex_rules) >> other

        return new_f.is_valid

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
