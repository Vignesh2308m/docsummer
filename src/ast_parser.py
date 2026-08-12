from __future__ import annotations

import hashlib
from pathlib import Path

import tree_sitter_rust as tsrust
from tree_sitter import Language, Parser, Node

from .storage import RustDocument


class RustASTParser:
    """
    Parse Rust source code using tree-sitter and produce RustDocument objects.

    The parser is responsible only for:
        Rust source -> RustDocument

    It does not handle:
        - embeddings
        - SQLite
        - FAISS
        - HTML ingestion
    """

    NODE_TYPES = {
        "function_item": "function",
        "struct_item": "struct",
        "enum_item": "enum",
        "trait_item": "trait",
        "impl_item": "impl",
        "type_item": "type",
        "const_item": "constant",
        "static_item": "static",
        "macro_definition": "macro",
        "mod_item": "module",
    }

    def __init__(self) -> None:
        self.language = Language(tsrust.language())
        self.parser = Parser(self.language)

    def parse(
        self,
        source: str,
        *,
        path: Path | None = None,
        library: str = "",
    ) -> list[RustDocument]:

        source_bytes = source.encode("utf-8")

        tree = self.parser.parse(source_bytes)

        documents: list[RustDocument] = []

        for node in tree.root_node.children:

            if node.type not in self.NODE_TYPES:
                continue

            kind = self.NODE_TYPES[node.type]

            if kind == "impl":
                documents.extend(
                    self._parse_impl(
                        node,
                        source,
                        source_bytes,
                        path,
                        library,
                    )
                )
            else:
                document = self._parse_item(
                    node,
                    source,
                    source_bytes,
                    path,
                    library,
                    kind,
                )

                if document:
                    documents.append(document)

        return documents

    # ---------------------------------------------------------
    # Generic Rust item
    # ---------------------------------------------------------

    def _parse_item(
        self,
        node: Node,
        source: str,
        source_bytes: bytes,
        path: Path | None,
        library: str,
        kind: str,
    ) -> RustDocument | None:

        name = self._get_name(
            node,
            source_bytes,
        )

        if not name:
            return None

        code = self._node_text(
            node,
            source_bytes,
        )

        docs = self._get_doc_comment(
            node,
            source_bytes,
        )

        signature = self._get_signature(
            node,
            source_bytes,
        )

        visibility = self._get_visibility(
            node,
            source_bytes,
        )

        return RustDocument(
            id=self._make_id(
                library,
                path,
                kind,
                name,
            ),
            library=library,
            item=name,
            kind=kind,
            definition=signature,
            description=docs,
            example=self._get_examples(
                node,
                source_bytes,
            ),
        )

    # ---------------------------------------------------------
    # impl blocks
    # ---------------------------------------------------------

    def _parse_impl(
        self,
        node: Node,
        source: str,
        source_bytes: bytes,
        path: Path | None,
        library: str,
    ) -> list[RustDocument]:

        documents: list[RustDocument] = []

        target = node.child_by_field_name("type")

        if target:
            target_name = self._node_text(
                target,
                source_bytes,
            )
        else:
            target_name = "unknown"

        trait = node.child_by_field_name("trait")

        if trait:
            trait_name = self._node_text(
                trait,
                source_bytes,
            )
            impl_name = (
                f"{trait_name} for {target_name}"
            )
        else:
            impl_name = target_name

        # -----------------------------------------------------
        # Create document for the impl block itself
        # -----------------------------------------------------

        impl_code = self._node_text(
            node,
            source_bytes,
        )

        documents.append(
            RustDocument(
                id=self._make_id(
                    library,
                    path,
                    "impl",
                    impl_name,
                ),
                library=library,
                item=impl_name,
                kind="impl",
                definition=self._get_signature(
                    node,
                    source_bytes,
                ),
                description=self._get_doc_comment(
                    node,
                    source_bytes,
                ),
                example=[],
            )
        )

        # -----------------------------------------------------
        # Extract methods/functions inside impl
        # -----------------------------------------------------

        body = node.child_by_field_name("body")

        if not body:
            return documents

        for child in body.children:

            if child.type != "function_item":
                continue

            method = self._parse_item(
                child,
                source,
                source_bytes,
                path,
                library,
                "method",
            )

            if not method:
                continue

            # Make method identity unambiguous.
            method.item = (
                f"{target_name}::{method.item}"
            )

            method.id = self._make_id(
                library,
                path,
                "method",
                method.item,
            )

            documents.append(method)

        return documents

    # ---------------------------------------------------------
    # Name extraction
    # ---------------------------------------------------------

    def _get_name(
        self,
        node: Node,
        source_bytes: bytes,
    ) -> str | None:

        name_node = node.child_by_field_name("name")

        if name_node:
            return self._node_text(
                name_node,
                source_bytes,
            )

        # Some nodes have special naming structures.
        if node.type == "impl_item":

            type_node = node.child_by_field_name(
                "type"
            )

            if type_node:
                return self._node_text(
                    type_node,
                    source_bytes,
                )

        return None

    # ---------------------------------------------------------
    # Signature
    # ---------------------------------------------------------

    def _get_signature(
        self,
        node: Node,
        source_bytes: bytes,
    ) -> str:

        body = node.child_by_field_name("body")

        if body:
            start = node.start_byte
            end = body.start_byte

            return source_bytes[
                start:end
            ].decode("utf-8").strip()

        return self._node_text(
            node,
            source_bytes,
        ).strip()

    # ---------------------------------------------------------
    # Visibility
    # ---------------------------------------------------------

    def _get_visibility(
        self,
        node: Node,
        source_bytes: bytes,
    ) -> str:

        visibility = node.child_by_field_name(
            "visibility"
        )

        if not visibility:
            return "private"

        return self._node_text(
            visibility,
            source_bytes,
        )

    # ---------------------------------------------------------
    # Documentation comments
    # ---------------------------------------------------------

    def _get_doc_comment(
        self,
        node: Node,
        source_bytes: bytes,
    ) -> str:

        parent = node.parent

        if not parent:
            return ""

        siblings = parent.children

        try:
            index = siblings.index(node)
        except ValueError:
            return ""

        comments: list[str] = []

        for sibling in reversed(
            siblings[:index]
        ):

            if sibling.type != "line_comment":
                break

            text = self._node_text(
                sibling,
                source_bytes,
            )

            if text.startswith("///"):
                comments.append(
                    text[3:].strip()
                )
                continue

            break

        comments.reverse()

        return "\n".join(comments)

    # ---------------------------------------------------------
    # Examples
    # ---------------------------------------------------------

    def _get_examples(
        self,
        node: Node,
        source_bytes: bytes,
    ) -> list[str]:

        examples: list[str] = []

        for child in node.children:

            if child.type != "line_comment":
                continue

            text = self._node_text(
                child,
                source_bytes,
            )

            if "```" in text:
                examples.append(text)

        return examples

    # ---------------------------------------------------------
    # Exact source extraction
    # ---------------------------------------------------------

    @staticmethod
    def _node_text(
        node: Node,
        source_bytes: bytes,
    ) -> str:

        return source_bytes[
            node.start_byte:node.end_byte
        ].decode("utf-8")

    # ---------------------------------------------------------
    # Stable document ID
    # ---------------------------------------------------------

    @staticmethod
    def _make_id(
        library: str,
        path: Path | None,
        kind: str,
        name: str,
    ) -> str:

        path_string = (
            str(path)
            if path
            else ""
        )

        value = (
            f"{library}:"
            f"{path_string}:"
            f"{kind}:"
            f"{name}"
        )

        return hashlib.sha1(
            value.encode("utf-8")
        ).hexdigest()