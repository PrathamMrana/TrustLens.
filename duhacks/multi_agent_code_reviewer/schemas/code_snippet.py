"""
Code Snippet Schema
Represents a curated code snippet for agent analysis.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CodeSnippet:
    """
    Represents a relevant code snippet extracted for analysis.
    Contains context and metadata to help agents understand the code.
    """
    filename: str
    start_line: int
    end_line: int
    content: str
    context: str  # function/class name or description
    relevance_score: float  # 0.0 to 1.0
    tags: List[str]  # e.g., ['sql', 'auth', 'crypto', 'loop', 'complexity']
    
    def __post_init__(self):
        """Validate snippet data"""
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("relevance_score must be between 0.0 and 1.0")
        
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
    
    def get_location(self) -> str:
        """Get human-readable location string"""
        return f"{self.filename}:{self.start_line}-{self.end_line}"
    
    def get_size(self) -> int:
        """Get snippet size in characters"""
        return len(self.content)
    
    def has_tag(self, tag: str) -> bool:
        """Check if snippet has a specific tag"""
        return tag.lower() in [t.lower() for t in self.tags]
