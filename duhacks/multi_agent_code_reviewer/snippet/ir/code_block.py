from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class CodeBlock:
    """
    Intermediate Representation (IR) of a code block.
    Normalizes structure across languages.
    """
    type: str                # "function", "class", "loop"
    name: str                # function/class name or empty
    start_line: int          # 1-indexed inclusive
    end_line: int            # 1-indexed inclusive
    complexity: int          # cyclomatic complexity estimate
    language: str            # "python", "javascript", etc.
    metadata: Dict[str, Any] = field(default_factory=dict) # e.g. {"uses_eval": True}

    def length(self) -> int:
        return self.end_line - self.start_line + 1
