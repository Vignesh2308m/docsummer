from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Document:
    id: int
    html_tag: str
    html_id: str
    html_class: str
    href: str
    content: str
    child: List[Document]