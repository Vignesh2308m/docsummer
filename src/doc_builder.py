from __future__ import annotations

from typing import Any

from .storage import RustDocument





class RustDocumentBuilder:

    def build(
        self,
        tree: dict,
        library: str = "",
    ) -> list[RustDocument]:

        documents = []

        self._walk(
            tree,
            documents,
            library,
            None,
        )

        return documents

    def _walk(
        self,
        node,
        documents,
        library,
        parent_item,
    ):

        if isinstance(node, list):
            for child in node:
                self._walk(
                    child,
                    documents,
                    library,
                    parent_item,
                )
            return

        if not isinstance(node, dict):
            return

        attributes = node.get(
            "_attributes",
            {},
        )

        classes = set(
            attributes.get("class", [])
        )

        # ---------------------------------------------
        # Rustdoc declaration
        # ---------------------------------------------

        if "item-decl" in classes:

            document = self._build_item(
                node,
                library,
                parent_item,
            )

            if document:
                documents.append(document)

                parent_item = document.item

        # ---------------------------------------------
        # Recurse
        # ---------------------------------------------

        for key, value in node.items():

            if key.startswith("_"):
                continue

            self._walk(
                value,
                documents,
                library,
                parent_item,
            )

    def _build_item(
        self,
        node: dict,
        library: str,
        parent_item: str | None,
    ) -> RustDocument | None:

        definition = self._find_text(
            node,
            "pre",
        )

        if not definition:
            return None

        kind = self._kind(definition)
        name = self._name(definition)

        if not name:
            return None

        description = self._description(node)

        examples = self._examples(node)

        if parent_item and kind == "method":
            item = f"{parent_item}::{name}"
        else:
            item = name

        return RustDocument(
            id=f"{library}:{kind}:{item}",
            library=library,
            item=item,
            kind=kind,
            definition=definition,
            description=description,
            example=examples,
        )

    def _description(
        self,
        node: dict,
    ) -> str:

        descriptions = []

        self._find_class_text(
            node,
            "docblock",
            descriptions,
        )

        return "\n".join(
            descriptions
        ).strip()

    def _examples(
        self,
        node: dict,
    ) -> list[str]:

        examples = []

        self._find_class_text(
            node,
            "example-wrap",
            examples,
        )

        return examples

    def _find_class_text(
        self,
        node,
        class_name,
        result,
    ):

        if isinstance(node, list):
            for item in node:
                self._find_class_text(
                    item,
                    class_name,
                    result,
                )
            return

        if not isinstance(node, dict):
            return

        attributes = node.get(
            "_attributes",
            {},
        )

        classes = set(
            attributes.get("class", [])
        )

        if class_name in classes:

            text = node.get(
                "_text",
                "",
            )

            if text:
                result.append(text)

        for key, value in node.items():

            if not key.startswith("_"):
                self._find_class_text(
                    value,
                    class_name,
                    result,
                )

    @staticmethod
    def _find_text(
        node,
        tag: str,
    ) -> str:

        if isinstance(node, list):

            for item in node:
                result = RustDocumentBuilder._find_text(
                    item,
                    tag,
                )

                if result:
                    return result

            return ""

        if not isinstance(node, dict):
            return ""

        if tag in node:

            value = node[tag]

            if isinstance(value, list):
                value = value[0]

            if isinstance(value, dict):
                return value.get(
                    "_text",
                    "",
                )

        for key, value in node.items():

            if not key.startswith("_"):
                result = RustDocumentBuilder._find_text(
                    value,
                    tag,
                )

                if result:
                    return result

        return ""

    @staticmethod
    def _kind(
        definition: str,
    ) -> str:

        for rust_kind, document_kind in {
            "fn": "function",
            "struct": "struct",
            "enum": "enum",
            "trait": "trait",
            "impl": "impl",
            "type": "type",
            "const": "constant",
            "static": "static",
            "macro": "macro",
        }.items():

            if f" {rust_kind} " in definition:
                return document_kind

        return "item"

    @staticmethod
    def _name(
        definition: str,
    ) -> str:

        tokens = (
            definition
            .replace("(", " ")
            .replace("{", " ")
            .split()
        )

        keywords = {
            "pub",
            "pub(crate)",
            "pub(super)",
            "unsafe",
            "async",
            "const",
            "fn",
            "struct",
            "enum",
            "trait",
            "impl",
            "type",
            "static",
            "mod",
            "macro",
        }

        for i, token in enumerate(tokens):

            if token in keywords:
                if i + 1 < len(tokens):
                    return tokens[i + 1]

        return ""