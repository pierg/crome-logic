from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean


class Active(Boolean):
    def __init__(self):
        super().__init__("active", kind=CromeType.Kind.ACTIVE)
