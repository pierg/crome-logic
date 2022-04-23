from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.patterns import Pattern
from crome_logic.tools.logic import Logic


@dataclass(kw_only=True)
class Trigger(Pattern):
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.ROBOTIC_TRIGGER)
    pre: str
    post: str


@dataclass(kw_only=True)
class InstantaneousReaction(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.g_(Logic.implies_(self.pre, self.post))


@dataclass(kw_only=True)
class BoundReaction(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.g_(Logic.iff_(self.pre, self.post))


@dataclass(kw_only=True)
class BoundDelay(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.g_(Logic.iff_(self.pre, Logic.x_(self.post)))


@dataclass(kw_only=True)
class PromptReaction(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.x_(self.post)))


@dataclass(kw_only=True)
class DelayedReaction(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.f_(self.post)))


@dataclass(kw_only=True)
class Wait(Trigger):
    description: str = field(init=False, default="TODO: description")

    def __post_init__(self):
        self.formula = Logic.u_(self.pre, self.post)
