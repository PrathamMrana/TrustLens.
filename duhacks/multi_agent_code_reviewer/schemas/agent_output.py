"""
Agent Output Schema
Defines the standardized output format for all agents.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            severity = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "none": 0
            }
            return severity[self.value] < severity[other.value]
        return NotImplemented
        
    def __le__(self, other):
        if self.__class__ is other.__class__:
            severity = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "none": 0
            }
            return severity[self.value] <= severity[other.value]
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            severity = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "none": 0
            }
            return severity[self.value] > severity[other.value]
        return NotImplemented
        
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            severity = {
                "critical": 4,
                "high": 3,
                "medium": 2,
                "low": 1,
                "none": 0
            }
            return severity[self.value] >= severity[other.value]
        return NotImplemented


class AgentType(Enum):
    """Types of agents in the system"""
    FEATURE_EXTRACTION = "feature_extraction"
    SECURITY_ANALYSIS = "security_analysis"
    LOGIC_ANALYSIS = "logic_analysis"
    CODE_QUALITY = "code_quality"
    DECISION = "decision"


@dataclass
class AgentOutput:
    """
    Standardized output from any agent.
    All agents MUST return this format.
    """
    agent_type: AgentType
    confidence: float  # 0.0 to 1.0
    findings: List[Dict[str, Any]]
    risk_level: RiskLevel
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate output"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "agent_type": self.agent_type.value,
            "confidence": self.confidence,
            "findings": self.findings,
            "risk_level": self.risk_level.value,
            "metadata": self.metadata,
            "success": self.success,
            "error_message": self.error_message
        }
