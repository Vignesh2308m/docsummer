from bs4 import BeautifulSoup, Tag
from src.storage.models import Document
from dataclasses import asdict
import json

def parse_html(html: str) -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")

    counter = 0
    documents = []

    def build_node(element: Tag, parent: int = 0):
        nonlocal counter

        counter += 1
        current_id = counter

        node = Document(
            id=current_id,
            parent=parent,
            html_tag=element.name,
            html_id=element.get("id", ""),
            html_class=" ".join(element.get("class", [])),
            href=element.get("href", ""),
            content=element.get_text(" ", strip=True)
        )

        documents.append(node)

        for child in element.children:
            if isinstance(child, Tag):
                build_node(child, current_id)

    root = soup.find("html")

    if root is None:
        raise ValueError("HTML document does not contain an <html> element")

    build_node(root)

    return documents

def save_document(document: Document, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            asdict(document),
            f,
            indent=2,
            ensure_ascii=False
        )