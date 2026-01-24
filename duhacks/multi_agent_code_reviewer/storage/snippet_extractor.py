"""
Snippet Extractor
Extracts relevant code snippets for agent analysis.
"""

import re
from typing import Dict, List, Any
from schemas.code_snippet import CodeSnippet
from utils.logger import Logger


class SnippetExtractor:
    """
    Extracts curated code snippets based on analysis type.
    Prevents agents from seeing full codebase.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize snippet extractor.
        
        Args:
            config: Configuration dict with max_snippet_length, etc.
        """
        self.config = config or {}
        self.logger = Logger("SnippetExtractor")
        self.max_snippet_length = self.config.get("max_snippet_length", 500)
        self.max_snippets_per_type = self.config.get("max_snippets_per_type", 20)
    
    def extract_all(self, code_files: Dict[str, str], features: Dict[str, Any]) -> Dict[str, List[CodeSnippet]]:
        """
        Extract all snippet types.
        
        Args:
            code_files: Dictionary of {filename: content}
            features: Raw features from FeatureExtractionAgent
        
        Returns:
            Dictionary with keys: 'security', 'logic', 'quality'
        """
        return {
            'security': self.extract_security_snippets(code_files, features),
            'logic': self.extract_logic_snippets(code_files, features),
            'quality': self.extract_quality_snippets(code_files, features)
        }
    
    def extract_security_snippets(self, code_files: Dict[str, str], features: Dict[str, Any]) -> List[CodeSnippet]:
        """
        Extract security-relevant code snippets.
        
        Args:
            code_files: All code files
            features: Extracted features
        
        Returns:
            List of security-relevant snippets
        """
        snippets = []
        
        # Security keywords to look for
        security_patterns = {
            'sql': (r'(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)\s+', ['sql', 'injection']),
            'auth': (r'(password|token|authenticate|login|session)', ['auth', 'authentication']),
            'crypto': (r'(encrypt|decrypt|hash|crypto|cipher)', ['crypto', 'encryption']),
            'exec': (r'(eval|exec|compile|__import__)', ['code_execution', 'dangerous']),
            'pickle': (r'pickle\.(load|loads|dump|dumps)', ['deserialization', 'dangerous']),
            'path': (r'(open|read|write)\s*\(.*\+', ['path_traversal', 'file_access']),
        }
        
        for filename, content in code_files.items():
            lines = content.split('\n')
            
            for pattern_name, (pattern, tags) in security_patterns.items():
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Extract snippet with context
                    snippet_content, start_line, end_line = self._extract_context_lines(
                        lines, line_num, self.max_snippet_length
                    )
                    
                    # Get function/class context
                    context = self._find_context(lines, line_num)
                    
                    # Calculate relevance score
                    relevance = self._calculate_security_relevance(snippet_content, tags)
                    
                    snippets.append(CodeSnippet(
                        filename=filename,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        context=context,
                        relevance_score=relevance,
                        tags=['security'] + tags
                    ))
        
        # Sort by relevance and limit
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:self.max_snippets_per_type]
    
    def extract_logic_snippets(self, code_files: Dict[str, str], features: Dict[str, Any]) -> List[CodeSnippet]:
        """
        Extract logic-relevant code snippets.
        
        Args:
            code_files: All code files
            features: Extracted features
        
        Returns:
            List of logic-relevant snippets
        """
        snippets = []
        
        # Logic patterns to look for
        logic_patterns = {
            'loop': (r'(while|for)\s+', ['loop', 'iteration']),
            'conditional': (r'if\s+.*:', ['conditional', 'branching']),
            'recursion': (r'def\s+(\w+).*:\s*.*\1\s*\(', ['recursion', 'complexity']),
        }
        
        for filename, content in code_files.items():
            lines = content.split('\n')
            
            # Extract complex control flow
            for pattern_name, (pattern, tags) in logic_patterns.items():
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Check nesting depth at this line
                    nesting = self._calculate_nesting_at_line(lines, line_num)
                    
                    # Only extract if complex enough
                    if nesting >= 2 or pattern_name == 'recursion':
                        snippet_content, start_line, end_line = self._extract_context_lines(
                            lines, line_num, self.max_snippet_length
                        )
                        
                        context = self._find_context(lines, line_num)
                        relevance = min(1.0, nesting / 5.0 + 0.3)  # Higher nesting = more relevant
                        
                        snippets.append(CodeSnippet(
                            filename=filename,
                            start_line=start_line,
                            end_line=end_line,
                            content=snippet_content,
                            context=context,
                            relevance_score=relevance,
                            tags=['logic'] + tags + [f'nesting_{nesting}']
                        ))
        
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:self.max_snippets_per_type]
    
    def extract_quality_snippets(self, code_files: Dict[str, str], features: Dict[str, Any]) -> List[CodeSnippet]:
        """
        Extract quality-relevant code snippets.
        
        Args:
            code_files: All code files
            features: Extracted features
        
        Returns:
            List of quality-relevant snippets
        """
        snippets = []
        
        for filename, content in code_files.items():
            lines = content.split('\n')
            
            # Find long functions
            function_pattern = r'(def|function)\s+(\w+)\s*\('
            matches = list(re.finditer(function_pattern, content))
            
            for i, match in enumerate(matches):
                func_name = match.group(2)
                start_line = content[:match.start()].count('\n') + 1
                
                # Find function end (next function or end of file)
                if i + 1 < len(matches):
                    end_line = content[:matches[i + 1].start()].count('\n')
                else:
                    end_line = len(lines)
                
                func_length = end_line - start_line + 1
                
                # Extract if function is long
                if func_length > 30:  # Threshold for long function
                    snippet_content, snippet_start, snippet_end = self._extract_context_lines(
                        lines, start_line, self.max_snippet_length
                    )
                    
                    relevance = min(1.0, func_length / 100.0)
                    
                    snippets.append(CodeSnippet(
                        filename=filename,
                        start_line=snippet_start,
                        end_line=snippet_end,
                        content=snippet_content,
                        context=f"function {func_name} ({func_length} lines)",
                        relevance_score=relevance,
                        tags=['quality', 'long_function', f'length_{func_length}']
                    ))
            
            # Find deeply nested code
            for line_num, line in enumerate(lines, 1):
                nesting = self._calculate_nesting_at_line(lines, line_num)
                
                if nesting >= 4:  # Deep nesting threshold
                    snippet_content, start_line, end_line = self._extract_context_lines(
                        lines, line_num, self.max_snippet_length
                    )
                    
                    context = self._find_context(lines, line_num)
                    relevance = min(1.0, nesting / 6.0)
                    
                    snippets.append(CodeSnippet(
                        filename=filename,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        context=context,
                        relevance_score=relevance,
                        tags=['quality', 'deep_nesting', f'nesting_{nesting}']
                    ))
        
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:self.max_snippets_per_type]
    
    def _extract_context_lines(self, lines: List[str], target_line: int, max_chars: int) -> tuple:
        """
        Extract lines around target line up to max_chars.
        
        Args:
            lines: All lines in file
            target_line: Target line number (1-indexed)
            max_chars: Maximum characters to extract
        
        Returns:
            Tuple of (content, start_line, end_line)
        """
        # Start from target line and expand
        start = target_line - 1  # Convert to 0-indexed
        end = target_line
        
        current_chars = len(lines[start]) if start < len(lines) else 0
        
        # Expand up and down
        while current_chars < max_chars:
            expanded = False
            
            # Try to add line above
            if start > 0:
                new_chars = current_chars + len(lines[start - 1]) + 1  # +1 for newline
                if new_chars <= max_chars:
                    start -= 1
                    current_chars = new_chars
                    expanded = True
            
            # Try to add line below
            if end < len(lines):
                new_chars = current_chars + len(lines[end]) + 1
                if new_chars <= max_chars:
                    end += 1
                    current_chars = new_chars
                    expanded = True
            
            if not expanded:
                break
        
        content = '\n'.join(lines[start:end])
        return content, start + 1, end  # Convert back to 1-indexed
    
    def _find_context(self, lines: List[str], line_num: int) -> str:
        """
        Find function/class context for a line.
        
        Args:
            lines: All lines in file
            line_num: Line number (1-indexed)
        
        Returns:
            Context string (e.g., "function authenticate_user")
        """
        # Search backwards for function/class definition
        for i in range(line_num - 1, max(0, line_num - 50), -1):
            line = lines[i].strip()
            
            # Check for function
            func_match = re.match(r'(def|function)\s+(\w+)', line)
            if func_match:
                return f"function {func_match.group(2)}"
            
            # Check for class
            class_match = re.match(r'class\s+(\w+)', line)
            if class_match:
                return f"class {class_match.group(1)}"
        
        return "global scope"
    
    def _calculate_nesting_at_line(self, lines: List[str], line_num: int) -> int:
        """
        Calculate nesting depth at a specific line.
        
        Args:
            lines: All lines in file
            line_num: Line number (1-indexed)
        
        Returns:
            Nesting depth
        """
        if line_num > len(lines):
            return 0
        
        line = lines[line_num - 1]
        if not line.strip():
            return 0
        
        # Count leading whitespace
        indent = len(line) - len(line.lstrip())
        return indent // 4  # Assuming 4-space indentation
    
    def _calculate_security_relevance(self, content: str, tags: List[str]) -> float:
        """
        Calculate relevance score for security snippet.
        
        Args:
            content: Snippet content
            tags: Associated tags
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        score = 0.5  # Base score
        
        # Increase score for dangerous patterns
        if 'dangerous' in tags:
            score += 0.3
        
        # Increase for multiple security keywords
        security_keywords = ['password', 'token', 'secret', 'key', 'auth', 'sql', 'exec', 'eval']
        keyword_count = sum(1 for kw in security_keywords if kw in content.lower())
        score += min(0.2, keyword_count * 0.05)
        
        return min(1.0, score)
