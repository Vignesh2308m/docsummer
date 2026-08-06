from pathlib import Path
from bs4 import BeautifulSoup
import json
import re


# Your Rust documentation directory
DOC_ROOT = Path(
    r"C:\Users\Vickynila\.rustup\toolchains"
    r"\stable-x86_64-pc-windows-msvc\share\doc\rust\html"
)

OUTPUT_FILE = "rust_std_docs.jsonl"


def clean_text(text):
    """Clean whitespace while preserving readable text."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def get_code_blocks(element):
    """Extract code examples from an HTML element."""
    examples = []

    for code in element.find_all("code"):
        text = code.get_text("\n", strip=True)

        if text:
            examples.append(text)

    return examples


def find_definition(item_element):
    """
    rustdoc usually stores signatures in elements such as:
        code
        .item-info
        .method
        .associatedconstant
        .structfield
    """

    # First try common rustdoc structures
    candidates = [
        item_element.select_one(".item-info"),
        item_element.select_one(".method"),
        item_element.select_one(".associatedconstant"),
        item_element.select_one(".associatedtype"),
        item_element.select_one(".structfield"),
        item_element.select_one(".trait-impl"),
    ]

    for candidate in candidates:
        if candidate:
            text = clean_text(candidate.get_text(" ", strip=True))
            if text:
                return text

    # Fallback: first code block
    code = item_element.find("code")

    if code:
        return clean_text(code.get_text(" ", strip=True))

    return ""


def get_library(soup, file_path):
    """
    Try to determine the library/module represented by the page.
    """

    # Rustdoc breadcrumb
    breadcrumbs = soup.select(".breadcrumb")

    if breadcrumbs:
        text = clean_text(
            breadcrumbs[0].get_text(" ", strip=True)
        )

        if text:
            return text

    # Rustdoc sidebar/crate information
    crate = soup.select_one(".crate")

    if crate:
        text = clean_text(crate.get_text(" ", strip=True))

        if text:
            return text

    # Derive something from path
    relative = file_path.relative_to(DOC_ROOT)

    parts = list(relative.parts)

    if parts:
        return parts[0]

    return ""


def extract_page(file_path):
    """Extract documentation from one HTML page."""

    try:
        html = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
        return []

    soup = BeautifulSoup(html, "lxml")

    title = soup.find("title")

    if title:
        title = clean_text(title.get_text(" ", strip=True))
    else:
        title = file_path.stem

    library = get_library(soup, file_path)

    records = []

    # ---------------------------------------------------------
    # Find documented items
    # ---------------------------------------------------------

    # Rustdoc commonly uses these classes for documented items.
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

    found = set()

    for selector in selectors:

        for element in soup.select(selector):

            # Avoid processing same element multiple times
            element_id = id(element)

            if element_id in found:
                continue

            found.add(element_id)

            # Find name
            name = ""

            # Rustdoc commonly has .fnname, .struct, .trait, etc.
            name_element = (
                element.select_one(".fnname")
                or element.select_one(".struct")
                or element.select_one(".trait")
                or element.select_one(".enum")
                or element.select_one(".type")
                or element.select_one(".method")
            )

            if name_element:
                name = clean_text(
                    name_element.get_text(" ", strip=True)
                )

            # Fallback to heading
            if not name:
                heading = element.find(
                    ["h1", "h2", "h3", "h4", "h5"]
                )

                if heading:
                    name = clean_text(
                        heading.get_text(" ", strip=True)
                    )

            # If still nothing, skip
            if not name:
                continue

            definition = find_definition(element)

            description = ""

            # Try documentation section
            doc = (
                element.select_one(".docblock")
                or element.select_one(".docblock-short")
            )

            if doc:
                description = clean_text(
                    doc.get_text("\n", strip=True)
                )

            examples = get_code_blocks(element)

            # Determine item type
            kind = selector.replace(".", "")

            relative_path = file_path.relative_to(
                DOC_ROOT
            )

            record = {
                "file": str(relative_path).replace("\\", "/"),
                "library": library,
                "item": name,
                "kind": kind,
                "definition": definition,
                "description": description,
                "examples": examples,
                "path": str(file_path)
            }

            records.append(record)

    # ---------------------------------------------------------
    # If no structured item was found, still save page
    # ---------------------------------------------------------

    if not records:

        description = ""

        # Try main documentation area
        doc = soup.select_one(".docblock")

        if doc:
            description = clean_text(
                doc.get_text("\n", strip=True)
            )

        examples = get_code_blocks(soup)

        relative_path = file_path.relative_to(
            DOC_ROOT
        )

        records.append({
            "file": str(relative_path).replace("\\", "/"),
            "library": library,
            "item": title,
            "kind": "page",
            "definition": "",
            "description": description,
            "examples": examples,
            "path": str(file_path)
        })

    return records


def main():

    if not DOC_ROOT.exists():
        print("Documentation directory does not exist:")
        print(DOC_ROOT)
        return

    html_files = list(DOC_ROOT.rglob("*.html"))

    print(f"Found {len(html_files)} HTML files")

    total_records = 0

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as output:

        for index, file_path in enumerate(html_files, 1):

            print(
                f"[{index}/{len(html_files)}] "
                f"{file_path.relative_to(DOC_ROOT)}"
            )

            records = extract_page(file_path)

            for record in records:

                output.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    )
                    + "\n"
                )

                total_records += 1

    print()
    print("Finished.")
    print(f"Records: {total_records}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()