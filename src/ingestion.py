from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedHTML:
    path: Path
    content: str
    metadata: dict[str, str] = field(
        default_factory=dict
    )


def read_html(path: Path) -> ParsedHTML:
    if not path.is_file():
        raise FileNotFoundError(
            f"HTML file does not exist: {path}"
        )

    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    return ParsedHTML(
        path=path,
        content=content,
        metadata={
            "filename": path.name,
            "extension": path.suffix,
        },
    )


def ingest(path: Path) -> list[ParsedHTML]:

    if not path.exists():
        raise FileNotFoundError(
            f"HTML path does not exist: {path}"
        )

    if path.is_file():
        return [read_html(path)]

    return [
        read_html(html_file)
        for html_file in path.rglob("*.html")
    ]