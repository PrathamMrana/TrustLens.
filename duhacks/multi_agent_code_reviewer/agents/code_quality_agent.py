"""
Code Quality Agent
Metric-based quality assessment. Advisory only, non-blocking.
Receives METRICS ONLY - no raw code (PRD Section 5.3).
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from schemas.agent_output import AgentOutput, AgentType, RiskLevel


class CodeQualityAgent(BaseAgent):
    """
    Evaluates code quality using metrics.
    
    PRD Compliance (Section 5.3):
    - Receives METRICS ONLY
    - NO raw code
    - NO snippets
    - NO LLM usage
    - NO S3 access
    - Advisory only - does not block
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.CODE_QUALITY, config)
        self.quality_thresholds = config.get("thresholds", {
            "max_function_length": 50,
            "max_file_length": 500,
            "min_comment_ratio": 0.1,
            "max_complexity": 10
        }) if config else {
            "max_function_length": 50,
            "max_file_length": 500,
            "min_comment_ratio": 0.1,
            "max_complexity": 10
        }
    
    def _validate_config(self) -> None:
        """Validate configuration"""
        pass
    
    def analyze(self, metrics: Dict[str, Any]) -> AgentOutput:
        """
        Analyze code quality from metrics.
        
        Args:
            metrics: Quality metrics from routing policy (NO code)
        
        Returns:
            AgentOutput with quality assessment
        
        PRD Constraints:
        - Metrics only, no code
        - No LLM usage
        - Advisory only
        """
        try:
            # Validate we received metrics, not code (PRD AC-1)
            if "code" in metrics or "snippets" in metrics:
                self.logger.error("❌ Quality agent received code/snippets - should only receive metrics")
            
            # Generate findings from metrics
            findings = self._generate_quality_findings(metrics)
            
            # Quality is always advisory, confidence is high (metrics are deterministic)
            return self._create_output(
                confidence=0.9,
                findings=findings,
                risk_level=RiskLevel.LOW,  # Quality issues are low risk
                metadata={
                    "quality_metrics": metrics,
                    "advisory": True,
                    "blocking": False
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
    
    def _calculate_quality_metrics(self, code_files: Dict[str, str], features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quality metrics.
        
        Args:
            code_files: Code files
            features: Pre-extracted features
        
        Returns:
            Quality metrics
        """
        metrics = {
            "total_loc": 0,
            "total_comments": 0,
            "comment_ratio": 0.0,
            "average_function_length": 0,
            "long_files": [],
            "long_functions": [],
            "complexity_score": 0
        }
        
        total_functions = 0
        total_function_lines = 0
        
        for filename, content in code_files.items():
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip()])
            comments = len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')])
            
            metrics["total_loc"] += loc
            metrics["total_comments"] += comments
            
            # Check file length
            if loc > self.quality_thresholds["max_file_length"]:
                metrics["long_files"].append({"file": filename, "loc": loc})
            
            # Estimate function lengths (placeholder logic)
            function_count = content.count('def ') + content.count('function ')
            if function_count > 0:
                total_functions += function_count
                total_function_lines += loc
        
        # Calculate ratios
        if metrics["total_loc"] > 0:
            metrics["comment_ratio"] = metrics["total_comments"] / metrics["total_loc"]
        
        if total_functions > 0:
            metrics["average_function_length"] = total_function_lines / total_functions
        
        # Use features for complexity
        if features and "complexity_indicators" in features.get("features", {}):
            metrics["complexity_score"] = features["features"]["complexity_indicators"].get("nested_depth", 0)
        
        return metrics
    
    
    def _generate_quality_findings(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate quality findings from metrics.
        
        Args:
            metrics: Metrics from routing policy
        
        Returns:
            List of findings
        """
        findings = []
        
        # Check average function length
        avg_func_length = metrics.get("avg_function_length", 0)
        if avg_func_length > self.quality_thresholds["max_function_length"]:
            findings.append({
                "type": "long_functions",
                "severity": "info",
                "description": f"Average function length {avg_func_length:.1f} exceeds threshold"
            })
        
        # Check complexity
        max_nesting = metrics.get("max_nesting_depth", 0)
        if max_nesting > self.quality_thresholds["max_complexity"]:
            findings.append({
                "type": "high_complexity",
                "severity": "warning",
                "description": f"Max nesting depth {max_nesting} is high"
            })
        
        # Check total LoC
        total_loc = metrics.get("total_loc", 0)
        if total_loc > 10000:
            findings.append({
                "type": "large_codebase",
                "severity": "info",
                "description": f"Codebase has {total_loc} lines of code"
            })
        
        return findings

