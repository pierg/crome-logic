def is_true_string(expression: str) -> bool:
    """DOCTEST.

    >>> is_true_string("1")
    True
    """
    if expression == "1":
        return True
    if expression == "TRUE":
        return True
    return False


def is_false_string(expression: str) -> bool:
    if expression == "0":
        return True
    if expression == "FALSE":
        return True
    return False
