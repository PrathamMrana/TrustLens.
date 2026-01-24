"""
Routing Policy Module
Explicit policy engine for curating agent-specific inputs.
This is the ONLY module that decides what data each agent receives.
"""

import re
from typing import Dict, Any, List, Tuple
from schemas.code_snippet import CodeSnippet
from utils.logger import Logger


class RoutingPolicy:
    """
    Deterministic policy engine for agent input curation.
    
    Core Principle:
    Agents must only see what the orchestrator intentionally gives them.
    
    Responsibilities:
    - Consume structured features
    - Select relevant files/regions
    - Extract bounded snippets
    - Return agent-specific input payloads
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize routing policy.
        
        Args:
            config: Configuration with snippet limits, size constraints, etc.
        """
        self.config = config or {}
        self.logger = Logger("RoutingPolicy")
        
        # Constraints from PRD (updated per user request)
        self.max_snippets_per_agent = self.config.get("max_snippets_per_agent", 5)
        self.max_snippet_chars = self.config.get("max_snippet_chars", 500)
    
    def route_for_security_agent(
        self, 
        code_files: Dict[str, str], 
        features: Dict[str, Any],
        s3_reader: Any = None,
        s3_path: str = None
    ) -> Tuple[Dict[str, Any], List[CodeSnippet]]:
        """
        Curate inputs for Security Agent.
        
        Args:
            code_files: All code files from S3
            features: Structured features from FeatureExtractionAgent
            s3_reader: Optional S3Reader to fetch pre-extracted snippets
            s3_path: Optional S3 path to find snippets folder
        
        Returns:
            Tuple of (curated_features, snippets)
            - Max 5 snippets
            - Max 500 chars per snippet
        """
        self.logger.info("🔒 Routing for Security Agent")
        
        # Curate security-specific features
        curated_features = self._curate_security_features(features)
        
        # Try fetching from S3 first if reader is provided
        snippets = []
        if s3_reader and s3_path:
            self.logger.info("  Fetching pre-extracted snippets from S3...")
            snippets = s3_reader.get_code_snippets(s3_path, "security")
        
        # If no snippets found in S3, fallback to scan
        if not snippets:
            self.logger.info("  No snippets in S3 or no reader, scanning code files...")
            snippets = self._extract_security_snippets(code_files, features)
        
        # Enforce constraints
        snippets = snippets[:self.max_snippets_per_agent]
        for s in snippets:
            if len(s.content) > self.max_snippet_chars:
                s.content = s.content[:self.max_snippet_chars]
        
        self.logger.info(f"✅ Selected {len(snippets)} security snippets")
        return curated_features, snippets
    
    def route_for_logic_agent(
        self, 
        code_files: Dict[str, str], 
        features: Dict[str, Any],
        s3_reader: Any = None,
        s3_path: str = None
    ) -> Tuple[Dict[str, Any], List[CodeSnippet]]:
        """
        Curate inputs for Logic Agent.
        
        Args:
            code_files: All code files from S3
            features: Structured features from FeatureExtractionAgent
            s3_reader: Optional S3Reader to fetch pre-extracted snippets
            s3_path: Optional S3 path to find snippets folder
        
        Returns:
            Tuple of (curated_features, snippets)
            - Max 5 snippets
        """
        self.logger.info("🧠 Routing for Logic Agent")
        
        # Curate logic-specific features
        curated_features = self._curate_logic_features(features)
        
        # Try fetching from S3 first
        snippets = []
        if s3_reader and s3_path:
            self.logger.info("  Fetching pre-extracted snippets from S3...")
            snippets = s3_reader.get_code_snippets(s3_path, "logic")
            
        # Fallback to scan
        if not snippets:
            self.logger.info("  No snippets in S3 or no reader, scanning code files...")
            snippets = self._extract_logic_snippets(code_files, features)
        
        # Enforce constraints
        snippets = snippets[:self.max_snippets_per_agent]
        for s in snippets:
            if len(s.content) > self.max_snippet_chars:
                s.content = s.content[:self.max_snippet_chars]
                
        self.logger.info(f"✅ Selected {len(snippets)} logic snippets")
        return curated_features, snippets
    
    def route_for_quality_agent(
        self, 
        features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Curate inputs for Code Quality Agent.
        
        Args:
            features: Structured features from FeatureExtractionAgent
        
        Returns:
            Metrics ONLY - no raw code, no snippets
        
        Note:
            Code Quality Agent never receives raw code per PRD Section 5.3
        """
        self.logger.info("📊 Routing for Code Quality Agent")
        
        # Extract metrics only
        metrics = self._curate_quality_metrics(features)
        
        self.logger.info(f"✅ Provided metrics only (no code)")
        self.logger.info(f"  Total LoC: {metrics.get('total_loc', 0)}")
        self.logger.info(f"  Max nesting: {metrics.get('max_nesting_depth', 0)}")
        self.logger.info(f"  Avg file size: {metrics.get('avg_file_size', 0)}")
        
        return metrics
    
    # ========== Private Helper Methods ==========
    
    def _curate_security_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract security-relevant features only"""
        raw = features.get("features", {})
        
        return {
            "signals": {
                "has_sql": self._detect_sql_usage(raw),
                "has_user_input": self._detect_user_input(raw),
                "has_crypto": self._detect_crypto_usage(raw),
                "has_auth": self._detect_auth_patterns(raw),
            },
            "risk_indicators": self._extract_risk_indicators(raw),
            "total_loc": raw.get("total_loc", 0),
        }
    
    def _curate_logic_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract logic-relevant features only"""
        raw = features.get("features", {})
        complexity = raw.get("complexity_indicators", {})
        
        return {
            "structure": {
                "max_nesting_depth": complexity.get("nested_depth", 0),
                "function_count": complexity.get("function_count", 0),
                "class_count": complexity.get("class_count", 0),
            },
            "complexity_metrics": {
                "avg_nesting": complexity.get("nested_depth", 0) / max(1, complexity.get("function_count", 1)),
            },
            "total_loc": raw.get("total_loc", 0),
        }
    
    def _curate_quality_metrics(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Extract quality metrics only (no code)"""
        raw = features.get("features", {})
        complexity = raw.get("complexity_indicators", {})
        
        return {
            "avg_function_length": raw.get("total_loc", 0) / max(1, complexity.get("function_count", 1)),
            "max_nesting_depth": complexity.get("nested_depth", 0),
            "total_loc": raw.get("total_loc", 0),
            "avg_file_size": raw.get("average_file_size", 0),
            "function_count": complexity.get("function_count", 0),
            "class_count": complexity.get("class_count", 0),
            "long_files": raw.get("long_files", []),
            "high_nesting_locations": complexity.get("high_nesting_locations", [])
        }
    
    def _extract_security_snippets(
        self, 
        code_files: Dict[str, str], 
        features: Dict[str, Any]
    ) -> List[CodeSnippet]:
        """
        Extract security-relevant snippets.
        
        Selection Criteria (PRD Section 5.1):
        - Must include source (user input) → sink (SQL, exec, crypto)
        - Max 3 snippets
        - Max 500 chars per snippet
        """
        snippets = []
        
        # Security patterns: source → sink
        security_patterns = {
            'sql_injection': {
                'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*(\+|format|f")',
                'tags': ['sql', 'injection', 'source_to_sink'],
                'priority': 1.0
            },
            'code_execution': {
                'pattern': r'(eval|exec)\s*\(',
                'tags': ['code_execution', 'dangerous', 'source_to_sink'],
                'priority': 0.9
            },
            'insecure_deserialization': {
                'pattern': r'pickle\.(load|loads)',
                'tags': ['deserialization', 'dangerous', 'source_to_sink'],
                'priority': 0.85
            },
            'path_traversal': {
                'pattern': r'open\s*\(.*\+',
                'tags': ['path_traversal', 'file_access', 'source_to_sink'],
                'priority': 0.8
            },
        }
        
        for filename, content in code_files.items():
            lines = content.split('\n')
            
            for pattern_name, pattern_info in security_patterns.items():
                matches = list(re.finditer(pattern_info['pattern'], content, re.IGNORECASE))
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Extract snippet with context
                    snippet_content, start_line, end_line = self._extract_bounded_snippet(
                        lines, line_num, self.max_snippet_chars
                    )
                    
                    # Get context
                    context = self._find_function_context(lines, line_num)
                    
                    snippet = CodeSnippet(
                        filename=filename,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        context=context,
                        relevance_score=pattern_info['priority'],
                        tags=pattern_info['tags']
                    )
                    
                    snippets.append(snippet)
                    
                    # Log WHY this snippet was selected (AC-3: Explainability)
                    self.logger.debug(
                        f"Selected snippet: {snippet.get_location()} - "
                        f"Reason: {pattern_name} detected - "
                        f"Tags: {', '.join(snippet.tags)}"
                    )
        
        # Sort by priority and return top 3
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:self.max_snippets_per_agent]
    
    def _extract_logic_snippets(
        self, 
        code_files: Dict[str, str], 
        features: Dict[str, Any]
    ) -> List[CodeSnippet]:
        """
        Extract logic-relevant snippets.
        
        Selection Criteria (PRD Section 5.2):
        - Loops, condition-heavy blocks, deeply nested functions
        - MUST NOT include SQL, auth, or security code
        - Max 3 snippets
        """
        snippets = []
        
        # Logic patterns (explicitly excluding security patterns)
        logic_patterns = {
            'infinite_loop_risk': {
                'pattern': r'while\s+True\s*:',
                'tags': ['loop', 'infinite_loop_risk'],
                'priority': 1.0
            },
            'complex_loop': {
                'pattern': r'for\s+\w+\s+in.*:',
                'tags': ['loop', 'iteration'],
                'priority': 0.6
            },
            'nested_conditional': {
                'pattern': r'if\s+.*:',
                'tags': ['conditional', 'branching'],
                'priority': 0.5
            },
        }
        
        for filename, content in code_files.items():
            # Skip files with security keywords (PRD: Logic agent must not see security code)
            if self._is_security_file(content):
                self.logger.debug(f"Skipped {filename} - contains security patterns")
                continue
            
            lines = content.split('\n')
            
            for pattern_name, pattern_info in logic_patterns.items():
                matches = list(re.finditer(pattern_info['pattern'], content, re.IGNORECASE))
                
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Only extract if nesting is significant
                    nesting = self._calculate_nesting(lines, line_num)
                    if nesting < 2 and pattern_name != 'infinite_loop_risk':
                        continue
                    
                    snippet_content, start_line, end_line = self._extract_bounded_snippet(
                        lines, line_num, self.max_snippet_chars
                    )
                    
                    context = self._find_function_context(lines, line_num)
                    
                    snippet = CodeSnippet(
                        filename=filename,
                        start_line=start_line,
                        end_line=end_line,
                        content=snippet_content,
                        context=context,
                        relevance_score=min(1.0, pattern_info['priority'] + (nesting * 0.1)),
                        tags=pattern_info['tags'] + [f'nesting_{nesting}']
                    )
                    
                    snippets.append(snippet)
                    
                    # Log selection reason (AC-3)
                    self.logger.debug(
                        f"Selected snippet: {snippet.get_location()} - "
                        f"Reason: {pattern_name} with nesting {nesting}"
                    )
        
        snippets.sort(key=lambda s: s.relevance_score, reverse=True)
        return snippets[:self.max_snippets_per_agent]
    
    # ========== Utility Methods ==========
    
    def _extract_bounded_snippet(
        self, 
        lines: List[str], 
        target_line: int, 
        max_chars: int
    ) -> Tuple[str, int, int]:
        """Extract snippet bounded by max_chars"""
        start = max(0, target_line - 1)
        end = min(len(lines), target_line + 1)
        
        content = '\n'.join(lines[start:end])
        
        # Expand until max_chars
        while len(content) < max_chars and (start > 0 or end < len(lines)):
            if start > 0:
                start -= 1
                content = lines[start] + '\n' + content
            if len(content) < max_chars and end < len(lines):
                content = content + '\n' + lines[end]
                end += 1
        
        # Truncate if needed
        if len(content) > max_chars:
            content = content[:max_chars]
        
        return content, start + 1, end
    
    def _find_function_context(self, lines: List[str], line_num: int) -> str:
        """Find function/class context"""
        for i in range(max(0, line_num - 20), line_num):
            line = lines[i].strip()
            
            func_match = re.match(r'def\s+(\w+)', line)
            if func_match:
                return f"function {func_match.group(1)}"
            
            class_match = re.match(r'class\s+(\w+)', line)
            if class_match:
                return f"class {class_match.group(1)}"
        
        return "global scope"
    
    def _calculate_nesting(self, lines: List[str], line_num: int) -> int:
        """Calculate nesting depth at line"""
        if line_num > len(lines):
            return 0
        
        line = lines[line_num - 1]
        indent = len(line) - len(line.lstrip())
        return indent // 4
    
    def _is_security_file(self, content: str) -> bool:
        """Check if file contains security patterns"""
        security_keywords = ['password', 'token', 'auth', 'sql', 'exec', 'eval', 'crypto']
        content_lower = content.lower()
        return any(kw in content_lower for kw in security_keywords)
    
    def _detect_sql_usage(self, features: Dict[str, Any]) -> bool:
        """Detect SQL usage from features"""
        # Placeholder - would check for SQL-related features
        return False
    
    def _detect_user_input(self, features: Dict[str, Any]) -> bool:
        """Detect user input handling"""
        return False
    
    def _detect_crypto_usage(self, features: Dict[str, Any]) -> bool:
        """Detect cryptography usage"""
        return False
    
    def _detect_auth_patterns(self, features: Dict[str, Any]) -> bool:
        """Detect authentication patterns"""
        return False
    
    def _extract_risk_indicators(self, features: Dict[str, Any]) -> List[str]:
        """Extract risk indicators"""
        return []
    
    def _extract_nesting_from_tags(self, tags: List[str]) -> int:
        """Extract nesting level from tags"""
        for tag in tags:
            if tag.startswith('nesting_'):
                try:
                    return int(tag.split('_')[1])
                except:
                    pass
        return 0
