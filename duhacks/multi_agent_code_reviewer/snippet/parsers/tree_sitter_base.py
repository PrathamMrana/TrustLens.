from typing import List, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_java

class TreeSitterBaseParser:
    """
    Base class for Tree-Sitter parsers.
    Handles parser initialization and tree parsing.
    """

    def __init__(self, language_name: str):
        """
        Initialize the parser with the specific language grammar.
        
        Args:
            language_name: 'javascript', 'typescript', or 'java'
        """
        self.parser = Parser()
        
        try:
            lang = None
            if language_name == 'javascript':
                lang = Language(tree_sitter_javascript.language())
            elif language_name == 'typescript':
                # Resilient loading for different versions of tree-sitter-typescript
                for attr in ['language', 'language_typescript', 'typescript']:
                    if hasattr(tree_sitter_typescript, attr):
                        lang = Language(getattr(tree_sitter_typescript, attr)())
                        break
                if not lang:
                    raise AttributeError("Could not find language function in tree_sitter_typescript")
            elif language_name == 'java':
                lang = Language(tree_sitter_java.language())
            
            if not lang:
                raise ValueError(f"Language {language_name} not properly loaded")
                
            try:
                # Try new API (0.22+)
                self.parser = Parser(lang)
            except (TypeError, AttributeError):
                # Fallback to old API (<0.22)
                self.parser = Parser()
                self.parser.set_language(lang)
            
        except Exception as e:
            # Fallback for environments where compilation fails
            print(f"Failed to load TreeSitter grammar for {language_name}: {e}")
            self.parser = None

    def parse_to_tree(self, code: str) -> Optional[Node]:
        """
        Parse source code string into a Tree-Sitter tree.
        
        Args:
            code: Source code string
            
        Returns:
            Root node of the parsed tree or None if failed
        """
        if not self.parser:
            return None
            
        try:
            # Tree-Sitter expects bytes
            tree = self.parser.parse(bytes(code, "utf8"))
            return tree.root_node
        except Exception as e:
            print(f"TreeSitter parsing failed: {e}")
            return None

    def get_node_text(self, node: Node, code: str) -> str:
        """Helper to get text content of a node."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        return code.encode("utf8")[start_byte:end_byte].decode("utf8")
