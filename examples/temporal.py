from copy import deepcopy

from crome_logic.specification.temporal import LTL


def example_1() -> None:
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    ltl = LTL(phi)
    lel2 = deepcopy(ltl)
    assert ltl == lel2
    print(ltl.tree)
    print(ltl.boolean.tree)
    print(ltl.print_summary)


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


if __name__ == "__main__":
    example_1()
