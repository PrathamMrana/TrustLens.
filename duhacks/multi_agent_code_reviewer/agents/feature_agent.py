"""
Feature Extraction Agent
Extracts static features from code WITHOUT using LLM.
This is the ONLY agent allowed to scan the full codebase (PRD Section 3.2).
"""

from typing import Dict, Any
from .base_agent import BaseAgent
from schemas.agent_output import AgentOutput, AgentType, RiskLevel


class FeatureExtractionAgent(BaseAgent):
    """
    Extracts deterministic features from code.
    NO LLM usage - purely static analysis.
    
    PRD Compliance (Section 3.2):
    - ONLY agent allowed to scan full codebase
    - Outputs structured features only
    - No S3 access (receives code from orchestrator)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.FEATURE_EXTRACTION, config)
    
    def _validate_config(self) -> None:
        """Validate configuration"""
        # No special config needed for feature extraction
        pass
    
    def analyze(self, code_files: Dict[str, str], features: Dict[str, Any] = None) -> AgentOutput:
        """
        Extract static features from code.
        
        Args:
            code_files: Dictionary of {filename: content} from orchestrator
            features: Ignored for this agent
        
        Returns:
            AgentOutput with extracted features
        """
        try:
            # Extract features (deterministic only)
            extracted_features = self._extract_features(code_files)
            
            return self._create_output(
                confidence=1.0,  # Feature extraction is deterministic
                findings=[],  # Features go in metadata
                risk_level=RiskLevel.NONE,  # Feature agent doesn't assess risk
                metadata={
                    "features": extracted_features,
                    "file_count": len(code_files)
                }
            )
        except Exception as e:
            return self._create_output(
                confidence=0.0,
                findings=[],
                risk_level=RiskLevel.NONE,
                metadata={},
                success=False,
                error_message=str(e)
            )
    
    def _extract_features(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract static features from code files.
        
        Args:
            code_files: Dictionary of {filename: content}
        
        Returns:
            Dictionary of extracted features
        """
        features = {
            "total_loc": 0,
            "languages": set(),
            "file_extensions": {},
            "average_file_size": 0,
            "complexity_indicators": {
                "nested_depth": 0,
                "function_count": 0,
                "class_count": 0
            }
        }
        
        total_size = 0
        for filename, content in code_files.items():
            # Count lines
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip()])
            features["total_loc"] += loc
            
            # Detect language by extension
            ext = filename.split('.')[-1] if '.' in filename else 'unknown'
            features["languages"].add(ext)
            features["file_extensions"][ext] = features["file_extensions"].get(ext, 0) + 1
            
            # File size
            total_size += len(content)
            
            # Simple complexity indicators (placeholder logic)
            features["complexity_indicators"]["nested_depth"] = max(
                features["complexity_indicators"]["nested_depth"],
                self._calculate_nesting_depth(content)
            )
            features["complexity_indicators"]["function_count"] += content.count('def ') + content.count('function ')
            features["complexity_indicators"]["class_count"] += content.count('class ')
        
        features["average_file_size"] = total_size / len(code_files) if code_files else 0
        features["languages"] = list(features["languages"])
        
        return features
    
    def _calculate_nesting_depth(self, content: str) -> int:
        """
        Calculate maximum nesting depth (simplified).
        
        Args:
            content: File content
        
        Returns:
            Maximum nesting depth
        """
        # Placeholder: count indentation levels
        max_depth = 0
        for line in content.split('\n'):
            if line.strip():
                depth = (len(line) - len(line.lstrip())) // 4
                max_depth = max(max_depth, depth)
        return max_depth
