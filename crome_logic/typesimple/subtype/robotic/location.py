from crome_logic.typesimple import CromeType
from crome_logic.typesimple.subtype.base.boolean import Boolean


class Location(Boolean):
    def __init__(self, name: str, mutex: str = "", adjacency: set[str] | None = None):
        super().__init__(
            name,
            kind=CromeType.Kind.LOCATION,
            mutex_group=mutex,
            adjacency=adjacency,
        )
