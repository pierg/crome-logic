from copy import deepcopy
from crome_logic.specification.temporal import LTL



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


if __name__ == '__main__':
    satisfiability_example()
    validity_example()
    simiplificaiton_example()