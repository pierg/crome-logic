import spot

from crome_logic.specification.temporal.temporal import LTL


def spot_example():
    """Spot Simplify is not good for booleans."""
    f = spot.formula("!b & (a | b)")
    f.simplify()
    print(f)


def example_1():
    phi = "! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)"
    sformula = LTL(phi)
    print(sformula.tree(LTL.TreeType.LTL))
    # print(sformula.tree(LTL.TreeType.BOOLEAN))
    # print(sformula.represent(LTL.Output.SUMMARY))


def example_boolean_ops():
    f1 = LTL("a | b")
    f2 = LTL("c & b")
    phi = f1 & f2
    print(phi.represent())

    phi = f1 | f2
    print(phi.represent())

    phi = ~f2
    print(phi.represent())

    phi = ~f2 | ~f1
    print(phi.represent())

    phi = f1 >> f2
    print(phi.represent())

    f1 &= f2
    print(f1.represent())

    f2 |= f1
    print(f2.represent())


def inconsistencies():
    # f1 = LTL("G(a)")
    # f2 = LTL("!G(a)")
    # phi_2 = "(! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p)) & z"
    # phi_2_ltl = LTL(phi_2)
    try:
        # phi = LTL("a & !a")
        # phi = LTL("a | !a")
        phi = LTL(
            "(! z & G(a & b | G(k & l)) & F(c | !d) & (X(e & f) | !X(g | h)) & (l U p))"
        )
        print(phi.tree(LTL.TreeType.LTL))
        print(phi.tree(LTL.TreeType.BOOLEAN))
        print(phi.represent(LTL.Output.SUMMARY))
    except SpecNotSATException as e:
        print(f"{e.formula.original_formula} is not satisfiable")


def release():
    f = LTL("G(!l2 | X(!l2 U l1))")
    f_not = ~f
    print(f_not)
    spot = f_not.spot_formula
    print(spot)
    print(f_not.is_satisfiable)


def bug():

    f1 = "(GFps -> G(ps <-> wa)) & GF(l1 & F(l2 & F(l3 & F(l4 & Fl5)))) & (!l2 U l1) & (!l3 U l2) & (!l4 U l3) & (!l5 U l4) & G(l2 -> X(!l2 U l1)) & G(l3 -> X(!l3 U l2)) & G(l4 -> X(!l4 U l3)) & G(l5 -> X(!l5 U l4)) & G(l1 -> X(!l1 U l5)) & G(l1 -> X(!l1 U l2)) & G(l2 -> X(!l2 U l3)) & G(l3 -> X(!l3 U l4)) & G(l4 -> X(!l4 U l5)) & G(l5 -> X(!l5 U l1)) & (GFbk -> G(bk -> Xre)) & (GFlc -> G(lf -> (Xch & Xlc))) & (GFps -> G(ps -> pc))"
    f2 = "!(((GFps & GFbk) | !((GFps -> G(ps <-> wa)) & (GFbk -> G(bk -> Xre)) & (GFps -> G(ps -> pc)))) & (GFlc | !(GF(l1 & F(l2 & F(l3 & F(l4 & Fl5)))) & (!l2 U l1) & (!l3 U l2) & (!l4 U l3) & (!l5 U l4) & G(l2 -> X(!l2 U l1)) & G(l3 -> X(!l3 U l2)) & G(l4 -> X(!l4 U l3)) & G(l5 -> X(!l5 U l4)) & G(l1 -> X(!l1 U l5)) & G(l1 -> X(!l1 U l2)) & G(l2 -> X(!l2 U l3)) & G(l3 -> X(!l3 U l4)) & G(l4 -> X(!l4 U l5)) & G(l5 -> X(!l5 U l1)) & (GFlc -> G(lf -> (Xch & Xlc))))))"

    f1 = LTL(f1)
    print(f1)

    f2 = LTL(f2)
    print(f2)

    g = f1 | ~f2
    print(g)

    f3 = ~f2
    print(f3)

    f4 = f1 | f3
    print(f4)


if __name__ == "__main__":
    example_1()
