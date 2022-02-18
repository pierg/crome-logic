import spot

from crome_logic.controller.synthesis import generate_controller
from crome_logic.tools.io import save_to_file


def example_1() -> None:
    a1: str = "G(F(a1))"
    g1: str = "G(a1 <-> (b1 | c1))"
    i1: str = "a1"
    o1: str = "b1, c1"

    realizable1, controller1, time1 = generate_controller(a1, g1, i1, o1)

    print(controller1)
    file_path = save_to_file(controller1, "controller_1")

    automaton = spot.automaton(file_path)
    dotfile = automaton.to_str(format="dot")

    print(dotfile)

    a2: str = "G(F(a2))"
    g2: str = "G(a2 -> b2)"
    i2: str = "a2"
    o2: str = "b2"

    realizable2, controller2, time2 = generate_controller(a2, g2, i2, o2)

    print(controller2)


if __name__ == "__main__":
    example_1()
