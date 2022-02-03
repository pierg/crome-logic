from __future__ import annotations

from copy import deepcopy

from pyeda.boolalg.expr import Expression, expr
from pyeda.boolalg.minimization import espresso_exprs

from crome_logic.crome_type.subtype.base.boolean import Boolean
from crome_logic.specification.specification import Specification
from crome_logic.specification.temporal import extract_ap
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

        self._expression: expr = expression

        if typeset is None:
            set_ap_str = extract_ap(str(self._expression))
            set_ap = set(map(lambda x: Boolean(x), set_ap_str))
            self._typeset = Typeset(set_ap)

        super().__init__(str(self._expression), self._typeset)

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
        return self._expression

    def minimize(self):
        """Espresso minimization works only for DNF forms and it's slow."""
        if not (str(self._expression) == "1" or str(self._expression) == "0"):
            print("start dnf")
            self._expression = self._expression.to_dnf()
            print("end dnf")
            if not (str(self._expression) == "1" or str(self._expression) == "0"):
                print("start espresso")
                self._expression = espresso_exprs(self._expression)[0]
                print("end espresso")

    def represent(
        self, output_type: Specification.OutputStr = Specification.OutputStr.DEFAULT
    ) -> str:
        pass

    def cnf(self) -> list[set[Bool]]:  # type: ignore
        pass

    def dnf(self) -> list[set[Bool]]:  # type: ignore
        pass

    def __and__(self: Specification, other: Specification) -> Bool:
        """self & other Returns a new Bool with the conjunction with
        other."""

    def __or__(self: Specification, other: Specification) -> Bool:
        """self | other Returns a new Bool with the disjunction with
        other."""

    def __invert__(self: Specification) -> Bool:
        """Returns a new Bool with the negation of self."""

    def __rshift__(self: Specification, other: Specification) -> Bool:
        """>> Returns a new Bool that is the result of self -> other
        (implies)"""

    def __iand__(self: Specification, other: Specification) -> Bool:
        """self &= other Modifies self with the conjunction with other."""

    def __ior__(self: Specification, other: Specification) -> Bool:
        """self |= other Modifies self with the disjunction with other."""

    @property
    def is_satisfiable(self: Specification) -> bool:
        pass

    @property
    def is_valid(self: Specification) -> bool:
        pass
