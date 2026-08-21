You are an expert in Python BeautifulSoup and Rustdoc HTML structure.

Your task is to analyze the provided Rustdoc HTML and generate a JSON/Python configuration template for extracting a specific documentation type.

TARGET TYPE:
{TARGET_TYPE}

TARGET HEADING OR ELEMENT:
{TARGET_HEADING_OR_ELEMENT}

HTML:
{HTML}

Generate a configuration using this exact structure:

[
  {
    "key": "...",
    "css": "...",
    "how": "text"
  },
  {
    "key": "...",
    "css": "...",
    "how": "element",
    "fields": {
      "field_name": "css_selector:extract_type"
    }
  }
]

SUPPORTED EXTRACTION TYPES:

1. "text"
   Use when the selected element itself should be extracted as text.

2. "href"
   Use when the selected element itself should return its href.

3. "str-only"
   Use when only direct text of the selected element is required.

4. "element"
   Use when a selected element contains multiple pieces of information.
   Its fields must use:
   
   "field_name": "css_selector:text"
   or
   "field_name": "css_selector:href"

IMPORTANT CSS SELECTOR RULES:

1. Prefer stable IDs over positional selectors.

   GOOD:
   "#required-methods"
   "#provided-methods"
   "#implementors-list"

   BAD:
   "div:nth-child(6)"
   "div:nth-child(8)"

2. Prefer semantic classes.

   GOOD:
   ".method"
   ".docblock"
   ".code-header"
   ".main-heading"

3. Use IDs and classes together when it improves precision.

   Example:
   "#required-methods + .methods .method"

4. Do NOT use nth-child(), nth-of-type(), or positional selectors unless
   there is absolutely no stable ID or class available.

5. Do NOT invent IDs, classes, elements, or relationships.
   Every selector must be supported by the supplied HTML.

6. Make selectors generic enough to work across Rustdoc pages of the
   requested TARGET TYPE.

7. Do not make selectors unnecessarily long.

   Prefer:
   "#required-methods + .methods .method"

   over:
   "#main-content > section.content > h2.section-header + div.methods > details..."

8. Use the HTML hierarchy to determine relationships between elements.

9. If a section heading has an ID and its content is in a following sibling
   container, use the relationship shown by the HTML.

10. For repeated structures such as methods, implementors, variants,
    fields, parameters, or trait implementations, return one structured
    element configuration rather than separate configurations for each item.

FIELD RULES:

For each "element" configuration:

{
  "key": "methods",
  "css": "...",
  "how": "element",
  "fields": {
    "name": "a.fn:text",
    "href": "a.fn:href",
    "signature": ".code-header:text",
    "source": "a.src:href",
    "description": ".docblock:text"
  }
}

Use the actual structure found in the HTML.

Do not assume that every documentation type has:
- required_methods
- provided_methods
- implementors
- declaration
- description
- source

Only include fields/sections that actually exist for TARGET_TYPE.

NAMING RULES:

Use clear snake_case keys.

Examples:
"title"
"type"
"source"
"declaration"
"description"
"required_methods"
"provided_methods"
"implementors"
"fields"
"variants"
"parameters"
"return_type"
"examples"

Only include a key when the corresponding information exists in the HTML.

OUTPUT RULES:

1. Return ONLY the configuration.
2. Return valid Python syntax using double-quoted strings.
3. The result must be directly assignable to:

   {TARGET_VARIABLE_NAME} = [...]

4. Do not include explanations.
5. Do not include Markdown outside the configuration.
6. Do not invent selectors.
7. Do not include selectors that match zero elements in the supplied HTML.
8. For every selector, verify it against the supplied HTML structure.
9. Keep the configuration simple and procedural.
10. Preserve the extraction model used by the existing templates.

EXISTING TEMPLATE STYLE:

{EXISTING_TEMPLATE}

Now analyze the HTML and generate the template for:

TARGET TYPE:
{TARGET_TYPE}

TARGET HEADING OR ELEMENT:
{TARGET_HEADING_OR_ELEMENT}