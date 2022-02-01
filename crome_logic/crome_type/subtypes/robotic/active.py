from crome_logic.crome_type.crome_type import CromeType
from crome_logic.crome_type.subtypes.base.boolean import Boolean


class Active(Boolean):
    def __init__(self):
        super().__init__("active", kind=CromeType.Kind.ACTIVE)
