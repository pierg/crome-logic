from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.typeelement import CromeType
from crome_logic.typeelement.basic import Boolean, BoundedInteger


@dataclass(kw_only=True)
class BooleanAction(Boolean):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.ACTION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanLocation(Boolean):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.LOCATION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanSensor(Boolean):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class BooleanContext(Boolean):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.CONTEXT)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class Active(Boolean):
    name: str = field(init=False, default="active")
    kind = CromeType.Kind.ACTIVE

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class IntegerAction(BoundedInteger):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.ACTION)

    def __hash__(self):
        return hash(self.name + type(self).__name__)


@dataclass(kw_only=True)
class IntegerSensor(BoundedInteger):
    kind: CromeType.Kind = field(init=False, default=CromeType.Kind.SENSOR)

    def __hash__(self):
        return hash(self.name + type(self).__name__)
