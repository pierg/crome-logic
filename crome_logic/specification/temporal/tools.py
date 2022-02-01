from typing import Set

import spot


def transform_spot_tree(spot_formula):
    """Applies equalities to spot tree."""

    if spot_formula._is(spot.op_F):
        if spot_formula[0]._is(spot.op_Or):
            new_f = spot.formula.Or([spot.formula.F(sf) for sf in spot_formula[0]])
            return transform_spot_tree(new_f)

    if spot_formula._is(spot.op_G):
        if spot_formula[0]._is(spot.op_And):
            new_f = spot.formula.And([spot.formula.G(sf) for sf in spot_formula[0]])
            return transform_spot_tree(new_f)

    if spot_formula._is(spot.op_X):
        if spot_formula[0]._is(spot.op_And):
            new_f = spot.formula.And([spot.formula.X(sf) for sf in spot_formula[0]])
            return transform_spot_tree(new_f)

        if spot_formula[0]._is(spot.op_Or):
            new_f = spot.formula.Or([spot.formula.X(sf) for sf in spot_formula[0]])
            return transform_spot_tree(new_f)

    if count_sugar(spot_formula) == 0:
        return spot_formula

    # Apply it recursively on any other operator's children
    return spot_formula.map(transform_spot_tree)


def count_sugar(spot_formula, n_sugar=0) -> int:
    if (
        spot_formula._is(spot.op_G)
        or spot_formula._is(spot.op_F)
        or spot_formula._is(spot.op_X)
    ):
        for subformula in spot_formula:
            return count_sugar(spot_formula=subformula, n_sugar=n_sugar + 1)

    if spot_formula.size() > 0:
        for subformula in spot_formula:
            return count_sugar(spot_formula=subformula, n_sugar=n_sugar + 1)
    else:
        return n_sugar


def extract_ap(spot_formula, ap=None) -> Set[str]:
    if ap is None:
        ap = set()
    if spot_formula._is(spot.op_ap):
        ap.add(str(spot_formula))
    else:
        for subformula in spot_formula:
            ap | extract_ap(spot_formula=subformula, ap=ap)
    return ap
