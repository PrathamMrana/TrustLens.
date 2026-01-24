from typing import List, Dict, Any
from snippet.ir.code_block import CodeBlock

class QualitySelector:
    """
    Computes quality metrics from code blocks.
    does NOT return snippets, only metrics.
    """

    def compute_metrics(self, blocks: List[CodeBlock]) -> Dict[str, Any]:
        """
        Compute aggregation metrics for the file.
        
        Metrics:
        - avg_function_length
        - max_function_length
        - avg_complexity
        - max_complexity
        """
        functions = [b for b in blocks if b.type == "function"]
        
        if not functions:
            return {
                "avg_function_length": 0,
                "max_function_length": 0,
                "avg_complexity": 0,
                "max_complexity": 0,
                "function_count": 0
            }
            
        # Length metrics
        lengths = [f.length() for f in functions]
        max_len = max(lengths) if lengths else 0
        avg_len = sum(lengths) / len(lengths) if lengths else 0
        
        # Complexity metrics
        complexities = [f.complexity for f in functions]
        max_comp = max(complexities) if complexities else 0
        avg_comp = sum(complexities) / len(complexities) if complexities else 0
        
        return {
            "avg_function_length": round(avg_len, 2),
            "max_function_length": max_len,
            "avg_complexity": round(avg_comp, 2),
            "max_complexity": max_comp,
            "function_count": len(functions)
        }
