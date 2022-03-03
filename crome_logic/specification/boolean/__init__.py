from __future__ import annotations

from copy import deepcopy

from pyeda.boolalg.expr import AndOp, Expression, OrOp, expr
from pyeda.boolalg.minimization import espresso_exprs
from treelib import Tree

from crome_logic.specification import Specification
from crome_logic.specification.boolean.tools import dot_to_spot_string
from crome_logic.specification.string_logic import and_, or_
from crome_logic.specification.trees import gen_atoms_tree
from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.typeset import Typeset
from crome_logic.typesimple.subtype.base.boolean import Boolean


class Bool(Specification):
    def __init__(
        self,
        formula: str | Expression,
        typeset: Typeset | None = None,
        tree: None | Tree = None,
    ):

        if isinstance(formula, str):
            self._init__boolean_formula(formula, typeset, tree)
        elif isinstance(formula, Expression):
            self._pyeda_expression = formula
            if typeset is None:
                raise AttributeError
            self._typeset = typeset
        else:
            raise AttributeError

        super().__init__(
            dot_to_spot_string(self._pyeda_expression.to_dot()), self._typeset
        )

    def __hash__(self: Bool):
        return hash(str(self))

    def _init__boolean_formula(
        self, formula: str, typeset: Typeset | None, tree: None | Tree = None
    ):
        if typeset is None:
            set_ap_str = extract_ap(formula)
            set_ap = set(map(lambda x: Boolean(x), set_ap_str))
            self._typeset = Typeset(set_ap)
        else:
            self._typeset = typeset
        if tree is None:
            self._tree = gen_atoms_tree(formula)
        else:
            self._tree = tree
        formula = formula.replace("!", "~")
        self._pyeda_expression = expr(formula)

    def __deepcopy__(self: Bool, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        try:
            for k, v in self.__dict__.items():
                if "_Bool_expression" in k:
                    setattr(result, k, expr(self.expression))
                else:
                    setattr(result, k, deepcopy(v, memo))
        except Exception:
            print(k)
        return result

    def __str__(self):
        formula = str(self._pyeda_expression)
        formula = formula.replace("~", "!")
        return formula

    @property
    def expression(self) -> Expression:
        return self._pyeda_expression

    @property
    def tree(self) -> Tree:
        return self._tree

    def minimize(self):
        """Espresso minimization works only for DNF forms and it's slow."""
        if not (
            str(self._pyeda_expression) == "1" or str(self._pyeda_expression) == "0"
        ):
            print("start dnf")
            self._pyeda_expression = self._pyeda_expression.to_dnf()
            print("end dnf")
            if not (
                str(self._pyeda_expression) == "1" or str(self._pyeda_expression) == "0"
            ):
                print("start espresso")
                self._pyeda_expression = espresso_exprs(self._pyeda_expression)[0]
                print("end espresso")

    def represent(
        self, output_type: Bool.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        if output_type == Specification.OutputStr.DEFAULT:
            return dot_to_spot_string(self._pyeda_expression.to_dot())
        elif output_type == Specification.OutputStr.CNF:
            return " & ".join([or_([str(e) for e in elem]) for elem in self.cnf()])
        elif output_type == Specification.OutputStr.DNF:
            return " | ".join(
                [and_([str(e) for e in elem], brackets=True) for elem in self.dnf()]
            )
        else:
            raise NotImplementedError

    def cnf(self) -> list[set[Bool]]:  # type: ignore
        cnf_list = []
        cnf = expr(self._pyeda_expression.to_cnf())
        if isinstance(cnf, AndOp):
            for clause in cnf.xs:
                atoms = set()
                if isinstance(clause, OrOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool(atom, typeset=self.typeset.get_sub_typeset(str(atom)))
                        )
                else:
                    atoms.add(
                        Bool(clause, typeset=self.typeset.get_sub_typeset(str(clause)))
                    )
                cnf_list.append(atoms)
        elif isinstance(cnf, OrOp):
            atoms = set()
            for atom in cnf.xs:
                atoms.add(Bool(atom, typeset=self.typeset.get_sub_typeset(str(atom))))
            cnf_list.append(atoms)
        else:
            cnf_list.append({Bool(cnf, typeset=self.typeset.get_sub_typeset(str(cnf)))})
        return cnf_list

    def dnf(self) -> list[set[Bool]]:  # type: ignore
        dnf_list = []
        dnf = expr(self._pyeda_expression.to_dnf())
        if isinstance(dnf, OrOp):
            for clause in dnf.xs:
                atoms = set()
                if isinstance(clause, AndOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool(atom, typeset=self.typeset.get_sub_typeset(str(atom)))
                        )
                else:
                    atoms.add(
                        Bool(clause, typeset=self.typeset.get_sub_typeset(str(clause)))
                    )
                dnf_list.append(atoms)
        elif isinstance(dnf, AndOp):
            atoms = set()
            for atom in dnf.xs:
                atoms.add(Bool(atom, typeset=self.typeset.get_sub_typeset(str(atom))))
            dnf_list.append(atoms)
        else:
            dnf_list.append({Bool(dnf, typeset=self.typeset.get_sub_typeset(str(dnf)))})
        return dnf_list

    def __and__(self: Bool, other: Bool) -> Bool:
        """self & other Returns a new Pyeda with the conjunction with other."""
        return Bool(
            self.expression & other.expression, typeset=self.typeset + other.typeset
        )

    def __or__(self: Bool, other: Bool) -> Bool:
        """self | other Returns a new Pyeda with the disjunction with other."""
        return Bool(
            self.expression | other.expression, typeset=self.typeset + other.typeset
        )

    def __invert__(self: Bool) -> Bool:
        """Returns a new Pyeda with the negation of self."""
        inverted_expr = ~self._pyeda_expression
        return Bool(inverted_expr, typeset=self.typeset)

    def __rshift__(self: Bool, other: Bool) -> Bool:
        """>> Returns a new Pyeda that is the result of self -> other
        (implies)"""
        return Bool(
            self.expression >> other.expression, typeset=self.typeset + other.typeset
        )

    def __lshift__(self: Bool, other: Bool) -> Bool:
        """<< Returns a new Pyeda that is the result of other -> self
        (implies)"""
        return Bool(
            other.expression >> self.expression, typeset=self.typeset + other.typeset
        )

    def __iand__(self: Bool, other: Bool) -> Bool:
        """self &= other Modifies self with the conjunction with other."""
        self._pyeda_expression = self._pyeda_expression & other.expression
        return self

    def __ior__(self: Bool, other: Bool) -> Bool:
        """self |= other Modifies self with the disjunction with other."""
        self._pyeda_expression = expr(self._pyeda_expression | other.expression)
        return self

    @property
    def is_satisfiable(self: Bool) -> bool:
        pass

    @property
    def is_valid(self: Bool) -> bool:
        pass
