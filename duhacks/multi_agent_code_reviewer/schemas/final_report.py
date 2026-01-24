"""
Final Report Schema
Defines the output format for the complete analysis.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from .agent_output import AgentOutput, RiskLevel


@dataclass
class ConflictInfo:
    """Information about conflicts between agents"""
    agents_involved: List[str]
    disagreement_level: float
    conflicting_findings: List[Dict[str, Any]]


@dataclass
class FinalReport:
    """
    Complete analysis report from the orchestrator.
    This is what the system outputs to the user.
    """
    repository_url: str
    s3_snapshot_path: str
    timestamp: datetime
    
    overall_confidence: float
    overall_risk_level: RiskLevel
    
    agent_outputs: List[AgentOutput]
    conflicts: List[ConflictInfo]
    
    recommendation: str
    action_recommended: Optional[str]  # e.g., "defer", "review_required", "proceed_with_caution"
    
    deferred: bool  # True if system could not make confident assessment
    deferral_reason: Optional[str]
    
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for output"""
        return {
            "repository_url": self.repository_url,
            "s3_snapshot_path": self.s3_snapshot_path,
            "timestamp": self.timestamp.isoformat(),
            "overall_confidence": self.overall_confidence,
            "overall_risk_level": self.overall_risk_level.value,
            "agent_outputs": [output.to_dict() for output in self.agent_outputs],
            "conflicts": [
                {
                    "agents_involved": c.agents_involved,
                    "disagreement_level": c.disagreement_level,
                    "conflicting_findings": c.conflicting_findings
                }
                for c in self.conflicts
            ],
            "recommendation": self.recommendation,
            "action_recommended": self.action_recommended,
            "deferred": self.deferred,
            "deferral_reason": self.deferral_reason,
            "metadata": self.metadata
        }
