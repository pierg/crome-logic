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
        self.name = "Instantaneous Reaction"
        self.description = "The occurrence of a stimulus instantaneously triggers a counteraction."
        self.formula = Logic.g_(Logic.implies_(self.pre, self.post))


@dataclass
class BoundReaction(Trigger):

    def __post_init__(self):
        self.name = "Bound Reaction"
        self.description = "A counteraction must be performed every time and only when a specific location is entered."
        self.formula = Logic.g_(Logic.iff_(self.pre, self.post))


@dataclass
class BoundDelay(Trigger):

    def __post_init__(self):
        self.name = "Bound Delay"
        self.description = "A counteraction must be performed, in the next time instant, every time and only when a " \
                           "specific location is entered."
        self.formula = Logic.g_(Logic.iff_(self.pre, Logic.x_(self.post)))


@dataclass
class PromptReaction(Trigger):

    def __post_init__(self):
        self.name = "Prompt Reaction"
        self.description = "The occurrence of a stimulus triggers a counteraction promptly, i.e in the next time " \
                           "instant."
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.x_(self.post)))


@dataclass
class DelayedReaction(Trigger):

    def __post_init__(self):
        self.name = "Delayed Reaction"
        self.description = "The occurrence of a stimulus triggers a counteraction some time later."
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.f_(self.post)))


@dataclass
class Wait(Trigger):

    def __post_init__(self):
        self.name = "Wait"
        self.description = "Inaction is desired till a stimulus occurs."
        self.formula = Logic.u_(self.pre, self.post)
