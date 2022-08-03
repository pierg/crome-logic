from __future__ import annotations

from dataclasses import dataclass, field

from src.crome_logic.patterns import Pattern, PatternKind


@dataclass
class Init(Pattern):
    element: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = self.element


@dataclass
class G(Pattern):
    element: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"G({self.element})"


@dataclass
class F(Pattern):
    element: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"F{self.element}"


@dataclass
class X(Pattern):
    element: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"X{self.element}"


@dataclass
class GF(Pattern):
    element: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"GF{self.element}"


@dataclass
class InfOft(GF):
    pass


@dataclass
class U(Pattern):
    pre: str
    post: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"(({self.pre}) U ({self.post}))"


@dataclass
class W(Pattern):
    pre: str
    post: str

    def __post_init__(self):
        self.kind = PatternKind.BASIC
        self.formula = f"((({self.pre}) U ({self.post})) | G({self.pre}))"
