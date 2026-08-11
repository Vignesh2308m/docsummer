from pathlib import Path
from bs4 import BeautifulSoup

from .storage import RustDocument


def parse_html(
    path: Path,
) -> list[RustDocument]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        soup = BeautifulSoup(
            file,
            "html.parser",
        )

    documents: list[RustDocument] = []

    # Parse Rust documentation HTML here.
    #
    # Each parsed item becomes:
    #
    # RustDocument(
    #     id=...,
    #     library=...,
    #     item=...,
    #     kind=...,
    #     definition=...,
    #     description=...,
    #     example=...
    # )

    return documents


def ingest(
    path: Path,
) -> list[RustDocument]:

    if not path.exists():
        raise FileNotFoundError(
            f"HTML path does not exist: {path}"
        )

    if path.is_file():
        return parse_html(path)

    documents: list[RustDocument] = []

    for html_file in path.rglob("*.html"):
        documents.extend(
            parse_html(html_file)
        )

    return documents