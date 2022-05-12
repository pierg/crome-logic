from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.patterns import Pattern, PatternKind
from crome_logic.tools.logic import Logic


@dataclass
class Trigger(Pattern):
    kind: PatternKind = field(init=False, default=PatternKind.ROBOTIC_TRIGGER)
    pre: str
    post: str


@dataclass
class InstantaneousReaction(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.g_(Logic.implies_(self.pre, self.post))


@dataclass
class BoundReaction(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.g_(Logic.iff_(self.pre, self.post))


@dataclass
class BoundDelay(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.g_(Logic.iff_(self.pre, Logic.x_(self.post)))


@dataclass
class PromptReaction(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.x_(self.post)))


@dataclass
class DelayedReaction(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.f_(self.post)))


@dataclass
class Wait(Trigger):
    

    def __post_init__(self):
        self.description = "TODO: description"
        self.formula = Logic.u_(self.pre, self.post)
