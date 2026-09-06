from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
from dataclasses import asdict 
import json

from src.storage.models import Document, Relations



def parse_relation(docs:list[Document], config: dict, field: str)->list[Relations]:
    relations = []
    for doc in docs:
        col:str = getattr(doc, field)
        rel = config["equals"].get(col) 
        if rel:
            relations.append(
                Relations(
                    path=doc.path,
                    page_id=doc.page_id,
                    source_id=doc.parent,
                    target_id=doc.id,
                    relation=rel
                )
            )
        else:
            for i, j in enumerate(config["startswith"]):
                if col.startswith(i):
                    relations.append(
                        Relations(
                            path=doc.path,
                            page_id=doc.page_id,
                            source_id=doc.parent,
                            target_id=doc.id,
                            relation=j
                        )
                    )
                    break
    return relations
        
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