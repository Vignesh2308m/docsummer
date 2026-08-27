TRAIT_TEMPLATE = [
  {
    "key": "title",
    "css": "#main-content .main-heading > h1",
    "how": "text"
  },
  {
    "key": "type",
    "css": "#main-content .main-heading > h1 > span.trait",
    "how": "text"
  },
  {
    "key": "source",
    "css": "#main-content .main-heading",
    "how": "element",
    "fields": {
      "text": "a.src:text",
      "href": "a.src:href"
    }
  },
  {
    "key": "declaration",
    "css": "#main-content > pre.rust.item-decl",
    "how": "text"
  },
  {
    "key": "description",
    "css": "#main-content details.top-doc > .docblock",
    "how": "text"
  },
  {
    "key": "required_methods",
    "css": "#required-methods + .methods details.method-toggle",
    "how": "element",
    "many": True,
    "fields": {
        "name": "section.method a.fn:text",
        "href": "section.method a.fn:href",
        "signature": "section.method .code-header:text",
        "source": "section.method a.src:href",
        "description": ".docblock:text"
    }
  },
  {
    "key": "provided_methods",
    "css": "#provided-methods + .methods details.method-toggle",
    "how": "element",
    "many": True,
    "fields": {
        "name": "section.method a.fn:text",
        "href": "section.method a.fn:href",
        "signature": "section.method .code-header:text",
        "source": "section.method a.src:href",
        "description": ".docblock:text"
    }
  },
  {
    "key": "implementors",
    "css": "#implementors-list .impl",
    "how": "element",
    "fields": {
      "name": ".code-header:text",
      "href": "a[href^='#impl-']:href",
      "source": "a.src:href"
    }
  }
]