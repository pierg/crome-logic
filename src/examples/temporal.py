from copy import deepcopy

from crome_cgg.context import Context
from crome_logic.specification.temporal import LTL
from crome_logic.typelement.robotic import BooleanContext
from crome_logic.typeset import Typeset


def example_1() -> None:
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    ltl = LTL(phi)
    lel2 = deepcopy(ltl)
    assert ltl == lel2
    print(ltl.tree)
    print(ltl.boolean.tree)
    print(ltl.summary)


def sat1() -> None:
    phi = "a & b"
    ltl = LTL(phi)
    print(ltl.is_satisfiable)

    phi = "a & !a"
    ltl = LTL(phi)
    print(ltl.is_satisfiable)


def val1() -> None:
    phi = "a & !a"
    ltl = LTL(phi)
    print(ltl.is_valid)

    phi = "a | !a"
    ltl = LTL(phi)
    print(ltl.is_valid)


def simplify() -> None:
    phi1 = LTL("TRUE")
    phi2 = LTL("a")
    print(phi1 & phi2)
    print(phi1 | phi2)
    phi2 &= phi1
    print(phi2)
    phi2 |= phi1
    print(phi2)



def sat_example():
    day = Context("day")
    night = Context("night")
    c = day & night
    print(c.is_satisfiable)
    print(c)


def unsat_example():
    typeset = Typeset({
        BooleanContext(name="day", mutex_group="time"),
        BooleanContext(name="night", mutex_group="time"),
    })
    day = Context(_init_formula="day", _typeset=typeset)
    night = Context(_init_formula="night", _typeset=typeset)
    c = day & night
    print(c.is_satisfiable)
    print(c)
    c = day | night
    print(c.is_satisfiable)
    print(c)


if __name__ == '__main__':
    unsat_example()
