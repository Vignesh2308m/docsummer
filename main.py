from bs4 import BeautifulSoup, Tag


PATH = "C:/Users/Vickynila/.rustup/toolchains/stable-x86_64-pc-windows-msvc/share/doc/rust/html/alloc/alloc/trait.Allocator.html"

def print_dom(element, depth=0):
    indent = "  " * depth

    if isinstance(element, Tag):
        attrs = []

        if element.get("id"):
            attrs.append(f'id="{element["id"]}"')

        if element.get("class"):
            attrs.append(f'class="{" ".join(element["class"])}"')

        attr_text = " " + " ".join(attrs) if attrs else ""

        print(f"{indent}<{element.name}{attr_text}>")

        for child in element.children:
            print_dom(child, depth + 1)


def main():
    with open(PATH, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    print_dom(soup.html)


if __name__ == "__main__":
    main()