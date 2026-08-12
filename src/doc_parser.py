import re
import sys
from pathlib import Path
 
try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit(
        "This script requires BeautifulSoup4.\n"
        "Install with: pip install beautifulsoup4 --break-system-packages"
    )
 
 
def extract_title(soup):
    """Grab the page <title>."""
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None
 
 
def extract_description(soup):
    """Grab the <meta name="description"> content."""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()
    return None
 
 
def extract_docblocks(soup):
    """
    Extract prose documentation text (rustdoc wraps explanatory text in
    <div class="docblock">). Code inside <pre> tags is skipped here since
    it's captured separately by extract_code_blocks().
    """
    docblocks = []
    for db in soup.find_all("div", class_="docblock"):
        text_parts = []
        for child in db.find_all(["p", "h5", "li"], recursive=True):
            if child.find_parent("pre"):
                continue
            txt = child.get_text(" ", strip=True)
            if txt:
                text_parts.append(txt)
        if text_parts:
            docblocks.append(" ".join(text_parts))
    return docblocks
 
 
def extract_code_blocks(soup):
    """
    Extract all Rust code blocks:
      - item-decl:   the top-of-page signature (struct/enum/trait/fn/macro/...)
      - method-sig:  signatures of individual methods/associated items, which
                     rustdoc renders as <h4 class="code-header"> rather than
                     inside the top <pre class="item-decl"> (present on
                     struct/enum/trait pages with methods or impls)
      - example:     rendered usage examples from doc comments
    """
    code_blocks = []
 
    # The main item declaration (trait/struct/fn signature block at the top)
    for decl in soup.find_all("pre", class_=re.compile(r"item-decl")):
        code_blocks.append({"type": "item-decl", "code": decl.get_text().strip()})
 
    # Individual method / associated-item signatures (methods, impl blocks, etc.)
    for header in soup.find_all("h4", class_=re.compile(r"code-header")):
        text = header.get_text(" ", strip=True)
        if text:
            code_blocks.append({"type": "method-sig", "code": text})
 
    # Example code blocks (inside "Examples" sections)
    for example in soup.find_all("pre", class_=re.compile(r"rust-example-rendered")):
        code_blocks.append({"type": "example", "code": example.get_text().strip()})
 
    return code_blocks
 
 
def extract_references(soup):
    """
    Extract links pointing to other documents/pages, classified as:
      - doc:      links to other local HTML doc pages
      - external: absolute http(s) links (e.g. playground links)
      - other:    everything else (e.g. .js/.css asset links used as hrefs)
    Pure in-page anchors (#foo) and javascript:/mailto: links are skipped.
    """
    references = []
    seen = set()
 
    for a in soup.find_all("a", href=True):
        href = a["href"]
 
        if href.startswith("#") or href.startswith(("javascript:", "mailto:")):
            continue
 
        text = a.get_text(" ", strip=True)
 
        if href.startswith(("http://", "https://")):
            ref_type = "external"
        elif ".html" in href:
            ref_type = "doc"
        else:
            ref_type = "other"
 
        key = (href, text)
        if key in seen:
            continue
        seen.add(key)
 
        references.append({"text": text, "href": href, "type": ref_type})
 
    return references
 
 
def extract_implementors(soup):
    """Rustdoc-specific bonus: list types that implement this trait, if any."""
    implementors = []
    impl_list = soup.find("div", id="implementors-list")
    if not impl_list:
        return implementors
 
    for section in impl_list.find_all("section", class_="impl"):
        header = section.find("h3", class_="code-header")
        if header:
            implementors.append(header.get_text(" ", strip=True))
 
    return implementors
 
 
def extract_all(html_path):
    html_path = Path(html_path)
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
 
    return {
        "title": extract_title(soup),
        "description": extract_description(soup),
        "docblocks": extract_docblocks(soup),
        "code_blocks": extract_code_blocks(soup),
        "references": extract_references(soup),
        "implementors": extract_implementors(soup),
    }