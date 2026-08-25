from bs4 import BeautifulSoup


def extract_html(html, config):
    soup = BeautifulSoup(html, "html.parser")
    result = {}

    for item in config:
        key = item["key"]
        css = item["css"]
        how = item["how"]

        elements = soup.select(css)

        if how == "text":
            result[key] = [
                element.get_text(" ", strip=True)
                for element in elements
            ]

        elif how == "href":
            result[key] = [
                element.get("href")
                for element in elements
            ]

        elif how == "str-only":
            result[key] = [
                element.find(string=True, recursive=False)
                for element in elements
            ]

        elif how == "element":
            objects = []

            for element in elements:
                obj = {}

                for field, selector in item["fields"].items():           
                    # Extract from a child element
                    selector, extract_type = selector.rsplit(":", 1)

                    child = element.select_one(selector)

                    if child is None:
                        obj[field] = None

                    elif extract_type == "text":
                        obj[field] = child.get_text(" ", strip=True)

                    elif extract_type == "href":
                        obj[field] = child.get("href")

                objects.append(obj)

            result[key] = objects

    return result

def coverage(html, document):
    soup = BeautifulSoup(html, "lxml")

    # All meaningful text in HTML
    html_text = soup.select_one("#main-content").get_text(" ", strip=True)

    # All text extracted into RustDocument
    def collect(obj):
        if isinstance(obj, str):
            return [obj]
        if isinstance(obj, list):
            return sum((collect(x) for x in obj), [])
        if hasattr(obj, "__dataclass_fields__"):
            return sum(
                (collect(getattr(obj, f)) for f in obj.__dataclass_fields__),
                []
            )
        return []

    extracted_text = " ".join(collect(document))

    html_words = set(html_text.split())
    extracted_words = set(extracted_text.split())

    missing = html_words - extracted_words
    matched = html_words & extracted_words

    return {
        "coverage": len(matched) / len(html_words) if html_words else 1,
        "html_words": len(html_words),
        "extracted_words": len(extracted_words),
        "missing": sorted(missing)
    }