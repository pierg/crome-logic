from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean
from crome_logic.typesimple.subtype.base.bounded_integer import BoundedInteger


class IntegerSensor(BoundedInteger):
    def __init__(self, name: str, min_value=0, max_value=50):
        super().__init__(
            name,
            kind=CromeType.Kind.SENSOR,
            min_value=min_value,
            max_value=max_value,
        )


class BooleanSensor(Boolean):
    def __init__(self, name: str, mutex: str = ""):
        super().__init__(name, kind=CromeType.Kind.SENSOR, mutex_group=mutex)
