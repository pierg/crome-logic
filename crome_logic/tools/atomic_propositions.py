from typing import Set

import spot


def extract_ap(spot_formula: str | spot.formula, ap=None) -> Set[str]:
    if isinstance(spot_formula, str):
        spot_formula = spot.formula(spot_formula)
    if ap is None:
        ap = set()
    if spot_formula._is(spot.op_ap):
        ap.add(str(spot_formula))
    else:
        for subformula in spot_formula:
            ap | extract_ap(spot_formula=subformula, ap=ap)
    return ap
