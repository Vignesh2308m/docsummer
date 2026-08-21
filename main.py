from bs4 import BeautifulSoup, Tag
import json

from src.parser import extract_html
from src.templates.trait import TRAIT_TEMPLATE

PATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html/alloc/str/pattern/trait.Pattern.html"


def main():
    with open(PATH, encoding="utf-8") as f:
        result = extract_html(f,TRAIT_TEMPLATE)
        with open("trait_test.json","w") as fp:
            json.dump(result, fp, indent=4)

if __name__ == "__main__":
    main()