"""
Feature Curator
Transforms raw features into structured, agent-specific features.
"""

from typing import Dict, Any, List
from schemas.curated_features import SecurityFeatures, LogicFeatures, QualityFeatures
from utils.logger import Logger


class FeatureCurator:
    """
    Curates raw features into structured, agent-specific features.
    Filters and transforms features to provide only relevant information to each agent.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize feature curator.
        
        Args:
            config: Configuration dict
        """
        self.config = config or {}
        self.logger = Logger("FeatureCurator")
    
    def curate_all(self, raw_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Curate features for all agent types.
        
        Args:
            raw_features: Raw features from FeatureExtractionAgent
        
        Returns:
            Dictionary with keys: 'security', 'logic', 'quality'
        """
        features = raw_features.get("features", {})
        
        return {
            'security': self.curate_for_security(features),
            'logic': self.curate_for_logic(features),
            'quality': self.curate_for_quality(features)
        }
    
    def curate_for_security(self, raw_features: Dict[str, Any]) -> SecurityFeatures:
        """
        Curate features for security analysis.
        
        Args:
            raw_features: Raw extracted features
        
        Returns:
            SecurityFeatures object
        """
        # Extract security-relevant indicators
        risk_indicators = []
        sensitive_files = []
        
        # Check file extensions for sensitive types
        file_extensions = raw_features.get("file_extensions", {})
        if "py" in file_extensions or "js" in file_extensions:
            risk_indicators.append("dynamic_language")
        
        # Check for languages with common security issues
        languages = raw_features.get("languages", [])
        if "php" in languages:
            risk_indicators.append("php_usage")
        if "c" in languages or "cpp" in languages:
            risk_indicators.append("memory_unsafe_language")
        
        # Placeholder for dependency risks (would integrate with dependency scanner)
        dependency_risks = {}
        
        # Placeholder for authentication patterns (detected from code)
        authentication_patterns = []
        
        # Placeholder for input validation gaps
        input_validation_gaps = []
        
        # Calculate total risk score
        total_risk_score = min(1.0, len(risk_indicators) * 0.2)
        
        # Count critical files (placeholder - would be detected from actual analysis)
        critical_file_count = 0
        
        return SecurityFeatures(
            risk_indicators=risk_indicators,
            sensitive_files=sensitive_files,
            dependency_risks=dependency_risks,
            authentication_patterns=authentication_patterns,
            input_validation_gaps=input_validation_gaps,
            total_risk_score=total_risk_score,
            critical_file_count=critical_file_count
        )
    
    def curate_for_logic(self, raw_features: Dict[str, Any]) -> LogicFeatures:
        """
        Curate features for logic analysis.
        
        Args:
            raw_features: Raw extracted features
        
        Returns:
            LogicFeatures object
        """
        complexity_indicators = raw_features.get("complexity_indicators", {})
        
        # Extract complexity metrics
        complexity_metrics = {
            "max_nesting_depth": complexity_indicators.get("nested_depth", 0),
            "total_functions": complexity_indicators.get("function_count", 0),
            "total_classes": complexity_indicators.get("class_count", 0),
        }
        
        control_flow_depth = complexity_indicators.get("nested_depth", 0)
        
        # Function-level metrics (placeholder - would extract from actual analysis)
        function_metrics = {
            "average_function_length": 0,
            "max_function_length": 0,
            "functions_with_high_complexity": []
        }
        
        # Detect loop patterns (placeholder)
        loop_patterns = []
        
        # Calculate conditional complexity
        conditional_complexity = 0
        
        # Calculate average complexity
        total_functions = complexity_metrics["total_functions"]
        average_complexity = control_flow_depth / max(1, total_functions)
        
        # Identify high complexity files (placeholder)
        high_complexity_files = []
        
        return LogicFeatures(
            complexity_metrics=complexity_metrics,
            control_flow_depth=control_flow_depth,
            function_metrics=function_metrics,
            loop_patterns=loop_patterns,
            conditional_complexity=conditional_complexity,
            average_complexity=average_complexity,
            high_complexity_files=high_complexity_files
        )
    
    def curate_for_quality(self, raw_features: Dict[str, Any]) -> QualityFeatures:
        """
        Curate features for code quality analysis.
        
        Args:
            raw_features: Raw extracted features
        
        Returns:
            QualityFeatures object
        """
        # Extract quality-relevant metrics
        total_loc = raw_features.get("total_loc", 0)
        average_file_size = int(raw_features.get("average_file_size", 0))
        
        # Detect code smells (placeholder - would use actual analysis)
        code_smells = []
        
        # Calculate duplication score (placeholder)
        duplication_score = 0.0
        
        # Calculate maintainability index (simplified)
        # Real formula: 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(LoC)
        # Simplified: based on LoC and complexity
        complexity_indicators = raw_features.get("complexity_indicators", {})
        nesting = complexity_indicators.get("nested_depth", 0)
        
        if total_loc > 0:
            # Simple heuristic: lower LoC and nesting = higher maintainability
            maintainability_index = max(0, min(100, 100 - (total_loc / 100) - (nesting * 5)))
        else:
            maintainability_index = 100.0
        
        # Identify long functions (placeholder)
        long_functions = []
        
        # Identify deep nesting (placeholder)
        deep_nesting = []
        
        # Identify files needing refactor (placeholder)
        files_needing_refactor = []
        
        return QualityFeatures(
            code_smells=code_smells,
            duplication_score=duplication_score,
            maintainability_index=maintainability_index,
            long_functions=long_functions,
            deep_nesting=deep_nesting,
            total_loc=total_loc,
            average_file_size=average_file_size,
            files_needing_refactor=files_needing_refactor
        )
