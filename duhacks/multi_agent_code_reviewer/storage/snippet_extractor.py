from typing import Dict, List, Any
from schemas.code_snippet import CodeSnippet
from utils.logger import Logger

# Detectors
from snippet.detectors.language_detector import detect_language, Language

# Parsers
from snippet.parsers.python_parser import PythonParser
from snippet.parsers.javascript_parser import JavascriptParser
from snippet.parsers.typescript_parser import TypescriptParser
from snippet.parsers.java_parser import JavaParser

# IR
from snippet.ir.code_block import CodeBlock

# Selectors
from snippet.selectors.security_selector import SecuritySelector
from snippet.selectors.logic_selector import LogicSelector
from snippet.selectors.quality_selector import QualitySelector

class SnippetExtractor:
    """
    Production-grade Code Snippet Extraction System.
    Orchestrates parsing, selection, and extraction.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = Logger("SnippetExtractor")
        self.max_snippet_length = self.config.get("max_snippet_length", 500)
        
        # Tools
        self.python_parser = PythonParser()
        self.javascript_parser = JavascriptParser()
        self.typescript_parser = TypescriptParser()
        self.java_parser = JavaParser()
        
        self.security_selector = SecuritySelector()
        self.logic_selector = LogicSelector()
        self.quality_selector = QualitySelector()

    def extract_from_directory(self, local_dir: str) -> Dict[str, Any]:
        """
        Legacy support wrapper for folder-based extraction.
        Reads files and calls extract_all.
        """
        import os
        code_files = {}
        
        for root, _, files in os.walk(local_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java')):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, local_dir)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            code_files[rel_path] = f.read()
                    except Exception as e:
                        self.logger.warning(f"Could not read {rel_path}: {e}")
                        
        # Mock features since new architecture doesn't use them (yet)
        return self.extract_all(code_files, features={})

    def extract_all(self, code_files: Dict[str, str], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for extraction.
        
        Returns:
            {
                'security': [CodeSnippet],
                'logic': [CodeSnippet],
                'quality': {metrics}
            }
        """
        security_snippets = []
        logic_snippets = []
        quality_metrics_agg = {}

        for filename, content in code_files.items():
            lang = detect_language(filename)
            
            # 1. Parse into IR using correct parser
            blocks = []
            try:
                if lang == Language.PYTHON:
                    blocks = self.python_parser.parse(content)
                elif lang == Language.JAVASCRIPT:
                    blocks = self.javascript_parser.parse(content)
                elif lang == Language.TYPESCRIPT:
                    blocks = self.typescript_parser.parse(content)
                elif lang == Language.JAVA:
                    blocks = self.java_parser.parse(content)
                else:
                    self.logger.debug(f"Skipping unsupported file: {filename}")
                    continue
            except Exception as e:
                self.logger.error(f"Failed to parse {filename}: {e}")
                continue
                
            if not blocks:
                # If no blocks found, skip selector step
                continue

            # 2. Select Blocks
            sec_blocks = self.security_selector.select(blocks)
            log_blocks = self.logic_selector.select(blocks)
            qual_metrics = self.quality_selector.compute_metrics(blocks)

            # 3. Convert to Snippets
            lines = content.splitlines()
            
            for b in sec_blocks:
                security_snippets.append(self._to_snippet(b, filename, lines, "security"))
                
            for b in log_blocks:
                logic_snippets.append(self._to_snippet(b, filename, lines, "logic"))
                
            quality_metrics_agg[filename] = qual_metrics

        return {
            "security": security_snippets,
            "logic": logic_snippets,
            "quality": quality_metrics_agg # Return metrics directly, strictly no snippets
        }

    def _to_snippet(self, block: CodeBlock, filename: str, lines: List[str], category: str) -> CodeSnippet:
        """
        Convert IR CodeBlock to bounded CodeSnippet.
        Enforces line boundaries and max length.
        """
        # 0-indexed slicing
        start = max(0, block.start_line - 1)
        end = min(len(lines), block.end_line)
        
        subset = lines[start:end]
        content = "\n".join(subset)
        
        # Hard cap on length just in case
        if len(content) > self.max_snippet_length:
            content = content[:self.max_snippet_length] + "\n...[truncated]"

        # Context description
        context = f"{block.type} {block.name}"
        if block.name:
            context += f" (complexity: {block.complexity})"

        # Create Schema Object
        # Note: Relevance score is simplified here as 1.0 since selectors filter aggressively
        return CodeSnippet(
            filename=filename,
            start_line=block.start_line,
            end_line=block.end_line,
            content=content,
            context=context,
            relevance_score=1.0, 
            tags=[category, block.type] + list(block.metadata.keys())
        )
