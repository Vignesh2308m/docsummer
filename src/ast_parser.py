from dataclasses import dataclass
from typing import List
import tree_sitter_rust as tsrust
from tree_sitter import Language, Parser, Node

@dataclass
class RustASTChunk:
    symbol_name: str
    symbol_type: str  # function_item, struct_item, impl_item, trait_item
    code: str
    start_line: int
    end_line: int

class RustASTChunker:
    def __init__(self):
        # Initialize tree-sitter Rust parser
        self.language = Language(tsrust.language())
        self.parser = Parser(self.language)

    def chunk_code(self, source_code: str) -> List[RustASTChunk]:
        tree = self.parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node
        
        chunks = []
        
        # Top-level item types to extract as standalone chunks
        target_types = {
            "function_item": "Function",
            "struct_item": "Struct",
            "enum_item": "Enum",
            "trait_item": "Trait",
            "impl_item": "Impl Block"
        }

        lines = source_code.splitlines()

        for child in root.children:
            if child.type in target_types:
                # Get the name identifier node
                name_node = child.child_by_field_name("name")
                
                # For `impl` blocks, extract the trait/type name being implemented
                if child.type == "impl_item":
                    type_node = child.child_by_field_name("type")
                    symbol_name = source_code[type_node.start_byte:type_node.end_byte] if type_node else "impl"
                elif name_node:
                    symbol_name = source_code[name_node.start_byte:name_node.end_byte]
                else:
                    symbol_name = "anonymous"

                start_line = child.start_point.row
                end_line = child.end_point.row
                
                # Extract chunk exact string including inner/outer doc comments
                chunk_code = "\n".join(lines[start_line:end_line + 1])

                chunks.append(RustASTChunk(
                    symbol_name=symbol_name,
                    symbol_type=target_types[child.type],
                    code=chunk_code,
                    start_line=start_line + 1,
                    end_line=end_line + 1
                ))

        return chunks

# --- Quick Test ---
if __name__ == "__main__":
    rust_code = '''
    /// Calculates the dot product of two vectors
    pub fn dot_product(a: &[f32], b: &[f32]) -> f32 {
        a.iter().zip(b).map(|(x, y)| x * y).sum()
    }

    /// Representation of a 3D Point
    pub struct Point3D {
        pub x: f32,
        pub y: f32,
        pub z: f32,
    }

    impl Point3D {
        pub fn new(x: f32, y: f32, z: f32) -> Self {
            Self { x, y, z }
        }
    }
    '''

    chunker = RustASTChunker()
    chunks = chunker.chunk_code(rust_code)

    for c in chunks:
        print(f"[{c.symbol_type}] {c.symbol_name} (Lines {c.start_line}-{c.end_line})")
        print("```rust")
        print(c.code)
        print("```\n")