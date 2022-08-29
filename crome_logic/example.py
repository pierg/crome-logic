from copy import deepcopy

from specification.boolean import Bool
from specification.temporal import LTL


def boolean_example() -> None:
    f = "! a | b & c | (f & d) & (!f | h)"
    boolean = Bool(f)
    print(boolean.tree)
    print(boolean.cnf.to_str)
    print(boolean.dnf.to_str)


def temporal_example() -> None:
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    ltl = LTL(phi)
    lel2 = deepcopy(ltl)
    assert ltl == lel2
    print(ltl.tree)
    print(ltl.boolean.tree)
    print(ltl.summary)


def satisfiability_example() -> None:
    phi = "a & b"
    ltl = LTL(phi)
    print(ltl.is_satisfiable)

    phi = "a & !a"
    ltl = LTL(phi)
    print(ltl.is_satisfiable)


def validity_example() -> None:
    phi = "a & !a"
    ltl = LTL(phi)
    print(ltl.is_valid)

    phi = "a | !a"
    ltl = LTL(phi)
    print(ltl.is_valid)


def simiplificaiton_example() -> None:
    phi1 = LTL("TRUE")
    phi2 = LTL("a")
    print(phi1 & phi2)
    print(phi1 | phi2)
    phi2 &= phi1
    print(phi2)
    phi2 |= phi1
    print(phi2)


if __name__ == "__main__":
    boolean_example()
    temporal_example()
    satisfiability_example()
    validity_example()
    simiplificaiton_example()
