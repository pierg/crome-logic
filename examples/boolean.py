from crome_logic.specification.boolean import Bool
from copy import deepcopy


def boolean_example() -> None:
    f = "! a | b & c | (f & d) & (!f | h)"
    boolean = Bool(f)
    print(boolean.tree)
    print(boolean.cnf.to_str)
    print(boolean.dnf.to_str)


if __name__ == '__main__':
    boolean_example()