import ast
from typing import List, Dict, Any
from snippet.ir.code_block import CodeBlock

class PythonParser:
    """
    Parses Python code using AST to extract structural analysis metrics and blocks.
    Strictly deterministic and AST-based (no regex).
    """

    def parse(self, code: str) -> List[CodeBlock]:
        """
        Parse Python source code into IR CodeBlocks.
        
        Args:
            code: Python source code string
            
        Returns:
            List of extracted CodeBlocks
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # If code isn't valid Python, we can't extract structural blocks safely
            return []

        blocks = []
        
        # Traverse top-level nodes
        for node in ast.walk(tree):
            block = self._visit_node(node)
            if block:
                blocks.append(block)
                
        return blocks

    def _visit_node(self, node: ast.AST) -> CodeBlock:
        """Process a single AST node into a CodeBlock if relevant."""
        
        # A. Function Extraction
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._extract_function(node)
            
        # B. Class Extraction
        elif isinstance(node, ast.ClassDef):
            return self._extract_class(node)
            
        # C. Loop Extraction
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            return self._extract_loop(node)
            
        return None

    def _extract_function(self, node: ast.FunctionDef) -> CodeBlock:
        """Handle function nodes."""
        complexity = self._compute_complexity(node)
        metadata = self._extract_security_metadata(node)
        metadata['is_recursive'] = self._is_recursive(node)
        
        return CodeBlock(
            type="function",
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            complexity=complexity,
            language="python",
            metadata=metadata
        )

    def _extract_class(self, node: ast.ClassDef) -> CodeBlock:
        """Handle class nodes."""
        # Classes just encompass their complexity
        # We don't typically compute cyclomatic complexity for a class itself, 
        # but could sum methods. Here we stick to structural basic info.
        return CodeBlock(
            type="class",
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            complexity=1, # Baseline
            language="python",
            metadata={}
        )

    def _extract_loop(self, node: ast.AST) -> CodeBlock:
        """Handle loop nodes (for/while)."""
        complexity = self._compute_complexity(node)
        
        # Check for infinite while loop: while True
        is_infinite = False
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                is_infinite = True
            elif isinstance(node.test, ast.NameConstant) and node.test.value is True: # Py < 3.8
                is_infinite = True

        name = "while_loop" if isinstance(node, ast.While) else "for_loop"
        
        return CodeBlock(
            type="loop",
            name=name,
            start_line=node.lineno,
            end_line=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            complexity=complexity,
            language="python",
            metadata={"is_infinite": is_infinite}
        )

    def _compute_complexity(self, node: ast.AST) -> int:
        """
        Compute Cyclomatic Complexity.
        Base = 1.
        Increment for: if, for, while, try, except, boolean ops.
        """
        complexity = 1
        for child in ast.walk(node):
            if child is node:  # Don't double count the root
                continue
                
            if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, 
                                  ast.Try, ast.ExceptHandler, 
                                  ast.BoolOp)):
                complexity += 1
                
        return complexity

    def _extract_security_metadata(self, node: ast.AST) -> Dict[str, bool]:
        """
        Detect risky calls and SQL patterns inside the node.
        """
        uses_eval = False
        uses_exec = False
        uses_sql_strings = False
        
        sql_keywords = {"SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE"}

        for child in ast.walk(node):
            # Detect calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == "eval":
                        uses_eval = True
                    elif child.func.id == "exec":
                        uses_exec = True
            
            # Detect strings (constants)
            if isinstance(child, ast.Constant):
                if isinstance(child.value, str):
                    val_upper = child.value.upper()
                    # Naive check: string starts with SQL keyword involves potential SQL (simplified)
                    # To be more robust, we look for space after kw
                    for kw in sql_keywords:
                        if f"{kw} " in val_upper:
                            uses_sql_strings = True
                            break
                            
        return {
            "uses_eval": uses_eval,
            "uses_exec": uses_exec,
            "uses_sql_strings": uses_sql_strings
        }

    def _is_recursive(self, node: ast.FunctionDef) -> bool:
        """Check if function calls itself."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id == node.name:
                        return True
        return False
