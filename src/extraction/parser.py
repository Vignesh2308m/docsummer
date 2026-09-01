from bs4 import BeautifulSoup, Tag
from src.storage.models import Document
from dataclasses import asdict
import json

def parse_html(html: str) -> Document:
    soup = BeautifulSoup(html, "html.parser")

    counter = 0

    def build_node(element: Tag) -> Document:
        nonlocal counter

        counter += 1

        # Direct text only, excluding children's text
        content = element.get_text(" ", strip=True)
        content = content.strip() if content else ""

        node = Document(
            id=counter,
            html_tag=element.name,
            html_id=element.get("id", ""),
            html_class=" ".join(element.get("class", [])),
            href=element.get("href", ""),
            content=content,
            child=[]
        )

        for child in element.children:
            if isinstance(child, Tag):
                node.child.append(build_node(child))

        return node

    root = soup.find("html")

    if root is None:
        raise ValueError("HTML document does not contain an <html> element")

    return build_node(root)

def save_document(document: Document, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            asdict(document),
            f,
            indent=2,
            ensure_ascii=False
        )