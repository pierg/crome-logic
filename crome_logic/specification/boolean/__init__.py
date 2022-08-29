from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, fields

from pyeda.boolalg.expr import AndOp, Expression, OrOp, expr
from pyeda.boolalg.minimization import espresso_exprs
from specification import Cnf, Dnf, Specification
from specification.boolean.tools import dot_to_spot_string
from specification.tools import is_true_string
from specification.trees import extract_atoms_dictionary, gen_atoms_tree
from tools.atomic_propositions import extract_ap
from tools.string_manipulation import pyeda_syntax_fix, spot_syntax_fix
from treelib import Tree
from typelement.basic import Boolean
from typeset import Typeset


@dataclass(frozen=True)
class Bool(Specification):
    _init_formula: str
    _typeset: Typeset | None = None
    _expression: Expression | None = None
    _tree: Tree | None = None

    @property
    def expression(self) -> Expression:
        return self._expression

    @property
    def tree(self) -> Tree:
        return self._tree

    def __post_init__(self):
        if self._expression is None:
            # print(pyeda_syntax_fix(self._init_formula))
            expression = expr(pyeda_syntax_fix(self._init_formula))
            object.__setattr__(self, "_expression", expression)

        if self._typeset is None:
            set_ap_str = extract_ap(self.formula)
            typeset = Typeset(set(map(lambda x: Boolean(name=x), set_ap_str)))
            object.__setattr__(self, "_typeset", typeset)

        if self._tree is None:
            tree = gen_atoms_tree(self.formula)
            object.__setattr__(self, "_tree", tree)

    @classmethod
    def from_expression(
        cls, expression: Expression, typeset: Typeset, atoms_dictionary: dict[str, str]
    ) -> Bool:
        formula = dot_to_spot_string(expression.to_dot())
        tree = gen_atoms_tree(spot_f=formula, atoms_dictionary=atoms_dictionary)
        return cls(
            _init_formula=formula, _expression=expression, _typeset=typeset, _tree=tree
        )

    def __hash__(self: Bool):
        return hash(str(self))

    def __deepcopy__(self: Bool, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        for field in fields(cls):
            if not (field.name == "_expression" or field.name == "_tree"):
                object.__setattr__(
                    result, field.name, deepcopy(getattr(self, field.name))
                )
        result.__post_init__()  # type: ignore
        return result

    @property
    def formula(self) -> str:
        return dot_to_spot_string(self.expression.to_dot())

    def __str__(self):
        return self.formula

    @property
    def atoms_dictionary(self) -> dict[str, str]:
        return extract_atoms_dictionary(self.tree)

    def minimize(self):
        """Espresso minimization works only for DNF forms and it's slow."""
        if not (str(self.expression) == "1" or str(self.expression) == "0"):
            print("start dnf")
            self._expression = self.expression.to_dnf()  # type: ignore
            print("end dnf")
            if not (str(self.expression) == "1" or str(self.expression) == "0"):
                print("start espresso")
                expression = espresso_exprs(self.expression)[0]
                object.__setattr__(self, "_expression", expression)
                print("end espresso")

    @property
    def cnf(self) -> Cnf:
        cnf_list = []
        cnf = expr(self.expression.to_cnf())
        if isinstance(cnf, AndOp):
            for clause in cnf.xs:
                atoms = set()
                if isinstance(clause, OrOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool.from_expression(
                                expression=atom,
                                typeset=self.typeset.get_sub_typeset(str(atom)),
                                atoms_dictionary=self.atoms_dictionary,
                            )
                        )
                else:
                    atoms.add(
                        Bool.from_expression(
                            expression=clause,
                            typeset=self.typeset.get_sub_typeset(str(clause)),
                            atoms_dictionary=self.atoms_dictionary,
                        )
                    )
                cnf_list.append(atoms)
        elif isinstance(cnf, OrOp):
            atoms = set()
            for atom in cnf.xs:
                atoms.add(
                    Bool.from_expression(
                        expression=atom,
                        typeset=self.typeset.get_sub_typeset(str(atom)),
                        atoms_dictionary=self.atoms_dictionary,
                    )
                )
            cnf_list.append(atoms)
        else:
            cnf_list.append(
                {
                    Bool.from_expression(
                        expression=cnf,
                        typeset=self.typeset.get_sub_typeset(str(cnf)),
                        atoms_dictionary=self.atoms_dictionary,
                    )
                }
            )
        return Cnf(cnf_list)  # type: ignore

    @property
    def dnf(self) -> Dnf:
        dnf_list = []
        dnf = expr(self.expression.to_dnf())
        if isinstance(dnf, OrOp):
            for clause in dnf.xs:
                atoms = set()
                if isinstance(clause, AndOp):
                    for atom in clause.xs:
                        atoms.add(
                            Bool.from_expression(
                                expression=atom,
                                typeset=self.typeset.get_sub_typeset(str(atom)),
                                atoms_dictionary=self.atoms_dictionary,
                            )
                        )
                else:
                    atoms.add(
                        Bool.from_expression(
                            expression=clause,
                            typeset=self.typeset.get_sub_typeset(str(clause)),
                            atoms_dictionary=self.atoms_dictionary,
                        )
                    )
                dnf_list.append(atoms)
        elif isinstance(dnf, AndOp):
            atoms = set()
            for atom in dnf.xs:
                atoms.add(
                    Bool.from_expression(
                        expression=atom,
                        typeset=self.typeset.get_sub_typeset(
                            spot_syntax_fix(str(atom))
                        ),
                        atoms_dictionary=self.atoms_dictionary,
                    )
                )
            dnf_list.append(atoms)
        else:
            dnf_list.append(
                {
                    Bool.from_expression(
                        expression=dnf,
                        typeset=self.typeset.get_sub_typeset(str(dnf)),
                        atoms_dictionary=self.atoms_dictionary,
                    )
                }
            )
        return Dnf(dnf_list)  # type: ignore

    def __and__(self: Specification, other: Specification) -> Bool:
        """self & other Returns a new Pyeda with the conjunction with other."""
        if isinstance(self, Bool) and isinstance(other, Bool):
            return Bool.from_expression(
                expression=self.expression & other.expression,
                typeset=self.typeset + other.typeset,
                atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary,
            )
        raise AttributeError

    def __or__(self: Specification, other: Specification) -> Bool:
        """self | other Returns a new Pyeda with the disjunction with other."""
        if isinstance(self, Bool) and isinstance(other, Bool):
            return Bool.from_expression(
                expression=self.expression | other.expression,
                typeset=self.typeset + other.typeset,
                atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary,
            )
        raise AttributeError

    def __invert__(self: Specification) -> Bool:
        """Returns a new Pyeda with the negation of self."""
        if isinstance(self, Bool):
            return Bool.from_expression(
                expression=~self.expression,
                typeset=self.typeset,
                atoms_dictionary=self.atoms_dictionary,
            )
        raise AttributeError

    def __rshift__(self: Specification, other: Specification) -> Bool:
        """>> Returns a new Pyeda that is the result of self -> other
        (implies)"""
        if isinstance(self, Bool) and isinstance(other, Bool):
            return Bool.from_expression(
                expression=self.expression >> other.expression,
                typeset=self.typeset + other.typeset,
                atoms_dictionary=self.atoms_dictionary | other.atoms_dictionary,
            )
        raise AttributeError

    def __iand__(self: Specification, other: Specification) -> Bool:
        """self &= other Modifies self with the conjunction with other."""
        if isinstance(self, Bool) and isinstance(other, Bool):
            expression = self.expression & other.expression
            object.__setattr__(self, "_expression", expression)
            return self
        raise AttributeError

    def __ior__(self: Specification, other: Specification) -> Bool:
        """self |= other Modifies self with the disjunction with other."""
        if isinstance(self, Bool) and isinstance(other, Bool):
            expression = expr(self.expression | other.expression)
            object.__setattr__(self, "_expression", expression)
            return self
        raise AttributeError

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

    @property
    def is_true_expression(self) -> bool:
        if is_true_string(str(self)):
            return True
