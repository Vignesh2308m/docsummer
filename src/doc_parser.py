from bs4 import BeautifulSoup, Tag

from .ingestion import ParsedHTML


def parse_element(element: Tag) -> dict:
    result = {}

    # HTML attributes
    if element.attrs:
        result["_attributes"] = dict(element.attrs)

    text = " ".join(element.get_text(" ", strip=True).split())

    if text:
        result["_text"] = text

    # Child elements
    for child in element.children:

        if not isinstance(child, Tag):
            continue

        key = child.name
        value = parse_element(child)

        if key in result:

            if not isinstance(result[key], list):
                result[key] = [result[key]]

            result[key].append(value)

        else:
            result[key] = value

    return result


def parse_html(parsed_html: ParsedHTML) -> dict:

    soup = BeautifulSoup(
        parsed_html.content,
        "lxml",
    )

    if not soup.html:
        return {}

    return {
        "html": parse_element(soup.html)
    }