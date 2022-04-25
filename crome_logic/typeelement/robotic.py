from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.typeelement import TypeKind
from crome_logic.typeelement.basic import Boolean, BoundedInteger


@dataclass(kw_only=True)
class BooleanAction(Boolean):
    kind: TypeKind = field(init=False, default=TypeKind.ACTION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanLocation(Boolean):
    kind: TypeKind = field(init=False, default=TypeKind.LOCATION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanSensor(Boolean):
    kind: TypeKind = field(init=False, default=TypeKind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanContext(Boolean):
    kind: TypeKind = field(init=False, default=TypeKind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class Active(Boolean):
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
