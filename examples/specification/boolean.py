from crome_logic.specification import Specification
from crome_logic.specification.boolean import Bool


def example_1() -> None:
    f = "! a | b & c | (f & d) & (!f | h)"
    boolean = Bool(f)
    print(boolean.tree)
    cnf = boolean.cnf()
    print(cnf)
    print(boolean.represent(Specification.OutputStr.CNF))
    print(boolean.represent(Specification.OutputStr.DNF))


if __name__ == "__main__":
    example_1()
