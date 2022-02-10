from crome_logic.specification.temporal import LTL


def example_1() -> None:
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    ltl = LTL(phi)
    print(ltl.tree)
    print(ltl.boolean.tree)


if __name__ == "__main__":
    example_1()
