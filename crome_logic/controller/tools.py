import re


def strix_syntax_fix(text: str):
    """Adds a space next to the '!' and converts TRUE to true."""
    try:
        res = re.sub(r"!(?!\s)", "! ", text)
        res = res.replace("TRUE", "true")
    except Exception as e:
        raise e
    return res
