import hashlib
from typing import Any

import spot
from treelib import Tree

from crome_logic.specification.string_logic import general_logic


def gen_ltl_tree(spot_f, tree: Tree | None = None, parent=None) -> Tree:
    if tree is None:
        tree = Tree()
    node = tree.create_node(
        tag=f"{spot_f.kindstr()}\t--\t({spot_f})",
        parent=parent,
        data={
            "formula": spot_f,
            "operator": spot_f.kindstr(),
            "n_children": spot_f.size(),
        },
    )

    if spot_f.size() > 0:
        for subformula in spot_f:
            gen_ltl_tree(spot_f=subformula, tree=tree, parent=node.identifier)

    return tree


def gen_atoms_tree(
    spot_f: spot.formula | str, tree: Tree | None = None, parent=None
) -> Tree:
    if isinstance(spot_f, str):
        spot_f = spot.formula(spot_f)
    if tree is None:
        tree = Tree()

    hash_ = ""
    ltl_string = ""
    if spot_f.kindstr() in ["G", "F", "X", "U", "ap", "tt", "ff"]:
        ltl_string = spot_f.to_str()
        if spot_f.kindstr() in ["ap", "tt", "ff"]:
            hash_ = ltl_string
        else:
            hash_ = f"a{hashlib.sha1(ltl_string.encode('utf-8')).hexdigest()}"[0:5]

    tag = spot_f.kindstr() if hash_ == "" else hash_
    node = tree.create_node(
        tag=tag,
        parent=parent,
        data={
            "generator": ltl_string,
            "spot_f": spot_f,
        },
    )

    if spot_f.size() > 0 and spot_f.kindstr() not in [
        "G",
        "F",
        "X",
        "U",
        "ap",
        "tt",
        "ff",
    ]:
        for subformula in spot_f:
            gen_atoms_tree(spot_f=subformula, tree=tree, parent=node.identifier)

    return tree


def extract_atoms_dictionary(tree: Tree) -> dict[str, str]:
    hash_ltl: dict[str, str] = {}
    for node in tree.leaves():
        hash_ltl[node.tag] = node.data["generator"]

    return hash_ltl


def boolean_tree_to_formula(boolean_tree) -> str:
    tree_dictionary = boolean_tree.to_dict()
    if isinstance(tree_dictionary, dict):
        return unwrap_tree(tree_dictionary)
    else:
        return tree_dictionary


def unwrap_tree(tree: dict[str, Any]) -> str:
    children = list(tree.values())[0]["children"]
    parent_op = list(tree.keys())[0]
    arguments = []
    for child in children:
        if isinstance(child, str):
            arguments.append(child)
        else:
            arguments.append(unwrap_tree(child))
    return general_logic(parent_op, arguments)
