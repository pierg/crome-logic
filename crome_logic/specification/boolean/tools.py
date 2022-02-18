from __future__ import annotations

from typing import TYPE_CHECKING

import pygraphviz as pgv

from crome_logic.specification.string_logic import and_, implies_, not_, or_

if TYPE_CHECKING:
    from pygraphviz.agraph import Node


def are_all_atoms(elems) -> bool:
    for e in elems:
        if e.attr["shape"] == "circle":
            return False
    return True


def combine_atoms(atoms: list[Node], operation: str) -> str:
    if operation == "and":
        return and_([a.attr["label"] for a in atoms], brackets=True)
    elif operation == "or":
        return or_([a.attr["label"] for a in atoms])
    elif operation == "impl":
        return implies_(list(atoms)[0].attr["label"], list(atoms)[1].attr["label"])
    elif operation == "not":
        return not_(list(atoms)[0].attr["label"])
    else:
        raise Exception("Attribute unkown")


def dot_to_spot_string(dot_format_string: str) -> str:
    graph = pgv.AGraph(string=dot_format_string)
    labels = set()
    for n in graph.nodes():
        for label in n.attr["label"].split(","):
            if label != "":
                labels.add(label)

    if len(labels) == 1:
        return list(labels)[0]

    operation_graph: dict[Node, list[Node]] = {}

    for (src, tgt) in graph.edges():
        if tgt in operation_graph.keys():
            operation_graph[tgt].append(src)
        else:
            operation_graph[tgt] = [src]

    # print(operation_graph)

    spot_str = convert_dict_to_spot_string(operation_graph)
    spot_str = spot_str.replace("~", "!")
    return spot_str


def convert_dict_to_spot_string(operation_graph: dict) -> str:
    # print(operation_graph_to_str(operation_graph))
    key: None | Node = None

    for k in operation_graph.keys():
        if are_all_atoms(operation_graph[k]):
            key = k

    if key is not None:

        if len(operation_graph.keys()) == 1:
            return combine_atoms(
                atoms=operation_graph[key], operation=key.attr["label"]
            )
        # print(
        #     f"SELECTED\n{key.attr['label']} -> {[elem.attr['label'] for elem in operation_graph[key]]}"
        # )
        new_label = combine_atoms(
            atoms=operation_graph[key], operation=key.attr["label"]
        )
        key.attr["label"] = new_label
        key.attr["shape"] = "box"

        del operation_graph[key]

    return convert_dict_to_spot_string(operation_graph)
