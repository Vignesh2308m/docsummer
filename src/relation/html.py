TAG_ROLES = {
    # Document structure
    "html": "DOCUMENT",
    "head": "METADATA_CONTAINER",
    "body": "CONTAINER",
    "main": "CONTAINER",
    "section": "CONTAINER",
    "div": "CONTAINER",
    "nav": "CONTAINER",
    "rustdoc-topbar": "CONTAINER",
    "rustdoc-toolbar": "CONTAINER",

    # Metadata
    "meta": "METADATA",
    "title": "METADATA",
    "script": "METADATA",
    "link": "REFERENCE",
    "noscript": "METADATA",

    # Headings
    "h1": "HEADING",
    "h2": "HEADING",
    "h3": "HEADING",
    "h4": "HEADING",
    "h5": "HEADING",
    "h6": "HEADING",

    # Text
    "p": "TEXT",
    "span": "TEXT",
    "em": "TEXT",
    "b": "TEXT",
    "i": "TEXT",
    "strong": "TEXT",
    "sup": "TEXT",
    "sub": "TEXT",
    "blockquote": "TEXT",

    # References
    "a": "REFERENCE",

    # Code
    "pre": "CODE_CONTAINER",
    "code": "CODE",

    # Lists
    "ul": "LIST",
    "ol": "LIST",
    "li": "LIST_ITEM",

    # Definition lists
    "dl": "LIST",
    "dt": "LIST_ITEM",
    "dd": "TEXT",

    # Tables
    "table": "TABLE",
    "thead": "TABLE_SECTION",
    "tbody": "TABLE_SECTION",
    "tr": "TABLE_ROW",
    "th": "TABLE_CELL",
    "td": "TABLE_CELL",

    # Collapsible
    "details": "CONTAINER",
    "summary": "HEADING",

    # Media
    "img": "MEDIA",
    "svg": "MEDIA",
    "path": "MEDIA_CONTENT",

    # UI
    "button": "ACTION",

    # Separators / formatting
    "hr": "SEPARATOR",
    "br": "SEPARATOR",
    "wbr": "SEPARATOR",
}

ID_RELATIONS = {
    "equals": {
        # Page structure
        "main-content": "MAIN_CONTENT",
        "copy-path": "COPY_PATH",

        # Sections
        "required-methods": "REQUIRED_METHODS",
        "provided-methods": "PROVIDED_METHODS",
        "implementors": "IMPLEMENTORS",
        "implementors-list": "IMPLEMENTORS_LIST",
        "trait-implementations": "TRAIT_IMPLEMENTATIONS",
        "trait-implementations-list": "TRAIT_IMPLEMENTATIONS_LIST",

        # Documentation sections
        "examples": "EXAMPLES",
        "safety": "SAFETY",
        "errors": "ERRORS",
    },

    "startswith": {
        # Rust semantic entities
        "method.": "METHOD",
        "tymethod.": "REQUIRED_METHOD",
        "impl-": "IMPLEMENTATION",
        "variant.": "VARIANT",
        "structfield.": "STRUCT_FIELD",
        "associatedconstant.": "ASSOCIATED_CONSTANT",
        "associatedtype.": "ASSOCIATED_TYPE",
        "reexport.": "REEXPORT",
    }
}

CLASS_ROLES = {
    # Rust entities
    "fn": "FUNCTION",
    "struct": "STRUCT",
    "trait": "TRAIT",
    "enum": "ENUM",
    "type": "TYPE",
    "primitive": "PRIMITIVE",
    "union": "UNION",
    "macro": "MACRO",
    "constant": "CONSTANT",
    "derive": "DERIVE",
    "traitalias": "TRAIT_ALIAS",
    "keyword": "KEYWORD",
    "mod": "MODULE",

    # Rust members
    "method": "METHOD",
    "associatedtype": "ASSOCIATED_TYPE",
    "associatedconstant": "ASSOCIATED_CONSTANT",
    "structfield": "STRUCT_FIELD",
    "variant": "VARIANT",

    # Structural semantics
    "main-heading": "MAIN_HEADING",
    "sub-heading": "SUB_HEADING",
    "section-header": "SECTION_HEADER",
    "item-table": "ITEM_TABLE",
    "item-info": "ITEM_INFO",
    "item-decl": "ITEM_DECLARATION",
    "impl-items": "IMPLEMENTATION_ITEMS",
    "methods": "METHODS",

    # Documentation
    "docblock": "DOCUMENTATION",
    "doccomment": "DOCUMENTATION",
    "example-wrap": "EXAMPLE",
    "footnotes": "FOOTNOTES",

    # Implementation
    "impl": "IMPLEMENTATION",
    "trait-implementation": "TRAIT_IMPLEMENTATION",
    "synthetic-implementation": "SYNTHETIC_IMPLEMENTATION",
    "blanket-implementation": "BLANKET_IMPLEMENTATION",
    "negative-marker": "NEGATIVE_IMPLEMENTATION",

    # Code
    "code-header": "CODE_HEADER",
    "code-attribute": "CODE_ATTRIBUTE",
    "where": "WHERE_CLAUSE",
    "lifetime": "LIFETIME",
    "attr": "ATTRIBUTE",
    "comment": "COMMENT",
    "string": "STRING",
    "number": "NUMBER",

    # References
    "anchor": "ANCHOR",
    "doc-anchor": "DOCUMENTATION_ANCHOR",
    "src": "SOURCE",
    "location": "LOCATION",

    # Metadata
    "since": "VERSION",
    "stab": "STABILITY",
    "deprecated": "DEPRECATED",
    "unstable": "UNSTABLE",
    "portability": "PORTABILITY",

    # UI / containers
    "content": "CONTAINER",
    "block": "BLOCK",
    "width-limiter": "CONTAINER",
    "sidebar": "SIDEBAR",
    "rightside": "SIDEBAR",
    "toggle": "TOGGLE",
}