from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Document:
    path: str
    page_id: int
    id: int
    parent: int
    html_tag: str
    html_id: str
    html_class: str
    href: str
    content: str

@dataclass
class Relations:
    path: str
    page_id: int
    source_id: int
    target_id: int
    relation: str