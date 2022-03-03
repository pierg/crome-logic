from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean
from crome_logic.typesimple.subtype.base.bounded_integer import BoundedInteger


class IntegerAction(BoundedInteger):
    def __init__(self, name: str, min_value=0, max_value=50):
        super().__init__(
            name,
            kind=CromeType.Kind.ACTION,
            min_value=min_value,
            max_value=max_value,
        )


class BooleanAction(Boolean):
    def __init__(self, name: str, mutex: str = ""):
        super().__init__(name, kind=CromeType.Kind.ACTION, mutex_group=mutex)
