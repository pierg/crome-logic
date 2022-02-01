from crome_logic.crome_type.crome_type import CromeType
from crome_logic.crome_type.subtype.base.boolean import Boolean


class Context(Boolean):
    def __init__(self, name: str, mutex: str = ""):
        super().__init__(name, kind=CromeType.Kind.CONTEXT, mutex_group=mutex)
