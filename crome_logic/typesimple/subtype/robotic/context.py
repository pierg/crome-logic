from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean


class Context(Boolean):
    def __init__(self, name: str, mutex: str = ""):
        super().__init__(name, kind=CromeType.Kind.CONTEXT, mutex_group=mutex)
