import hashlib
import random
import re
import string

match_LTL_no_spaces = r"((?<=[G|F|X])(?=[^\s]))|((?<=[U])(?=[a-z]))|(?=[U])+(?<=[a-z])"


def latexit(formula: str) -> str:
    import spot

    return spot.formula(str(formula))._repr_latex_()


def add_spaces_spot_ltl(formula: str) -> str:
    """TODO: FIX 'TRUE'"""
    return re.sub(match_LTL_no_spaces, " ", formula)


def get_name_and_id(value: str | None = None) -> tuple[str, str]:
    if value is None:
        """5 character ID generated from a random string"""
        value = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    """5 character ID generated from the name"""
    id = hashlib.sha1(value.encode("UTF-8")).hexdigest()[:5]
    return value, id


def strix_syntax_fix(text: str) -> str:
    """Adds a space next to the '!' and converts TRUE to true."""
    try:
        res = re.sub(r"!(?!\s)", "! ", text)
        res = res.replace("TRUE", "true")
    except Exception as e:
        raise e
    return res
