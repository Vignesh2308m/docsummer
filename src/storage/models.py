from dataclasses import dataclass
from typing import Optional


@dataclass
class Trait:
    id: Optional[int]
    name: str
    type: str
    declaration: Optional[str] = None
    description: Optional[str] = None
    source_text: Optional[str] = None
    source_href: Optional[str] = None


@dataclass
class TraitMethod:
    id: Optional[int]
    trait_id: int
    name: str
    kind: str  # "required" or "provided"
    href: Optional[str] = None
    signature: Optional[str] = None
    description: Optional[str] = None
    source_text: Optional[str] = None
    source_href: Optional[str] = None


@dataclass
class TraitImplementor:
    id: Optional[int]
    trait_id: int
    name: str
    href: Optional[str] = None
    source_text: Optional[str] = None
    source_href: Optional[str] = None