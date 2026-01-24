"""
Curated Feature Schemas
Structured features for specific agent types.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class SecurityFeatures:
    """
    Curated features for security analysis.
    """
    risk_indicators: List[str]  # e.g., ['sql_usage', 'eval_usage', 'pickle_usage']
    sensitive_files: List[str]  # Files that handle auth, crypto, etc.
    dependency_risks: Dict[str, str]  # {package: risk_description}
    authentication_patterns: List[str]  # Detected auth patterns
    input_validation_gaps: List[str]  # Files missing input validation
    
    # Summary metrics
    total_risk_score: float  # 0.0 to 1.0
    critical_file_count: int


@dataclass
class LogicFeatures:
    """
    Curated features for logic analysis.
    """
    complexity_metrics: Dict[str, int]  # {metric_name: value}
    control_flow_depth: int  # Maximum nesting depth
    function_metrics: Dict[str, Any]  # Function-level metrics
    loop_patterns: List[str]  # Detected loop patterns
    conditional_complexity: int  # Number of complex conditionals
    
    # Summary metrics
    average_complexity: float
    high_complexity_files: List[str]


@dataclass
class QualityFeatures:
    """
    Curated features for code quality analysis.
    """
    code_smells: List[str]  # Detected code smells
    duplication_score: float  # 0.0 to 1.0
    maintainability_index: float  # 0.0 to 100.0
    long_functions: List[Dict[str, Any]]  # Functions exceeding length threshold
    deep_nesting: List[Dict[str, Any]]  # Deeply nested code blocks
    
    # Summary metrics
    total_loc: int
    average_file_size: int
    files_needing_refactor: List[str]
