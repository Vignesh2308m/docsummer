from pathlib import Path
from typing import Iterator


def lookup(path: str | Path, pattern: str) -> Iterator[Path]:
    path = Path(path)

    if not path.exists():
        return

    if path.is_file():
        if path.match(pattern):
            yield path
        return

    for item in path.iterdir():

        if item.is_dir():
            yield from lookup(item, pattern)

        elif item.is_file() and item.match(pattern):
            yield item