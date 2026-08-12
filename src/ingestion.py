from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class ParsedHTML:
    path: Path
    title: str | None
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


def parse_html(path: Path) -> ParsedHTML:
    with path.open("r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    return ParsedHTML(
        path=path,
        title=soup.title.get_text(strip=True) if soup.title else None,
        content=soup.get_text("\n", strip=True),
        metadata={},
    )


def ingest(path: Path) -> list[ParsedHTML]:
    if not path.exists():
        raise FileNotFoundError(
            f"HTML path does not exist: {path}"
        )

    if path.is_file():
        return [parse_html(path)]

    return [
        parse_html(html_file)
        for html_file in path.rglob("*.html")
    ]