from __future__ import annotations
from dataclasses import dataclass, field

from pyeda.boolalg.expr import AndOp, Expression, OrOp, expr
from pyeda.boolalg.minimization import espresso_exprs
from treelib import Tree

from crome_logic.specification import Specification
from crome_logic.specification.boolean.tools import dot_to_spot_string
from crome_logic.specification.string_logic import and_, or_
from crome_logic.specification.trees import gen_atoms_tree, extract_atoms_dictionary
from crome_logic.tools.atomic_propositions import extract_ap
from crome_logic.tools.string_manipulation import pyeda_syntax_fix, spot_syntax_fix
from crome_logic.typeelement.basic import Boolean
from crome_logic.typeset import Typeset


@dataclass
class Bool(Specification):
    formula: str
    expression: Expression | None = None
    typeset: Typeset | None = None
    tree: Tree | None = None

    def __post_init__(self):
        if self.expression is None:
            self.expression = expr(pyeda_syntax_fix(self.formula))

        if self.typeset is None:
            set_ap_str = extract_ap(self.formula)
            self.typeset = Typeset(set(map(lambda x: Boolean(name=x), set_ap_str)))

        if self.tree is None:
            self.tree = gen_atoms_tree(self.formula)

        super().__init__(self.formula, self.typeset)

    @classmethod
    def from_expression(cls,
                        expression: Expression,
                        typeset: Typeset,
                        atoms_dictionary: dict[str, str]) -> Bool:
        formula = dot_to_spot_string(expression.to_dot())
        tree = gen_atoms_tree(spot_f=formula, atoms_dictionary=atoms_dictionary)
        return cls(formula=formula,
                   expression=expression,
                   typeset=typeset,
                   tree=tree)

    def __hash__(self: Bool):
        return hash(str(self))

    def __deepcopy__(self: Bool, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__init__(formula=self.formula, typeset=self.typeset,
                        tree=self.tree)  # type: ignore
        return result

    def __str__(self):
        formula = self.represent()
        formula = formula.replace("~", "!")
        return formula

    @property
    def atoms_dictionary(self) -> dict[str, str]:
        return extract_atoms_dictionary(self.tree)

    def minimize(self):
        """Espresso minimization works only for DNF forms and it's slow."""
        if not (
                str(self.expression) == "1" or str(self.expression) == "0"
        ):
            print("start dnf")
            self.expression = self.expression.to_dnf()
            print("end dnf")
            if not (
                    str(self.expression) == "1" or str(self.expression) == "0"
            ):
                print("start espresso")
                self.expression = espresso_exprs(self.expression)[0]
                print("end espresso")

    def represent(
            self, output_type: Bool.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        if output_type == Specification.OutputStr.DEFAULT:
            return dot_to_spot_string(self.expression.to_dot())
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
        cnf = expr(self.expression.to_cnf())
        if isinstance(cnf, AndOp):
            for clause in cnf.xs:
                atoms = set()
                if isinstance(clause, OrOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool.from_expression(expression=atom,
                                                 typeset=self.typeset.get_sub_typeset(str(atom)),
                                                 atoms_dictionary=self.atoms_dictionary)
                        )
                else:
                    atoms.add(
                        Bool.from_expression(expression=clause,
                                             typeset=self.typeset.get_sub_typeset(str(clause)),
                                             atoms_dictionary=self.atoms_dictionary)
                    )
                cnf_list.append(atoms)
        elif isinstance(cnf, OrOp):
            atoms = set()
            for atom in cnf.xs:
                atoms.add(Bool.from_expression(expression=atom,
                                               typeset=self.typeset.get_sub_typeset(str(atom)),
                                               atoms_dictionary=self.atoms_dictionary))
            cnf_list.append(atoms)
        else:
            cnf_list.append({Bool.from_expression(expression=cnf,
                                                  typeset=self.typeset.get_sub_typeset(str(cnf)),
                                                  atoms_dictionary=self.atoms_dictionary)})
        return cnf_list

    def dnf(self) -> list[set[Bool]]:  # type: ignore
        dnf_list = []
        dnf = expr(self.expression.to_dnf())
        if isinstance(dnf, OrOp):
            for clause in dnf.xs:
                atoms = set()
                if isinstance(clause, AndOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool.from_expression(expression=atom,
                                                 typeset=self.typeset.get_sub_typeset(str(atom)),
                                                 atoms_dictionary=self.atoms_dictionary)
                        )
                else:
                    atoms.add(
                        Bool.from_expression(expression=clause,
                                             typeset=self.typeset.get_sub_typeset(str(clause)),
                                             atoms_dictionary=self.atoms_dictionary)
                    )
                dnf_list.append(atoms)
        elif isinstance(dnf, AndOp):
            atoms = set()
            for atom in dnf.xs:
                atoms.add(Bool.from_expression(expression=atom,
                                               typeset=self.typeset.get_sub_typeset(str(atom)),
                                               atoms_dictionary=self.atoms_dictionary))
            dnf_list.append(atoms)
        else:
            dnf_list.append({Bool.from_expression(expression=dnf,
                                                  typeset=self.typeset.get_sub_typeset(str(dnf)),
                                                  atoms_dictionary=self.atoms_dictionary)})
        return dnf_list

    def __and__(self: Bool, other: Bool) -> Bool:
        """self & other Returns a new Pyeda with the conjunction with other."""
        return Bool.from_expression(
            expression=self.expression & other.expression,
            typeset=self.typeset + other.typeset,
            atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary
        )

    def __or__(self: Bool, other: Bool) -> Bool:
        """self | other Returns a new Pyeda with the disjunction with other."""
        return Bool.from_expression(
            expression=self.expression | other.expression,
            typeset=self.typeset + other.typeset,
            atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary
        )

    def __invert__(self: Bool) -> Bool:
        """Returns a new Pyeda with the negation of self."""
        return Bool.from_expression(
            expression=~self.expression,
            typeset=self.typeset,
            atoms_dictionary=self.atoms_dictionary
        )

    def __rshift__(self: Bool, other: Bool) -> Bool:
        """>> Returns a new Pyeda that is the result of self -> other
        (implies)"""
        return Bool.from_expression(
            expression=self.expression >> other.expression,
            typeset=self.typeset + other.typeset,
            atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary
        )

    def __iand__(self: Bool, other: Bool) -> Bool:
        """self &= other Modifies self with the conjunction with other."""
        self.expression = self.expression & other.expression
        return self

    def __ior__(self: Bool, other: Bool) -> Bool:
        """self |= other Modifies self with the disjunction with other."""
        self.expression = expr(self.expression | other.expression)
        return self

    @property
    def is_satisfiable(self: Bool) -> bool:
        if str(self.expression) == "1":
            return True
        return len(self.expression.satisfy_one()) > 0

    @property
    def is_valid(self: Bool) -> bool:
        if str(self.expression) == "1":
            return True
        else:
            return False
