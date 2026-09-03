from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from src.storage.models import Document
from dataclasses import asdict
import json

def parse_html(html: str, path: str, page_id: int, root_tag: str = "html") -> list[Document]:
    soup = BeautifulSoup(html, "html.parser")

    counter = 0
    documents = []

    def build_node(element: Tag, parent: int = 0):
        nonlocal counter

        counter += 1
        current_id = counter

        # Only direct text, excluding child tags
        content = " ".join(
            text.strip()
            for text in element.contents
            if isinstance(text, NavigableString) and text.strip()
        )

        node = Document(
            path = path,
            page_id=page_id,
            id=current_id,
            parent=parent,
            html_tag=element.name,
            html_id=element.get("id", ""),
            html_class=" ".join(element.get("class", [])),
            href=element.get("href", ""),
            content=content
        )

        documents.append(node)

        for child in element.children:
            if isinstance(child, Tag):
                build_node(child, current_id)

    root = soup.find(root_tag)

    if root is None:
        raise ValueError("HTML document does not contain an <html> element")

    build_node(root)

    return documents

def save_document(document: Document, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            [asdict(i) for i in document],
            f,
            indent=2,
            ensure_ascii=False
        )