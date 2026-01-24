from typing import List, Dict, Any, Optional
from tree_sitter import Node
from snippet.ir.code_block import CodeBlock
from snippet.parsers.tree_sitter_base import TreeSitterBaseParser

class JavaParser(TreeSitterBaseParser):
    """
    Parses Java code using Tree-Sitter to extract IR CodeBlocks.
    """

    def __init__(self):
        super().__init__('java')

    def parse(self, code: str) -> List[CodeBlock]:
        """
        Parse Java source code into IR CodeBlocks.
        
        Args:
            code: Source code string
            
        Returns:
            List of CodeBlocks
        """
        root = self.parse_to_tree(code)
        if not root:
            return []
            
        return self._traverse(root, code)

    def _traverse(self, root: Node, code: str) -> List[CodeBlock]:
        blocks = []
        stack = [root]
        
        while stack:
            node = stack.pop()
            
            block = self._process_node(node, code)
            if block:
                blocks.append(block)
                
            for child in node.children:
                stack.append(child)
                
        return blocks

    def _process_node(self, node: Node, code: str) -> Optional[CodeBlock]:
        """Convert Tree-Sitter node to CodeBlock if relevant."""
        node_type = node.type
        
        # A. Classes / Interfaces / Enums
        if node_type in ['class_declaration', 'interface_declaration', 'enum_declaration']:
            return self._extract_class(node, code)
            
        # B. Methods / Constructors
        elif node_type in ['method_declaration', 'constructor_declaration']:
            return self._extract_method(node, code)
            
        # C. Loops
        elif node_type in ['for_statement', 'enhanced_for_statement', 'while_statement', 'do_statement']:
            return self._extract_loop(node, code)
            
        return None

    def _extract_class(self, node: Node, code: str) -> CodeBlock:
        name_node = node.child_by_field_name('name')
        name = self.get_node_text(name_node, code) if name_node else "anonymous_class"
        
        return CodeBlock(
            type="class",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=1,
            language="java",
            metadata={}
        )

    def _extract_method(self, node: Node, code: str) -> CodeBlock:
        name_node = node.child_by_field_name('name')
        name = self.get_node_text(name_node, code) if name_node else "constructor"
        
        complexity = self._compute_complexity(node)
        metadata = self._extract_security_metadata(node, code)
        metadata['is_recursive'] = self._is_recursive(node, name, code)
        
        return CodeBlock(
            type="function",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=complexity,
            language="java",
            metadata=metadata
        )

    def _extract_loop(self, node: Node, code: str) -> CodeBlock:
        name = "loop"
        is_infinite = False
        
        if node.type == 'while_statement':
            name = "while_loop"
            condition = node.child_by_field_name('condition')
            if condition:
                text = self.get_node_text(condition, code).strip('() ')
                if text == 'true':
                    is_infinite = True
                    
        elif node.type == 'for_statement':
            name = "for_loop"
            # distinct infinite for(;;) loop structure usually lacks init/condition/update
            # but simpler heuristic: check raw text or structure
            # Tree-sitter for loop: for ( init; cond; update )
            # If condition is missing, it's infinite
            condition = node.child_by_field_name('condition')
            if not condition:
                 # It might be infinite if it's strictly a for loop vs enhanced
                 is_infinite = True

        elif node.type == 'enhanced_for_statement':
            name = "for_each_loop"
            
        complexity = self._compute_complexity(node)
        
        return CodeBlock(
            type="loop",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=complexity,
            language="java",
            metadata={"is_infinite": is_infinite}
        )

    def _compute_complexity(self, node: Node) -> int:
        """
        Compute Cyclomatic Complexity.
        """
        complexity = 1
        stack = [node]
        
        while stack:
            curr = stack.pop()
            
            # Nodes that increase complexity
            if curr.type in ['if_statement', 'for_statement', 'enhanced_for_statement', 
                             'while_statement', 'do_statement', 'catch_clause', 
                             'ternary_expression']:
                complexity += 1
            
            # Switch cases
            elif curr.type == 'switch_label':
                # default case usually doesn't increment complexity in some standards, 
                # but 'case' definitely does. Tree-sitter 'switch_label' covers both.
                # Only strictly count 'case'
                if len(curr.children) > 0 and curr.children[0].type == 'case':
                     complexity += 1

            # Logical operators (&&, ||)
            elif curr.type == 'binary_expression':
                # Check operator
                for child in curr.children:
                     if child.type in ['&&', '||']:
                         complexity += 1
            
            if curr != node:
                # Don't recurse into nested methods/classes for this method's complexity
                if curr.type not in ['method_declaration', 'constructor_declaration', 'class_declaration']:
                    for child in curr.children:
                        stack.append(child)
                        
        return complexity

    def _extract_security_metadata(self, node: Node, code: str) -> Dict[str, bool]:
        uses_exec = False
        uses_reflection = False
        uses_jdbc = False
        uses_hardcoded_secrets = False
        
        jdbc_terms = ['Statement', 'PreparedStatement', 'executeQuery', 'executeUpdate']
        secret_terms = ['password', 'secret', 'apikey', 'token']
        
        stack = [node]
        while stack:
            curr = stack.pop()
            
            # Check for method invocations
            if curr.type == 'method_invocation':
                # Check for Runtime.getRuntime().exec() or similar
                # text usually looks like "Runtime.getRuntime().exec"
                call_text = self.get_node_text(curr, code)
                
                if ".exec" in call_text or "ProcessBuilder" in call_text:
                    uses_exec = True
                
                if "Class.forName" in call_text or ".invoke" in call_text:
                    uses_reflection = True
                
                for term in jdbc_terms:
                    if term in call_text:
                        uses_jdbc = True
            
            # Check for object creation (ProcessBuilder)
            elif curr.type == 'object_creation_expression':
                 type_node = curr.child_by_field_name('type')
                 if type_node:
                     type_name = self.get_node_text(type_node, code)
                     if "ProcessBuilder" in type_name:
                         uses_exec = True

            # Check string literals for secrets
            if curr.type == 'string_literal':
                text = self.get_node_text(curr, code).strip('"').lower()
                for secret in secret_terms:
                    if secret in text:
                        uses_hardcoded_secrets = True
                        break
            
            for child in curr.children:
                stack.append(child)
                
        return {
            "uses_exec": uses_exec,
            "uses_reflection": uses_reflection,
            "uses_jdbc": uses_jdbc,
            "uses_hardcoded_secrets": uses_hardcoded_secrets
        }

    def _is_recursive(self, node: Node, func_name: str, code: str) -> bool:
        """Check if function calls itself."""
        stack = [node]
        while stack:
            curr = stack.pop()
            
            if curr.type == 'method_invocation':
                name_node = curr.child_by_field_name('name')
                if name_node:
                    name = self.get_node_text(name_node, code)
                    if name == func_name:
                        return True
            
            for child in curr.children:
                 if child.type not in ['method_declaration', 'constructor_declaration']:
                    stack.append(child)
                
        return False
