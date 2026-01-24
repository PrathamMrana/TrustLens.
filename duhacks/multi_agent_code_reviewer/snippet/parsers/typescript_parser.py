from typing import List, Dict, Any, Optional
from tree_sitter import Node
from snippet.ir.code_block import CodeBlock
from snippet.parsers.javascript_parser import JavascriptParser
import tree_sitter_typescript

class TypescriptParser(JavascriptParser):
    """
    Parses TypeScript code using Tree-Sitter.
    Inherits JS logic but handles TS-specific constructs.
    """

    def __init__(self):
        # Initialize with typescript grammar directly
        # We bypass JavascriptParser.__init__ but use its methods
        from snippet.parsers.tree_sitter_base import TreeSitterBaseParser
        TreeSitterBaseParser.__init__(self, 'typescript')

    def _process_node(self, node: Node, code: str) -> Optional[CodeBlock]:
        """Convert Tree-Sitter node to CodeBlock (TS Extensions)."""
        
        node_type = node.type
        
        # A. Interfaces / Types
        if node_type in ['interface_declaration', 'type_alias_declaration']:
            return self._extract_type_def(node, code)
            
        # Delegate to Javascript logic for functions/classes/loops
        # This works because TS grammar is a superset and node names often overlap
        return super()._process_node(node, code)

    def _extract_type_def(self, node: Node, code: str) -> CodeBlock:
        name_node = node.child_by_field_name('name')
        name = self.get_node_text(name_node, code) if name_node else "anonymous_type"
        
        return CodeBlock(
            type="type",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=1, # Types don't have cyclomatic complexity
            language="typescript",
            metadata={}
        )

    # Note: _extract_function, _extract_class etc are inherited.
    # TypeScript grammar produces 'method_definition', 'class_declaration' just like JS.
    # The complexity calculation relies on traversing children, which works fine for TS too.
