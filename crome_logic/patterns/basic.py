from __future__ import annotations

from dataclasses import dataclass, field

from crome_logic.patterns import Pattern


@dataclass(kw_only=True)
class Init(Pattern):
    element: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = self.element


@dataclass(kw_only=True)
class G(Pattern):
    element: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"G{self.element}"


@dataclass(kw_only=True)
class F(Pattern):
    element: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"F{self.element}"


@dataclass(kw_only=True)
class X(Pattern):
    element: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"X{self.element}"


@dataclass(kw_only=True)
class GF(Pattern):
    element: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"GF{self.element}"


@dataclass(kw_only=True)
class U(Pattern):
    pre: str
    post: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"(({self.pre}) U ({self.post}))"


@dataclass(kw_only=True)
class W(Pattern):
    pre: str
    post: str
    kind: Pattern.Kind = field(init=False, default=Pattern.Kind.BASIC)

    def __post_init__(self):
        self.formula = f"((({self.pre}) U ({self.post})) | G({self.pre}))"
