from treelib import Tree


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
            gen_ltl_tree(
                spot_f=subformula, tree=tree, parent=node.identifier
            )

    return tree

