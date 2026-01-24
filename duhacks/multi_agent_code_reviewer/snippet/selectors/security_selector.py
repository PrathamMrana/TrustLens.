from typing import List
from snippet.ir.code_block import CodeBlock

class SecuritySelector:
    """
    Selects security-relevant code blocks.
    Deterministic selection based on metadata flags and complexity.
    """

    def select(self, blocks: List[CodeBlock]) -> List[CodeBlock]:
        """
        Identify blocks with potential security risks.
        
        Rules:
        - Uses eval/exec
        - Uses SQL keywords AND complexity > 1 (to avoid simple constants)
        """
        selected = []
        
        for block in blocks:
            meta = block.metadata
            
            # Rule 1: Dangerous execution
            if meta.get("uses_eval") or meta.get("uses_exec") or meta.get("uses_dynamic_function") or meta.get("uses_reflection"):
                selected.append(block)
                continue

            # Rule 2: SQL / JDBC Interaction
            if (meta.get("uses_sql_strings") or meta.get("uses_jdbc")) and block.complexity > 1:
                selected.append(block)
                continue
            
            # Rule 3: Hardcoded Secrets
            if meta.get("uses_hardcoded_secrets"):
                selected.append(block)
                continue

        # Cap at 5 blocks to prevent Context overflow
        return selected[:5]
