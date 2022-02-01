from __future__ import annotations

import hashlib
from copy import deepcopy
from enum import Enum, auto

from treelib import Tree

import spot

from crome_logic.crome_type.subtype.base.boolean import Boolean
from crome_logic.specification.boolean.boolean import Bool
from crome_logic.specification.specification import Specification
from crome_logic.specification.temporal.tools import transform_spot_tree, extract_ap
from crome_logic.specification.temporal.trees import gen_ltl_tree
from crome_logic.typeset.typeset import Typeset


class LTL(Specification):
    class TreeType(Enum):
        LTL = auto()
        BOOLEAN = auto()

    def __init__(
        self,
        formula: str,
        typeset: Typeset | None = None,
        boolean_formula: Bool | None = None,
        atoms_dictionary: dict[str, LTL] | None = None,
        kind: Specification.Kind = None,
        atom_hash: str = None,
    ):
        """We can build a Sformula from scratch (str, or Pattern) or from an existing Pyeda."""

        self.__simplified_formula_spot = None
        self.__kind = kind
        self._ltl_tree = None
        self.__atoms_tree = None
        self.__atoms_dictionary = None
        self.__atom_hash = atom_hash
        self.__boolean_formula = None

        if kind is None:
            self.__kind = Specification.Kind.UNDEFINED

        self.__init__ltl_formula(formula, typeset)
        self.__init__atoms_formula(boolean_formula, atoms_dictionary)

        super().__init__(str(self._spot), self._typeset)

    def __init__ltl_formula(self, formula: str, typeset: Typeset | None):
        """Building the LTL formula and tree."""

        self._spot = transform_spot_tree(spot.formula(formula))

        if typeset is None:
            set_ap_str = extract_ap(self._spot)
            set_ap = set(map(lambda x: Boolean(x), set_ap_str))
            self._typeset = Typeset(set_ap)
        else:
            set_ap_str = extract_ap(self.__simplified_formula_spot)
            set_of_types = set(
                filter((lambda x: x.name in set_ap_str), typeset.values())
            )
            self._typeset = Typeset(set_of_types)

        self._ltl_tree = gen_ltl_tree(tree=self._ltl_tree, spot_f=self._spot)

    def __init__atoms_formula(self, boolean_formula, atoms_dictionary):
        """Building the ATOMS formula and tree."""
        if boolean_formula is None and atoms_dictionary is None:
            # Generate Atom Tree
            self.__atoms_dictionary = dict()
            self.__atoms_tree = Tree()
            self.__gen_atom_tree(tree=self.__atoms_tree)
            self.__boolean_formula = Bool(self.__atoms_tree_to_formula())

        else:
            """Create a 'boolean' spot formula."""
            self.__boolean_formula = boolean_formula
            self.__atoms_dictionary = atoms_dictionary

            """Trick to generate atoms tree"""
            bool_spot = spot.formula(boolean_formula.to_spot())
            self.__atoms_dictionary = dict()
            self.__atoms_tree = Tree()
            self.__gen_atom_tree(tree=self.__atoms_tree, spot_f=bool_spot)

    def __deepcopy__(self: LTL, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        try:
            for k, v in self.__dict__.items():
                if "_LTL__ltl_tree" not in k and "spot" not in k:
                    setattr(result, k, deepcopy(v, memo))
        except Exception as e:
            print(f"LTL deepcopy Exception:\n{k}")
            raise e
        result.__init__ltl_formula(formula=self.original, typeset=self.typeset)
        return result

    @property
    def is_satisfiable(self: LTL) -> bool:
        """TODO: Too slow when adding adjacency and refinement"""
        mtx_rules = LTL.extract_mutex_rules(self.typeset)

        new_f = self & mtx_rules

        # adj_rules = LTL.extract_adjacency_rules(self.typeset)
        #
        # if adj_rules is not None:
        #     new_f = self & mtx_rules & adj_rules
        #     print(self.string)
        #     print(mtx_rules.string)
        #     print(adj_rules.string)

        # ref_rules = LTL.extract_refinement_rules(self.typeset)
        #
        # if ref_rules is not None:
        #     print(ref_rules.string)
        #     new_f = ref_rules >> new_f

        if new_f.string == "1":
            return True

        return Nuxmv.check_satisfiability(new_f.original, new_f.typeset)

    @property
    def spot_formula(self):
        return self.__simplified_formula_spot

    @property
    def is_valid(self: LTL) -> bool:

        ref_rules = LTL.extract_refinement_rules(self.typeset)

        if ref_rules is not None:
            new_f = ref_rules >> self
        else:
            new_f = self

        if new_f.string == "1":
            return True

        return Nuxmv.check_validity(new_f.original, new_f.typeset)

    def represent(
        self, output_type: Specification.OutputStr = Specification.OutputStr.SUMMARY
    ) -> str:
        if output_type == Specification.OutputStr.SIMPLIFIED:
            return str(self.__simplified_formula_spot)
        elif output_type == Specification.OutputStr.ORIGINAL:
            return str(self._spot)
        elif output_type == Specification.OutputStr.CNF:
            return "\n".join([Logic.or_([e.string for e in elem]) for elem in self.cnf])
        elif output_type == Specification.OutputStr.DNF:
            return "\n".join(
                [Logic.and_([e.string for e in elem]) for elem in self.dnf]
            )
        elif output_type == Specification.OutputStr.SUMMARY:
            cnf = "\n".join([Logic.or_([e.string for e in elem]) for elem in self.cnf])
            dnf = "\n".join([Logic.and_([e.string for e in elem]) for elem in self.dnf])
            ret = (
                f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                f"LTL SIMPLIFIED\n"
                f"{self.string}\n\n"
                f"BOOLEAN REPRESENTATION\n"
                f"{self.to_bool}\n\n"
                f"LTL EXTENDED (from booleans)\n"
                f"{self.__translate_bool_to_ltl()}\n\n"
                f"LTL CNF (from booleans)\n"
                f"{cnf}\n\n"
                f"LTL DNF (from booleans)\n"
                f"{dnf}\n"
                f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n"
            )
            return ret

    @property
    def is_atom(self) -> bool:
        return self.__atom_hash is not None

    @property
    def string(self) -> str:
        return str(self.__simplified_formula_spot)

    @property
    def original(self) -> str:
        return str(self._spot)

    def is_true(self):
        return self.__simplified_formula_spot == "1"

    @property
    def to_bool(self) -> str:
        return str(self.__boolean_formula.to_spot())

    @property
    def hash(self):
        if self.is_atom:
            return self.__atom_hash
        else:
            raise Exception("The formula is not an atom")

    @property
    def typeset(self):
        return self._typeset

    @property
    def atoms_dictionary(self) -> dict:
        return self.__atoms_dictionary

    @property
    def cnf(self) -> list[set[LTL]]:
        ret = []
        for clause in self.__boolean_formula.cnf:
            clause_set = set()
            for atom in clause:
                if atom.startswith("~"):
                    clause_set.add(~self.__atoms_dictionary[atom[1:]])
                else:
                    clause_set.add(self.__atoms_dictionary[atom])
            ret.append(clause_set)
        return ret

    @property
    def dnf(self) -> list[set[LTL]]:
        ret = []
        for clause in self.__boolean_formula.dnf:
            clause_set = set()
            for atom in clause:
                if atom.startswith("~"):
                    clause_set.add(~self.__atoms_dictionary[atom[1:]])
                else:
                    clause_set.add(self.__atoms_dictionary[atom])
            ret.append(clause_set)
        return ret

    def saturate(self, saturation: LTL):
        """Reinitiate LTL formula TODO:code better."""
        new_ltl_formula = f"({saturation.original}) -> {self.original}"
        new_typeset = self.typeset | saturation.typeset

        self.__init__ltl_formula(new_ltl_formula, new_typeset)

        new_boolean_formula = saturation.__boolean_formula >> self.__boolean_formula
        new_boolean_dictionary = {
            **saturation.__atoms_dictionary,
            **self.__atoms_dictionary,
        }
        self.__init__atoms_formula(new_boolean_formula, new_boolean_dictionary)

    def __normal_form_to_str(
        self, kind: Specification.OutputStr = Specification.OutputStr.CNF
    ):
        if kind == Specification.OutputStr.CNF:
            return Logic.and_(
                [
                    Logic.or_([atom.string for atom in clause], brackets=True)
                    for clause in self.cnf
                ],
                brackets=False,
            )
        elif kind == Specification.OutputStr.DNF:
            return Logic.or_(
                [
                    Logic.and_([atom.string for atom in clause], brackets=True)
                    for clause in self.dnf
                ],
                brackets=False,
            )
        else:
            raise AttributeError

    @staticmethod
    def __unwrap_tree(parent: dict) -> str:
        children = list(parent.values())[0]["children"]
        parent_op = list(parent.keys())[0]
        arguments = []
        for child in children:
            if isinstance(child, str):
                arguments.append(child)
            else:
                arguments.append(LTL.__unwrap_tree(child))
        return Logic.general(parent_op, arguments)

    def __atoms_tree_to_formula(self) -> str:
        tree = self.__atoms_tree
        tree_dictionary = tree.to_dict()
        if isinstance(tree_dictionary, dict):
            return LTL.__unwrap_tree(tree_dictionary)
        else:
            return tree_dictionary

    def __translate_bool_to_ltl(self, formula: str = None) -> str:
        if isinstance(formula, str):
            ltl_formula_str = formula
        else:
            ltl_formula_str = deepcopy(self.__boolean_formula.to_spot())
        for key, value in self.__atoms_dictionary.items():
            ltl_formula_str = ltl_formula_str.replace(
                key, value.represent(Specification.OutputStr.SIMPLIFIED)
            )
        return ltl_formula_str

    def tree(self, tree_type: TreeType = TreeType.LTL) -> Tree:
        if tree_type == LTL.TreeType.LTL:
            return self._ltl_tree
        elif tree_type == LTL.TreeType.BOOLEAN:
            return self.__atoms_tree
        else:
            raise AttributeError

    def _gen_ltl_tree(self, tree: Tree, spot_f=None, parent=None):
        if spot_f is None:
            spot_f = self.__simplified_formula_spot
        node = tree.create_node(
            tag=f"{spot_f.kindstr()}\t--\t({spot_f})",
            parent=parent,
            data={
                "formula": spot_f,
                "operator": spot_f.kindstr(),
                "n_children": spot_f.size(),
            },
        )

        if spot_f.size() > 0:
            for subformula in spot_f:
                LTL._gen_ltl_tree(
                    self, spot_f=subformula, tree=tree, parent=node.identifier
                )

    def __create_atom_tree_node(self, tree, parent, spot_f, sformula, tag, hash):
        data = {
            "formula": str(spot_f),
            "operator": spot_f.kindstr(),
            "n_children": spot_f.size(),
            "lformula": sformula,
        }
        node = tree.create_node(
            tag=tag,
            parent=parent,
            data=data,
        )
        if hash is not None:
            self.__atoms_dictionary[hash] = sformula

        return node

    def __gen_atom_tree(
        self, tree: Tree = None, spot_f: spot.formula = None, parent=None
    ):
        if spot_f is None:
            spot_f = self.__simplified_formula_spot

        if self.is_atom:
            self.__create_atom_tree_node(
                tree=tree,
                spot_f=spot_f,
                parent=parent,
                sformula=self,
                tag=self.hash,
                hash=self.hash,
            )
            return

        s_typeset = Spot.extract_ap(spot_f)
        set_of_types = set(
            filter((lambda x: x.name in s_typeset), self._typeset.values())
        )
        f_typeset = Typeset(set_of_types)
        f_string = spot_f.to_str()

        if (
            spot_f.kindstr() == "G"
            or spot_f.kindstr() == "F"
            or spot_f.kindstr() == "X"
            or spot_f.kindstr() == "U"
            or spot_f.kindstr() == "ap"
            or spot_f.kindstr() == "tt"
        ):
            if spot_f.kindstr() == "ap" or spot_f.kindstr() == "tt":
                hash_ = f_string
            else:
                hash_ = f"a{hashlib.sha1(f_string.encode('utf-8')).hexdigest()}"[0:5]

            if self.__simplified_formula_spot == spot_f:
                self.__atom_hash = hash_
                sformula = self
            else:
                sformula = LTL(
                    formula=spot_f, kind=self.__kind, typeset=f_typeset, atom_hash=hash_
                )

            self.__create_atom_tree_node(
                tree=tree,
                spot_f=spot_f,
                parent=parent,
                sformula=sformula,
                tag=hash_,
                hash=hash_,
            )

            return

        node = self.__create_atom_tree_node(
            tree=tree,
            spot_f=spot_f,
            parent=parent,
            sformula=self,
            tag=str(spot_f.kindstr()),
            hash=None,
        )

        if spot_f.size() > 0:
            for subformula in spot_f:
                LTL.__gen_atom_tree(
                    self,
                    spot_f=subformula,
                    tree=tree,
                    parent=node.identifier,
                )

    def __and__(self: LTL, other: LTL) -> LTL:
        """self & other Returns a new Sformula with the conjunction with
        other."""
        """compose the boolean first"""
        try:
            boolean_formula = self.__boolean_formula & other.__boolean_formula
        except BooleansNotSATException:
            raise LTLNotSATException(f"({self.original}) & ({other.original})")
        return LTL(
            formula=f"({self.original}) & ({other.original})",
            boolean_formula=boolean_formula,
            typeset=self.typeset | other.typeset,
        )

    def __or__(self: LTL, other: LTL) -> LTL:
        """self | other Returns a new Sformula with the disjunction with
        other."""
        return LTL(
            formula=f"({self.original}) | ({other.original})",
            boolean_formula=self.__boolean_formula | other.__boolean_formula,
            typeset=self.typeset | other.typeset,
        )

    def __invert__(self: LTL) -> LTL:
        """Returns a new Sformula with the negation of self."""
        return LTL(
            formula=f"!({self.original})",
            boolean_formula=~self.__boolean_formula,
            typeset=self.typeset,
        )

    def __rshift__(self: LTL, other: LTL) -> LTL:
        """>> Returns a new Sformula that is the result of self -> other
        (implies)"""
        return LTL(
            formula=f"({self.original}) -> ({other.original})",
            boolean_formula=self.__boolean_formula >> other.__boolean_formula,
            typeset=self.typeset | other.typeset,
        )

    def __iand__(self: LTL, other: LTL) -> LTL:
        """self &= other Modifies self with the conjunction with other."""
        self.__init__ltl_formula(
            formula=f"({self.original}) & ({other.original})",
            typeset=self.typeset | other.typeset,
        )
        self.__init__atoms_formula(
            boolean_formula=self.__boolean_formula & other.__boolean_formula,
            atoms_dictionary={**self.__atoms_dictionary, **other.__atoms_dictionary},
        )
        return self

    def __ior__(self: LTL, other: LTL) -> LTL:
        """self |= other Modifies self with the disjunction with other."""
        self.__init__ltl_formula(
            formula=f"({self.original}) | ({other.original})",
            typeset=self.typeset | other.typeset,
        )
        self.__init__atoms_formula(
            boolean_formula=self.__boolean_formula | other.__boolean_formula,
            atoms_dictionary={**self.__atoms_dictionary, **other.__atoms_dictionary},
        )
        return self

    class RulesOutputType(Enum):
        ListCNF = auto()

    def is_satisfiable_old(self: LTL) -> bool:
        mtx_rules = LTL.extract_mutex_rules(self.typeset)

        adj_rules = LTL.extract_adjacency_rules(self.typeset)

        try:
            if adj_rules is not None:
                self & mtx_rules & adj_rules
            else:
                self & mtx_rules
        except SpecNotSATException:
            return False
        return True

    def is_valid_old(self: LTL) -> bool:

        ref_rules = LTL.extract_refinement_rules(self.typeset)

        try:
            if ref_rules is not None:
                new_formula = ref_rules >> self
            else:
                new_formula = self
        except SpecNotSATException:
            return False

        return new_formula.is_true()

    @staticmethod
    def extract_refinement_rules(
        typeset: Typeset,
        output=None,
    ) -> LTL | tuple[list[str], Typeset] | None:
        """Extract Refinement rules from the Formula."""

        rules_str = []
        rules_typeset = Typeset()

        for key_type, set_super_types in typeset.super_types.items():
            if isinstance(key_type, Boolean):
                for super_type in set_super_types:
                    rules_str.append(
                        Logic.g_(
                            Logic.implies_(
                                key_type.name,
                                super_type.name,
                            ),
                        ),
                    )
                    rules_typeset |= Typeset({key_type})
                    rules_typeset |= Typeset(set_super_types)

        if len(rules_str) == 0:
            return None

        if output is not None and output == LTL.RulesOutputType.ListCNF:
            return rules_str, rules_typeset

        return LTL(
            formula=Logic.and_(rules_str, brackets=True),
            typeset=rules_typeset,
            kind=Specification.Kind.Rule.REFINEMENT,
        )

    @staticmethod
    def extract_mutex_rules(
        typeset: Typeset,
        output=None,
    ) -> LTL | tuple[list[str], Typeset]:
        """Extract Mutex rules from the Formula."""

        rules_str = []
        rules_typeset = Typeset()

        for mutex_group in typeset.mutex_types:
            or_elements = []
            if len(mutex_group) > 1:
                for mutex_type in mutex_group:
                    neg_group = mutex_group.symmetric_difference({mutex_type})
                    and_elements = [mutex_type.name]
                    for elem in neg_group:
                        and_elements.append(Logic.not_(elem.name))
                    or_elements.append(Logic.and_(and_elements, brackets=True))
                rules_str.append(
                    Logic.g_(Logic.or_(or_elements, brackets=False)),
                )
                rules_typeset |= Typeset(mutex_group)

        if len(rules_str) == 0:
            return LTL("TRUE")

        if output is not None and output == LTL.RulesOutputType.ListCNF:
            return rules_str, rules_typeset

        return LTL(
            formula=Logic.and_(rules_str, brackets=True),
            typeset=rules_typeset,
            kind=Specification.Kind.Rule.MUTEX,
        )

    @staticmethod
    def extract_adjacency_rules(
        typeset: Typeset,
        output=None,
    ) -> LTL | tuple[list[str], Typeset] | None:
        """Extract Adjacency rules from the Formula."""

        rules_str = []
        rules_typeset = Typeset()

        for key_type, set_adjacent_types in typeset.adjacent_types.items():
            if isinstance(key_type, Boolean):
                # G(a -> X(b | c | d))
                rules_str.append(
                    Logic.g_(
                        Logic.implies_(
                            key_type.name,
                            Logic.x_(
                                Logic.or_(
                                    [e.name for e in set_adjacent_types],
                                ),
                            ),
                        ),
                    ),
                )
                rules_typeset |= Typeset({key_type})
                rules_typeset |= Typeset(set_adjacent_types)

        if len(rules_str) == 0:
            return None

        if output is not None and output == LTL.RulesOutputType.ListCNF:
            return rules_str, rules_typeset

        return LTL(
            formula=Logic.and_(rules_str, brackets=True),
            typeset=rules_typeset,
            kind=Specification.Kind.Rule.ADJACENCY,
        )

    @staticmethod
    def extract_liveness_rules(
        typeset: Typeset,
        output=None,
    ) -> LTL | tuple[list[str], Typeset] | None:
        """Extract Liveness rules from the Formula."""

        rules_str = []
        rules_typeset = Typeset()

        sensors, outs = typeset.extract_inputs_outputs()

        for t in sensors:
            if isinstance(t, Boolean):
                if t.kind == CTypes.Kind.SENSOR:
                    rules_str.append(Logic.g_(Logic.f_(t.name)))
                rules_typeset |= Typeset({t})

        if len(rules_str) == 0:
            return None

        if output is not None and output == LTL.RulesOutputType.ListCNF:
            return rules_str, rules_typeset

        return LTL(
            formula=Logic.and_(rules_str, brackets=True),
            typeset=rules_typeset,
            kind=Specification.Kind.Rule.LIVENESS,
        )

    @staticmethod
    def context_active_rules(
        typeset: Typeset,
        output=None,
    ) -> LTL | tuple[list[str], Typeset] | None:
        """Extract Liveness rules from the Formula."""

        rules_str = []
        rules_typeset = Typeset()

        inputs, outs = typeset.extract_inputs_outputs()

        active_context_types = []
        for t in inputs:
            if isinstance(t, Boolean):
                if t.kind == CTypes.Kind.ACTIVE or t.kind == CTypes.Kind.CONTEXT:
                    active_context_types.append(t.name)
                rules_typeset |= Typeset({t})

        if len(active_context_types) > 0:
            rules_str.append(Logic.g_(Logic.and_(active_context_types)))

        if len(rules_str) == 0:
            return None

        if output is not None and output == LTL.RulesOutputType.ListCNF:
            return rules_str, rules_typeset

        return LTL(
            formula=Logic.and_(rules_str, brackets=True),
            typeset=rules_typeset,
            kind=Specification.Kind.Rule.LIVENESS,
        )


def test():
    phi = "G(F(r1 & F(r2))) & (!(r2) U r1) & G(((r2) -> (X((!(r2) U r1))))) & G(((r1) -> (X((!(r1) U r2)))))"
    # phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    sformula = LTL(phi)
    print(sformula)
    print(sformula.tree(LTL.TreeType.LTL))
    print(sformula.tree(LTL.TreeType.BOOLEAN))


if __name__ == "__main__":
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    sformula = LTL(phi)
    # print(sformula)
    # print(sformula.tree(LTL.TreeType.LTL))
    # print(sformula.tree(LTL.TreeType.BOOLEAN))

    # print(lformula.tree)
    # print(lformula.atoms)
    # print(lformula.boolean.represent(Pyeda.Output.PYEDA.to_cnf()))

    # aps = Sformula.extract_ap(lformula.spot)
    # print(aps)
