"""
Decision Agent
Recommends actions based on findings from expert agents.
"""

from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent
from schemas.agent_output import AgentOutput, AgentType, RiskLevel


class DecisionAgent(BaseAgent):
    """
    Synthesizes expert findings into a recommended action (PRD Section 1.3).
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.DECISION, config)
    
    def _validate_config(self) -> None:
        pass
    
    def analyze(self, **kwargs) -> AgentOutput:
        raise NotImplementedError("Use recommend_action instead")
    
    def recommend_action(
        self,
        agent_outputs: List[AgentOutput],
        overall_confidence: float,
        conflicts: List[Any]
    ) -> AgentOutput:
        """
        Synthesize recommendation and calculate decision confidence.
        """
        # 1. Determine Highest Risk Level (PRD Section 2.2)
        success_outputs = [o for o in agent_outputs if o.success]
        
        # Risk priority mapping
        risk_priorities = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1,
            RiskLevel.NONE: 0
        }
        
        max_risk = RiskLevel.NONE
        if success_outputs:
            max_risk = max(success_outputs, key=lambda o: risk_priorities.get(o.risk_level, 0)).risk_level
            
        # 2. Map Risk to Action (PRD Section 1.3)
        recommendation = "acceptable"
        if max_risk == RiskLevel.CRITICAL:
            recommendation = "manual_review_required"
        elif max_risk == RiskLevel.HIGH:
            recommendation = "review_required"
        elif max_risk == RiskLevel.MEDIUM:
            recommendation = "proceed_with_caution"
            
        # 3. Calculate Decision Confidence (PRD Section 2.4)
        decision_confidence = self._calculate_decision_confidence(overall_confidence, conflicts)
        
        return self._create_output(
            confidence=decision_confidence,
            findings=[{
                "recommendation": recommendation,
                "max_risk": max_risk.value
            }],
            risk_level=max_risk,
            metadata={
                "recommendation": recommendation,
                "max_risk": max_risk.value,
                "decision_confidence": decision_confidence,
                # Store traces (PRD Section 3.1)
                "agent_traces": [
                    {
                        "agent": o.agent_type.value,
                        "success": o.success,
                        "confidence": o.confidence,
                        "risk": o.risk_level.value,
                        "snippets_used": o.metadata.get("snippet_locations", []),
                        "findings_count": len(o.findings)
                    }
                    for o in agent_outputs
                ]
            }
        )

    def _calculate_decision_confidence(self, overall_confidence: float, conflicts: List[Any]) -> float:
        """
        Apply conflict penalties (PRD Section 2.4).
        """
        penalty = 0.0
        for conflict in conflicts:
            disagreement = getattr(conflict, "disagreement_level", 1.0)
            penalty += 0.2 * disagreement
            
        penalty = min(penalty, 0.5)
        return max(0.0, overall_confidence - penalty)
