from typing import List, Dict, Any, Optional
from tree_sitter import Node
from snippet.ir.code_block import CodeBlock
from snippet.parsers.tree_sitter_base import TreeSitterBaseParser

class JavascriptParser(TreeSitterBaseParser):
    """
    Parses JavaScript code using Tree-Sitter to extract IR CodeBlocks.
    """

    def __init__(self):
        super().__init__('javascript')

    def parse(self, code: str) -> List[CodeBlock]:
        """
        Parse JavaScript source code into IR CodeBlocks.
        
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
        
        # Iterative traversal to avoid recursion limits
        stack = [root]
        
        while stack:
            node = stack.pop()
            
            # Process current node
            block = self._process_node(node, code)
            if block:
                blocks.append(block)
                
            # Add children to stack
            for child in node.children:
                stack.append(child)
                
        return blocks

    def _process_node(self, node: Node, code: str) -> Optional[CodeBlock]:
        """Convert Tree-Sitter node to CodeBlock if relevant."""
        
        node_type = node.type
        
        # A. Functions
        if node_type in ['function_declaration', 'function_expression', 'arrow_function', 'method_definition']:
            return self._extract_function(node, code)
            
        # B. Classes
        elif node_type == 'class_declaration':
            return self._extract_class(node, code)
            
        # C. Loops
        elif node_type in ['for_statement', 'while_statement', 'do_statement']:
            return self._extract_loop(node, code)
            
        return None

    def _extract_function(self, node: Node, code: str) -> CodeBlock:
        name = self._get_function_name(node, code)
        complexity = self._compute_complexity(node)
        metadata = self._extract_security_metadata(node, code)
        metadata['is_recursive'] = self._is_recursive(node, name, code) if name else False
        
        return CodeBlock(
            type="function",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=complexity,
            language="javascript",
            metadata=metadata
        )

    def _extract_class(self, node: Node, code: str) -> CodeBlock:
        name = "anonymous_class"
        name_node = node.child_by_field_name('name')
        if name_node:
            name = self.get_node_text(name_node, code)
            
        return CodeBlock(
            type="class",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=1,
            language="javascript",
            metadata={}
        )

    def _extract_loop(self, node: Node, code: str) -> CodeBlock:
        name = "loop"
        is_infinite = False
        
        if node.type == 'while_statement':
            name = "while_loop"
            condition = node.child_by_field_name('condition')
            # Check for while(true)
            if condition:
                # Typically condition is wrapped in parens, unwrap if needed
                text = self.get_node_text(condition, code).strip('() ')
                if text == 'true':
                    is_infinite = True
                    
        elif node.type == 'for_statement':
            name = "for_loop"
            
        complexity = self._compute_complexity(node)
        
        return CodeBlock(
            type="loop",
            name=name,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            complexity=complexity,
            language="javascript",
            metadata={"is_infinite": is_infinite}
        )

    def _get_function_name(self, node: Node, code: str) -> str:
        # 1. Declaration: function foo() {}
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, code)
            
        # 2. Method: foo() {}
        if node.type == 'method_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                return self.get_node_text(name_node, code)
        
        # 3. Assignment: const foo = function() {} / () => {}
        parent = node.parent
        if parent and parent.type in ['variable_declarator', 'assignment_expression', 'pair']:
            # For variable declarator
            name_node = parent.child_by_field_name('name') or parent.child_by_field_name('left') or parent.child_by_field_name('key')
            if name_node:
                return self.get_node_text(name_node, code)
                
        return "anonymous"

    def _compute_complexity(self, node: Node) -> int:
        """
        Compute complexity by traversing subtree.
        Increment for branching and loops.
        """
        complexity = 1
        stack = [node]
        
        while stack:
            curr = stack.pop()
            
            # Nodes that increase complexity
            if curr.type in ['if_statement', 'for_statement', 'while_statement', 
                             'do_statement', 'case_clause', 'catch_clause', 'ternary_expression']:
                complexity += 1
            # Logical operators
            elif curr.type == 'binary_expression':
                # We need to check the operator text manually or assume || && increase it?
                # Tree-sitter often puts operator as a child. 
                # Better approach: check for logical_expression type which handles && ||
                pass
            elif curr.type == 'binary_expression' or curr.type == 'logical_expression':
                # In some grammars && and || are binary_expression, in others logical_expression
                # Let's check operator
                 for child in curr.children:
                    if child.type in ['&&', '||']:
                        complexity += 1
            
            # Don't double count the root function itself if we called this on a function
            if curr != node: 
                # Traverse children
                for child in curr.children:
                    # Don't enter nested functions for complexity calculation (standard practice is per-function)
                    if child.type not in ['function_declaration', 'function_expression', 'arrow_function']:
                        stack.append(child)
                        
        return complexity

    def _extract_security_metadata(self, node: Node, code: str) -> Dict[str, bool]:
        uses_eval = False
        uses_dynamic_function = False
        uses_sql = False
        uses_exec = False
        
        sql_keywords = ["SELECT ", "INSERT ", "UPDATE ", "DELETE "]
        
        stack = [node]
        while stack:
            curr = stack.pop()
            
            # 1. Check calls: eval(), exec(), child_process.exec()
            if curr.type == 'call_expression':
                # For basic calls like eval()
                func = curr.child_by_field_name('function')
                if func:
                    func_name = self.get_node_text(func, code)
                    if func_name == 'eval':
                        uses_eval = True
                    elif func_name == 'exec':
                        uses_exec = True
                    elif func_name == 'Function':
                        uses_dynamic_function = True
                
                # For member calls like child_process.exec()
                # Tree-sitter: (call_expression function: (member_expression object: (identifier) property: (property_identifier)))
                if not func and curr.children:
                    for child in curr.children:
                        if child.type == 'member_expression':
                            prop_node = child.child_by_field_name('property')
                            if prop_node and self.get_node_text(prop_node, code) == 'exec':
                                uses_exec = True
            
            # 2. Check strict new Function()
            if curr.type == 'new_expression':
                constructor = curr.child_by_field_name('constructor')
                if constructor:
                     name = self.get_node_text(constructor, code)
                     if name == 'Function':
                         uses_dynamic_function = True

            # 3. Check strings for SQL
            if curr.type == 'string':
                text = self.get_node_text(curr, code).strip('"\'`').upper()
                for key in sql_keywords:
                    if key in text:
                        uses_sql = True
                        break
            
            for child in curr.children:
                stack.append(child)
                
        return {
            "uses_eval": uses_eval,
            "uses_dynamic_function": uses_dynamic_function,
            "uses_sql_strings": uses_sql,
            "uses_exec": uses_exec
        }

    def _is_recursive(self, node: Node, func_name: str, code: str) -> bool:
        """Check if function calls itself."""
        stack = [node]
        while stack:
            curr = stack.pop()
            
            if curr.type == 'call_expression':
                func = curr.child_by_field_name('function')
                if func:
                    name = self.get_node_text(func, code)
                    if name == func_name:
                        return True
            
            for child in curr.children:
                stack.append(child)
                
        return False
