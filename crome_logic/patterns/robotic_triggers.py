from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.patterns import Pattern, PatternKind
from crome_logic.tools.logic import Logic




@dataclass
class Trigger(Pattern):
    kind: PatternKind = field(init=False, default=PatternKind.ROBOTIC_TRIGGER)
    pre: str
    post: str

    @classmethod
    def iterate_over_preconditions(cls, preconditions: list[str], post: str):
        p = Pattern()
        for pre in preconditions:
            p &= cls(pre=pre, post=post)
        return p



@dataclass
class InitInstantaneousReaction(Trigger):

    def __post_init__(self):
        self.name = "Init Instantaneous Reaction"
        self.description = "At the first step, the occurrence of a stimulus instantaneously triggers a counteraction."
        self.formula = (Logic.implies_(self.pre, self.post))


@dataclass
class InitBoundReaction(Trigger):

    def __post_init__(self):
        self.name = "Init Bound Reaction"
        self.description = "At the first step, a counteraction must be performed every time and only when a specific location is entered."
        self.formula = (Logic.iff_(self.pre, self.post))


@dataclass
class InitBoundDelay(Trigger):

    def __post_init__(self):
        self.name = "Init Bound Delay"
        self.description = "At the first step, a counteraction must be performed, in the next time instant, every time and only when a " \
                           "specific location is entered."
        self.formula = (Logic.iff_(self.pre, Logic.x_(self.post)))


@dataclass
class InitPromptReaction(Trigger):

    def __post_init__(self):
        self.name = "Init Prompt Reaction"
        self.description = "At the first step, the occurrence of a stimulus triggers a counteraction promptly, i.e in the next time " \
                           "instant."
        self.formula = (Logic.implies_(self.pre, Logic.x_(self.post)))


@dataclass
class InitDelayedReaction(Trigger):

    def __post_init__(self):
        self.name = "Init Delayed Reaction"
        self.description = "At the first step, the occurrence of a stimulus triggers a counteraction some time later."
        self.formula = (Logic.implies_(self.pre, Logic.f_(self.post)))


@dataclass
class InstantaneousReaction(Trigger):
    name = "Instantaneous Reaction"
    description = "The occurrence of a stimulus instantaneously triggers a counteraction."
    arguments = [{"name": "trigger", "format": "value", "type": "any"},
                 {"name": "reaction", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.name = "Instantaneous Reaction"
        self.description = "The occurrence of a stimulus instantaneously triggers a counteraction."
        self.formula = Logic.g_(Logic.implies_(self.pre, self.post))


@dataclass
class BoundReaction(Trigger):
    name = "Bound Reaction"
    description = "A counteraction must be performed every time and only when a specific location is entered."
    arguments = [{"name": "trigger", "format": "value", "type": "any"},
                 {"name": "reaction", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.name = "Bound Reaction"
        self.description = "A counteraction must be performed every time and only when a specific location is entered."
        self.formula = Logic.g_(Logic.iff_(self.pre, self.post))


@dataclass
class BoundDelay(Trigger):
    name = "Bound Delay"
    description = "A counteraction must be performed, in the next time instant, every time and only when a " \
                  "specific location is entered."
    arguments = [{"name": "trigger", "format": "value", "type": "any"},
                 {"name": "reaction", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.formula = Logic.g_(Logic.iff_(self.pre, Logic.x_(self.post)))


@dataclass
class PromptReaction(Trigger):
    name = "Prompt Reaction"
    description = "The occurrence of a stimulus triggers a counteraction promptly, i.e in the next time " \
                       "instant."
    arguments = [{"name": "trigger", "format": "value", "type": "any"},
                 {"name": "reaction", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.x_(self.post)))


@dataclass
class DelayedReaction(Trigger):
    name = "Delayed Reaction"
    description = "The occurrence of a stimulus triggers a counteraction some time later."
    arguments = [{"name": "trigger", "format": "value", "type": "any"},
                 {"name": "reaction", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.name = "Delayed Reaction"
        self.description = "The occurrence of a stimulus triggers a counteraction some time later."
        self.formula = Logic.g_(Logic.implies_(self.pre, Logic.f_(self.post)))


@dataclass
class Wait(Trigger):
    name = "Wait"
    description = "Inaction is desired till a stimulus occurs."
    arguments = [{"name": "do", "format": "value", "type": "any"},
                 {"name": "until", "format": "value", "type": "any"}]

    def __post_init__(self):
        self.name = "Wait"
        self.description = "Inaction is desired till a stimulus occurs."
        self.formula = Logic.u_(self.pre, self.post)
