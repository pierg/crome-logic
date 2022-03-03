from __future__ import annotations

from enum import Enum, auto

import spot
from treelib import Tree

from crome_logic.specification import Specification
from crome_logic.specification.boolean import Bool
from crome_logic.specification.string_logic import and_, or_
from crome_logic.specification.temporal.tools import transform_spot_tree
from crome_logic.specification.trees import (
    boolean_tree_to_formula,
    extract_atoms_dictionary,
    gen_atoms_tree,
    gen_ltl_tree,
)
from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.tools.nuxmv import check_satisfiability, check_validity
from crome_logic.typeset import Typeset
from crome_logic.typesimple.subtype.base.boolean import Boolean


class LTL(Specification):
    class TreeType(Enum):
        LTL = auto()
        BOOLEAN = auto()

    def __init__(
        self,
        formula: str,
        typeset: Typeset | None = None,
        boolean_formula: Bool | None = None,
        kind: LTL.Kind = Specification.Kind.UNDEFINED,
    ):
        """We can build an LTL from scratch (str) or from an existing Bool."""

        self._kind = kind

        self._init_ltl_formula(formula, typeset)
        self._init_atoms_formula(boolean_formula)

        super().__init__(str(self.expression), self.typeset)

    def __hash__(self: LTL):
        return hash(str(self))

    def _init_ltl_formula(self, formula: str, typeset: Typeset | None):
        """Building the LTL formula and tree."""

        self._ltl_formula = transform_spot_tree(spot.formula(formula))

        if typeset is None:
            set_ap_str = extract_ap(self.expression)
            set_ap = set(map(lambda x: Boolean(x), set_ap_str))
            self._typeset = Typeset(set_ap)
        else:
            self._typeset = typeset.get_sub_typeset(str(self.expression))

        self._tree: Tree = gen_ltl_tree(spot_f=self.expression)

    def _init_atoms_formula(self, boolean_formula: Bool | None) -> None:
        """Building the ATOMS formula and tree."""
        if boolean_formula is None:
            atom_tree = gen_atoms_tree(spot_f=self.expression)
            self._boolean = Bool(boolean_tree_to_formula(atom_tree), tree=atom_tree)
        else:
            self._boolean = boolean_formula

    def cnf(self) -> list[set[LTL]]:  # type: ignore
        atoms_cnf = self.boolean.cnf()
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
                    ltl_formula, typeset=self.typeset.get_sub_typeset(ltl_formula)
                )
                atoms.add(ltl_object)
            cnf_list.append(atoms)
        return cnf_list

    def dnf(self) -> list[set[LTL]]:  # type: ignore
        atoms_dnf = self.boolean.dnf()
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
                    ltl_formula, typeset=self.typeset.get_sub_typeset(ltl_formula)
                )
                atoms.add(ltl_object)
            dnf_list.append(atoms)
        return dnf_list

    def represent(
        self, output_type: LTL.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        if output_type == Specification.OutputStr.DEFAULT:
            return str(self.expression)
        elif output_type == Specification.OutputStr.CNF:
            return " & ".join([or_([str(e) for e in elem]) for elem in self.cnf()])
        elif output_type == Specification.OutputStr.DNF:
            return " | ".join(
                [and_([str(e) for e in elem], brackets=True) for elem in self.dnf()]
            )
        elif output_type == Specification.OutputStr.SUMMARY:
            cnf = "\n".join([or_([str(e) for e in elem]) for elem in self.cnf()])
            dnf = "\n".join([and_([str(e) for e in elem]) for elem in self.dnf()])
            ret = (
                f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                f"LTL SIMPLIFIED\n"
                f"{str(self.expression)}\n\n"
                f"BOOLEAN REPRESENTATION\n"
                f"{str(self.boolean)}\n\n"
                f"LTL CNF (from booleans)\n"
                f"{cnf}\n\n"
                f"LTL DNF (from booleans)\n"
                f"{dnf}\n"
                f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n"
            )
            return ret
        else:
            raise NotImplementedError

    @property
    def tree(self) -> Tree:
        return self._tree

    @property
    def boolean(self) -> Bool:
        return self._boolean

    @property
    def expression(self) -> spot.formula:
        return self._ltl_formula

    def __iand__(self: LTL, other: LTL) -> LTL:
        """self &= other Modifies self with the conjunction with other."""
        self._init_ltl_formula(
            formula=f"({str(self)}) & ({str(other)})",
            typeset=self.typeset + other.typeset,
        )
        self._init_atoms_formula(
            boolean_formula=self.boolean & other.boolean,
        )
        return self

    def __ior__(self: LTL, other: LTL) -> LTL:
        """self |= other Modifies self with the disjunction with other."""
        self._init_ltl_formula(
            formula=f"({str(self)}) | ({str(other)})",
            typeset=self.typeset + other.typeset,
        )
        self._init_atoms_formula(
            boolean_formula=self.boolean | other.boolean,
        )
        return self

    def __and__(self: LTL, other: LTL) -> LTL:
        """self & other Returns a new LTL with the conjunction with
        other."""

        boolean_formula = self.boolean & other.boolean

        return LTL(
            formula=f"({str(self)}) & ({str(other)})",
            boolean_formula=boolean_formula,
            typeset=self.typeset + other.typeset,
        )

    def __or__(self: LTL, other: LTL) -> LTL:
        """self | other Returns a new LTL with the disjunction with
        other."""
        boolean_formula = self.boolean | other.boolean

        return LTL(
            formula=f"({str(self)}) | ({str(other)})",
            boolean_formula=boolean_formula,
            typeset=self.typeset + other.typeset,
        )

    def __invert__(self: LTL) -> LTL:
        """Returns a new LTL with the negation of self."""

        return LTL(
            formula=f"!({self.expression})",
            boolean_formula=~self.boolean,
            typeset=self.typeset,
        )

    def __rshift__(self: LTL, other: LTL) -> LTL:
        """>> Returns a new LTL that is the result of self -> other
        (implies)"""

        return LTL(
            formula=f"({self.expression}) -> ({other.expression})",
            boolean_formula=self.boolean >> other.boolean,
            typeset=self.typeset + other.typeset,
        )

    @property
    def is_satisfiable(self: LTL) -> bool:
        from crome_logic.specification.temporal.rules_extractors import (
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

        ref_rules = extract_refinement_rules(self.typeset)
        if isinstance(ref_rules, LTL):
            new_f = ref_rules >> new_f

        return check_satisfiability(str(new_f), new_f.typeset.to_str_nuxmv())

    @property
    def is_valid(self: LTL) -> bool:
        from crome_logic.specification.temporal.rules_extractors import (
            extract_refinement_rules,
        )

        ref_rules = extract_refinement_rules(self.typeset)

        if isinstance(ref_rules, LTL):
            new_f = ref_rules >> self
        else:
            new_f = self

        return check_validity(str(new_f), new_f.typeset.to_str_nuxmv())

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
        """Check if self == other"""
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
        """Check if self != other"""
        if not isinstance(other, LTL):
            return NotImplemented
        return not self.__eq__(other)
