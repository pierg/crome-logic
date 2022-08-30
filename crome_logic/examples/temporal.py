from copy import deepcopy

from crome_logic.specification.temporal import LTL


def temporal_example() -> None:
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    ltl = LTL(phi)
    lel2 = deepcopy(ltl)
    assert ltl == lel2
    print(ltl.tree)
    print(ltl.boolean.tree)
    print(ltl.summary)


if __name__ == "__main__":
    temporal_example()
