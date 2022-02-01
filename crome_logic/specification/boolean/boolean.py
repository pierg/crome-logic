from __future__ import annotations

from copy import deepcopy

from pyeda.boolalg.expr import Expression, expr
from pyeda.boolalg.minimization import espresso_exprs

from crome_logic.specification.specification import Specification
from crome_logic.typeset.typeset import Typeset


class Bool(Specification):
    def __init__(self, formula: str | Expression, typeset: Typeset | None = None):

        if isinstance(formula, str):
            formula = formula.replace("!", "~")
            try:
                expression = expr(formula)
            except Exception as e:
                print(e)
                raise Exception("Problem")
        elif isinstance(formula, Expression):
            expression = formula
        else:
            raise AttributeError

        self.__expression = expression
        super().__init__(formula, typeset)

    def __deepcopy__(self: Bool, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        try:
            for k, v in self.__dict__.items():
                if "_Bool__expression" in k:
                    setattr(result, k, expr(self.expression))
                else:
                    setattr(result, k, deepcopy(v, memo))
        except Exception:
            print(k)
        return result

    @property
    def expression(self):
        return self.__expression

    def minimize(self):
        """Espresso minimization works only for DNF forms and it's slow."""
        if not (str(self.__expression) == "1" or str(self.__expression) == "0"):
            print("start dnf")
            self.__expression = self.__expression.to_dnf()
            print("end dnf")
            if not (str(self.__expression) == "1" or str(self.__expression) == "0"):
                print("start espresso")
                self.__expression = espresso_exprs(self.__expression)[0]
                print("end espresso")

    def represent(
        self, output_type: Specification.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        pass

    @property
    def cnf(self) -> list[set[LTL]]:
        pass

    @property
    def dnf(self) -> list[set[LTL]]:
        pass

    def __and__(self: LTL, other: LTL) -> LTL:
        """self & other Returns a new LTL with the conjunction with
        other."""

    def __or__(self: LTL, other: LTL) -> LTL:
        """self | other Returns a new LTL with the disjunction with
        other."""

    def __invert__(self: LTL) -> LTL:
        """Returns a new LTL with the negation of self."""

    def __rshift__(self: LTL, other: LTL) -> LTL:
        """>> Returns a new LTL that is the result of self -> other
        (implies)"""

    def __iand__(self: LTL, other: LTL) -> LTL:
        """self &= other Modifies self with the conjunction with other."""

    def __ior__(self: LTL, other: LTL) -> LTL:
        """self |= other Modifies self with the disjunction with other."""

    @property
    def is_satisfiable(self: LTL) -> bool:
        pass

    @property
    def is_valid(self: LTL) -> bool:
        pass
