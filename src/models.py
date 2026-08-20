from dataclasses import dataclass, field


@dataclass
class Function:
    name: str
    definition: str
    example: str | None = None


@dataclass
class Method:
    name: str
    definition: str
    example: str | None = None


@dataclass
class Implementation:
    name: str
    definition: str
    functions: list[Function] = field(default_factory=list)


@dataclass
class Trait:
    title: str
    type: str
    definition: str
    required_methods: list[Method] = field(default_factory=list)
    provided_methods: list[Method] = field(default_factory=list)
    implementations: list[Implementation] = field(default_factory=list)