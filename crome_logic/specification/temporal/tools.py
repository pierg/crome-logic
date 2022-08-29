import spot


def transform_spot_tree(formula: spot.formula):
    """Applies equalities to spot tree."""

    if formula._is(spot.op_F):
        if formula[0]._is(spot.op_Or):
            new_f = spot.formula.Or([spot.formula.F(sf) for sf in formula[0]])
            return transform_spot_tree(new_f)

    if formula._is(spot.op_G):
        if formula[0]._is(spot.op_And):
            new_f = spot.formula.And([spot.formula.G(sf) for sf in formula[0]])
            return transform_spot_tree(new_f)

    if formula._is(spot.op_X):
        if formula[0]._is(spot.op_And):
            new_f = spot.formula.And([spot.formula.X(sf) for sf in formula[0]])
            return transform_spot_tree(new_f)

        if formula[0]._is(spot.op_Or):
            new_f = spot.formula.Or([spot.formula.X(sf) for sf in formula[0]])
            return transform_spot_tree(new_f)

    if count_sugar(formula) == 0:
        return formula

    # Apply it recursively on any other operator's children
    return formula.map(transform_spot_tree)


def count_sugar(formula: spot.formula, n_sugar: int = 0) -> int:
    if formula._is(spot.op_G) or formula._is(spot.op_F) or formula._is(spot.op_X):
        for subformula in formula:
            return count_sugar(formula=subformula, n_sugar=n_sugar + 1)

    if formula.size() > 0:
        for subformula in formula:
            return count_sugar(formula=subformula, n_sugar=n_sugar + 1)
    return n_sugar
