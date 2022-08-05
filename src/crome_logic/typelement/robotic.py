from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.src.crome_logic.typelement import TypeKind
from crome_logic.src.crome_logic.typelement.basic import (
    BooleanControllable,
    BooleanUncontrollable,
    BoundedInteger,
)


@dataclass(kw_only=True)
class BooleanAction(BooleanControllable):
    kind: TypeKind = field(init=False, default=TypeKind.ACTION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanLocation(BooleanControllable):
    kind: TypeKind = field(init=False, default=TypeKind.LOCATION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanSensor(BooleanUncontrollable):
    kind: TypeKind = field(init=False, default=TypeKind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanContext(BooleanUncontrollable):
    kind: TypeKind = field(init=False, default=TypeKind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class Active(BooleanControllable):
    name: str = field(init=False, default="active")
    kind = TypeKind.ACTIVE

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class IntegerAction(BoundedInteger):
    kind: TypeKind = field(init=False, default=TypeKind.ACTION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class IntegerSensor(BoundedInteger):
    kind: TypeKind = field(init=False, default=TypeKind.SENSOR)

    def __hash__(self):
        return hash(self.name + type(self).__name__)
