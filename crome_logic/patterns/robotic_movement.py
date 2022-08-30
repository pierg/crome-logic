from __future__ import annotations

from dataclasses import dataclass

from crome_logic.patterns import Pattern, PatternKind
from crome_logic.tools.logic import Logic


@dataclass
class CoreMovement(Pattern):
    locations: list[str]

    def __post_init__(self):
        self.kind = PatternKind.ROBOTIC_MOVEMENT


@dataclass
class Visit(CoreMovement):
    name = "Visit"
    description = "Visit a set of location in an unspecified order"
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        f = []
        """F(l1), F(l2), ...,F(ln)"""
        for l in self.locations:
            f.append(Logic.f_(l))
        """F(l1) & F(l2) & ... & F(ln)"""
        new_formula = Logic.and_(f)
        self.formula = new_formula


@dataclass
class OrderedVisit(CoreMovement):
    """Given a set of locations the robot should visit all the locations."""

    name = "Ordered Visit"
    description = (
        "The sequenced visit pattern does not forbid to visit a successor location before its "
        "predecessor, but only that after the predecessor is visited the successor is also "
        "visited. Ordered visit forbids a successor to be visited before its predecessor."
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        f = []
        """F(l1), F(l2), ...,F(ln)"""
        for l in self.locations:
            f.append(Logic.f_(l))
        """F(l1) & F(l2) & ... & F(ln)"""
        f1 = Logic.and_(f)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        new_formula = Logic.and_([f1, f2])

        self.formula = new_formula


@dataclass
class StrictOrderedVisit(CoreMovement):
    name = "Strict Ordered Visit"
    description = (
        "The ordered visit pattern does not avoid a predecessor location to be visited multiple "
        "times before its successor. Strict ordered visit forbids the behavior."
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        f = []
        """F(l1), F(l2), ...,F(ln)"""
        for l in self.locations:
            f.append(Logic.f_(l))
        """F(l1) & F(l2) & ... & F(ln)"""
        f1 = Logic.and_(f)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        f3 = []
        """1..n-1   !l_{i} U l_{i} & X(!l_{i} U l_{i+1})"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(
                Logic.not_(self.locations[i]),
                Logic.and_(
                    [
                        self.locations[i],
                        Logic.x_(
                            Logic.u_(
                                Logic.not_(self.locations[i]), self.locations[i + 1]
                            )
                        ),
                    ]
                ),
            )
            f3.append(f)
        f3 = Logic.and_(f3)

        new_formula = Logic.and_([f1, f2, f3])

        self.formula = new_formula


@dataclass
class Patrolling(CoreMovement):
    name = "Patrolling"
    description = (
        "Keep visiting a set of locations, but not a particular order. The patrolling problem "
        "also appears in literature as surveillance."
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        f = []

        for l in self.locations:
            f.append(Logic.gf_(l))

        self.formula = Logic.and_(f)


@dataclass
class OrderedPatrolling(CoreMovement):
    name = "Ordered Patrolling"
    description = (
        "Sequence patrolling deos not forbid to visit a successor location before its predecessor. "
        "Ordered patrolling ensures that (after a successor is visited) the successor is not "
        "visited (again) before its predecessor."
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        f1 = Logic.f_(lor[0])

        if len(self.locations) == 1:
            self.formula = Logic.g_(f1)
            return
        """GF(l1 & F(l2 & ... F(ln))))"""
        for l in lor[1:]:
            f2 = Logic.and_([l, f1])
            f1 = Logic.f_(f2)
        f1 = Logic.g_(f1)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        f3 = []
        """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
        for i, l in enumerate(self.locations):
            f = Logic.g_(
                Logic.implies_(
                    self.locations[(i + 1) % n],
                    Logic.x_(
                        Logic.u_(
                            Logic.not_(self.locations[(i + 1) % n]), self.locations[i]
                        )
                    ),
                )
            )
            f3.append(f)
        f3 = Logic.and_(f3)

        new_formula = Logic.and_([f1, f2, f3])

        self.formula = new_formula


@dataclass
class StrictOrderedPatrolling(CoreMovement):
    name = "Strict Ordered Patrolling"
    description = (
        "The ordered patrolling does not avoid a predecessor location to be visited multiple "
        "times before its successor. Strict Ordered Patrolling ensures that, after a predecessor "
        "is visited, it is not visited again before its successor."
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        f1 = Logic.f_(lor[0])

        if len(self.locations) == 1:
            self.formula = Logic.g_(f1)
            return
        """GF(l1 & F(l2 & ... F(ln))))"""
        for l in lor[1:]:
            f2 = Logic.and_([l, f1])
            f1 = Logic.f_(f2)
        f1 = Logic.g_(f1)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        f3 = []
        """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
        for i, l in enumerate(self.locations):
            f = Logic.g_(
                Logic.implies_(
                    self.locations[(i + 1) % n],
                    Logic.x_(
                        Logic.u_(
                            Logic.not_(self.locations[(i + 1) % n]), self.locations[i]
                        )
                    ),
                )
            )
            f3.append(f)
        f3 = Logic.and_(f3)

        if len(self.locations) > 2:
            f4 = []
            """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
            for i, l in enumerate(self.locations):
                f = Logic.g_(
                    Logic.implies_(
                        self.locations[i],
                        Logic.x_(
                            Logic.u_(
                                Logic.not_(self.locations[i]),
                                self.locations[(i + 1) % n],
                            )
                        ),
                    )
                )
                f4.append(f)
            f4 = Logic.and_(f4)
            new_formula = Logic.and_([f1, f2, f3, f4])
        else:
            new_formula = Logic.and_([f1, f2, f3])

        self.formula = new_formula


@dataclass
class StrictOrderedLocations(CoreMovement):
    name = "Strict Order"
    description = (
        "Modification of StrictOrderedPatrolling, it impose the order but not the actual visit."
        "The ordered patrolling does not avoid a predecessor location to be visited multiple "
        "times before its successor. Strict Ordered Patrolling ensures that, after a predecessor "
        "is visited, it is not visited again before its successor. "
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        # f1 = Logic.f_(lor[0])
        #
        # if len(self.locations) == 1:
        #     self.formula = Logic.g_(f1)
        #     return
        # """GF(l1 & F(l2 & ... F(ln))))"""
        # for l in lor[1:]:
        #     f2 = Logic.and_([l, f1])
        #     f1 = Logic.f_(f2)
        # f1 = Logic.g_(f1)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        f3 = []
        """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
        for i, l in enumerate(self.locations):
            f = Logic.g_(
                Logic.implies_(
                    self.locations[(i + 1) % n],
                    Logic.x_(
                        Logic.u_(
                            Logic.not_(self.locations[(i + 1) % n]), self.locations[i]
                        )
                    ),
                )
            )
            f3.append(f)
        f3 = Logic.and_(f3)

        if len(self.locations) > 2:
            f4 = []
            """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
            for i, l in enumerate(self.locations):
                f = Logic.g_(
                    Logic.implies_(
                        self.locations[i],
                        Logic.x_(
                            Logic.u_(
                                Logic.not_(self.locations[i]),
                                self.locations[(i + 1) % n],
                            )
                        ),
                    )
                )
                f4.append(f)
            f4 = Logic.and_(f4)
            new_formula = Logic.and_([f2, f3, f4])
        else:
            new_formula = Logic.and_([f2, f3])

        self.formula = new_formula


@dataclass
class OrderedLocations(CoreMovement):
    name = "Order Location"
    description = (
        "Modification of OrderedPatrolling, it impose the order but not the actual visit."
        "The ordered patrolling does not avoid a predecessor location to be visited multiple "
        "times before its successor. Strict Ordered Patrolling ensures that, after a predecessor "
        "is visited, it is not visited again before its successor. "
    )
    arguments = [{"name": "locations", "format": "list", "type": "location"}]

    def __post_init__(self):
        lor = list(self.locations)
        lor.reverse()
        n = len(self.locations)

        # f1 = Logic.f_(lor[0])
        #
        # if len(self.locations) == 1:
        #     self.formula = Logic.g_(f1)
        #     return
        # """GF(l1 & F(l2 & ... F(ln))))"""
        # for l in lor[1:]:
        #     f2 = Logic.and_([l, f1])
        #     f1 = Logic.f_(f2)
        # f1 = Logic.g_(f1)

        f2 = []
        """1..n-1   !l_{i+1} U l_{i}"""
        for i, l in enumerate(self.locations[: n - 1]):
            f = Logic.u_(Logic.not_(self.locations[i + 1]), self.locations[i])
            f2.append(f)
        f2 = Logic.and_(f2)

        f3 = []
        """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
        for i, l in enumerate(self.locations):
            f = Logic.g_(
                Logic.implies_(
                    self.locations[(i + 1) % n],
                    Logic.x_(
                        Logic.u_(
                            Logic.not_(self.locations[(i + 1) % n]), self.locations[i]
                        )
                    ),
                )
            )
            f3.append(f)
        f3 = Logic.and_(f3)

        if len(self.locations) > 2:
            f4 = []
            """1..n   G(l_{(i+1)%n} -> X((!l_{(i+1)%n} U l_{i})))"""
            for i, l in enumerate(self.locations):
                f = Logic.g_(
                    Logic.implies_(
                        self.locations[i],
                        Logic.x_(
                            Logic.u_(
                                Logic.not_(self.locations[i]),
                                self.locations[(i + 1) % n],
                            )
                        ),
                    )
                )
                f4.append(f)
            f4 = Logic.and_(f4)
            new_formula = Logic.and_([f2, f3])
        else:
            new_formula = Logic.and_([f2, f3])

        self.formula = new_formula
