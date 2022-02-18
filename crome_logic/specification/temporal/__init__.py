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
from crome_logic.tools.ap import extract_ap
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
        kind: Specification.Kind = Specification.Kind.UNDEFINED,
    ):
        """We can build an LTL from scratch (str) or from an existing Bool."""

        self._kind = kind

        self._init__ltl_formula(formula, typeset)
        self._init__atoms_formula(boolean_formula)

        super().__init__(str(self._ltl_formula), self._typeset)

    def _init__ltl_formula(self, formula: str, typeset: Typeset | None):
        """Building the LTL formula and tree."""

        self._ltl_formula = transform_spot_tree(spot.formula(formula))

        if typeset is None:
            set_ap_str = extract_ap(self._ltl_formula)
            set_ap = set(map(lambda x: Boolean(x), set_ap_str))
            self._typeset = Typeset(set_ap)
        else:
            self._typeset = typeset.get_sub_typeset(str(self._ltl_formula))

        self._tree: Tree = gen_ltl_tree(spot_f=self._ltl_formula)

    def _init__atoms_formula(self, boolean_formula: Bool | None) -> None:
        """Building the ATOMS formula and tree."""
        if boolean_formula is None:
            atom_tree = gen_atoms_tree(spot_f=self._ltl_formula)
            self._boolean_formula = Bool(
                boolean_tree_to_formula(atom_tree), tree=atom_tree
            )
        else:
            self._boolean_formula = boolean_formula

    def cnf(self) -> list[set[LTL]]:  # type: ignore
        atoms_cnf = self._boolean_formula.cnf()
        cnf_list = []
        atoms_dictionary = extract_atoms_dictionary(self._boolean_formula.tree)
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
        atoms_dnf = self._boolean_formula.dnf()
        dnf_list = []
        atoms_dictionary = extract_atoms_dictionary(self._boolean_formula.tree)
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
        self, output_type: Specification.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        if output_type == Specification.OutputStr.DEFAULT:
            return str(self._ltl_formula)
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
                f"{str(self._ltl_formula)}\n\n"
                f"BOOLEAN REPRESENTATION\n"
                f"{str(self._boolean_formula)}\n\n"
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
        return self._boolean_formula

    def __and__(self: Specification, other: Specification) -> LTL:
        """self & other Returns a new LTL with the conjunction with
        other."""

    def __or__(self: Specification, other: Specification) -> LTL:
        """self | other Returns a new LTL with the disjunction with
        other."""

    def __invert__(self: Specification) -> LTL:
        """Returns a new LTL with the negation of self."""

    def __rshift__(self: Specification, other: Specification) -> LTL:
        """>> Returns a new LTL that is the result of self -> other
        (implies)"""

    def __iand__(self: Specification, other: Specification) -> LTL:
        """self &= other Modifies self with the conjunction with other."""

    def __ior__(self: Specification, other: Specification) -> LTL:
        """self |= other Modifies self with the disjunction with other."""

    @property
    def is_satisfiable(self: Specification) -> bool:
        pass

    @property
    def is_valid(self: Specification) -> bool:
        pass
