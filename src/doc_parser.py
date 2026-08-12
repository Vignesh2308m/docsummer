from pathlib import Path

from bs4 import BeautifulSoup

from .ingestion import ParsedHTML
from .storage import RustDocument


def clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def get_code_blocks(element) -> list[str]:
    examples = []

    for code in element.find_all("code"):
        text = code.get_text("\n", strip=True)

        if text:
            examples.append(text)

    return examples


def find_definition(element) -> str:
    candidates = [
        element.select_one(".item-info"),
        element.select_one(".method"),
        element.select_one(".associatedconstant"),
        element.select_one(".associatedtype"),
        element.select_one(".structfield"),
        element.select_one(".trait-impl"),
    ]

    for candidate in candidates:
        if candidate:
            text = clean_text(
                candidate.get_text(" ", strip=True)
            )

            if text:
                return text

    code = element.find("code")

    if code:
        return clean_text(
            code.get_text(" ", strip=True)
        )

    return ""


def find_item_name(element) -> str:
    candidates = [
        ".fnname",
        ".struct",
        ".trait",
        ".enum",
        ".type",
        ".method",
    ]

    for selector in candidates:
        name_element = element.select_one(selector)

        if name_element:
            name = clean_text(
                name_element.get_text(" ", strip=True)
            )

            if name:
                return name

    heading = element.find(
        ["h1", "h2", "h3", "h4", "h5"]
    )

    if heading:
        return clean_text(
            heading.get_text(" ", strip=True)
        )

    return ""


def find_description(element) -> str:
    doc = (
        element.select_one(".docblock")
        or element.select_one(".docblock-short")
    )

    if not doc:
        return ""

    return doc.get_text(
        "\n",
        strip=True,
    ).strip()


def parse_html(
    parsed_html: ParsedHTML,
) -> list[RustDocument]:

    soup = BeautifulSoup(
        parsed_html.content,
        "lxml",
    )

    library = parsed_html.metadata.get(
        "library",
        "",
    )

    title = (
        parsed_html.title
        or parsed_html.path.stem
    )

    selectors = [
        ".item-decl",
        ".method",
        ".associatedconstant",
        ".associatedtype",
        ".structfield",
        ".variant",
        ".trait",
        ".struct",
        ".enum",
        ".fn",
        ".type",
        ".constant",
        ".static",
        ".macro",
    ]

    documents: list[RustDocument] = []
    found: set[int] = set()

    for selector in selectors:

        kind = selector.removeprefix(".")

        for element in soup.select(selector):

            element_id = id(element)

            if element_id in found:
                continue

            found.add(element_id)

            item = find_item_name(element)

            if not item:
                continue

            document = RustDocument(
                id=f"{library}:{item}",
                library=library,
                item=item,
                kind=kind,
                definition=find_definition(element),
                description=find_description(element),
                example=get_code_blocks(element),
            )

            documents.append(document)

    if documents:
        return documents

    doc = soup.select_one(".docblock")

    description = ""

    if doc:
        description = doc.get_text(
            "\n",
            strip=True,
        ).strip()

    return [
        RustDocument(
            id=f"{library}:{title}",
            library=library,
            item=title,
            kind="page",
            definition="",
            description=description,
            example=get_code_blocks(soup),
        )
    ]