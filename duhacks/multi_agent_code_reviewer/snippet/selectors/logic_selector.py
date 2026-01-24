from typing import List
from snippet.ir.code_block import CodeBlock

class LogicSelector:
    """
    Selects interesting logic blocks for analysis.
    Focuses on complexity, recursion, and infinite loops.
    """

    def select(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """
        Identify blocks with complex logic.
        
        Rules:
        - High complexity (>= 4)
        - Recursive function
        - Infinite loop
        """
        selected = []
        
        for block in blocks:
            # Rule 1: High Cyclomatic Complexity
            if block.complexity >= 4:
                selected.append(block)
                continue
                
            # Rule 2: Recursion
            if block.type == "function" and block.metadata.get("is_recursive"):
                selected.append(block)
                continue
            
            # Rule 3: Infinite Loops
            if block.type == "loop" and block.metadata.get("is_infinite"):
                selected.append(block)
                continue

        # Sort by complexity descending to prioritize hardest parts
        selected.sort(key=lambda b: b.complexity, reverse=True)
        
        # Limit results 
        return selected[:5]
