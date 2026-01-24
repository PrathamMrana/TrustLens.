"""
Conflict Resolver
Detects and analyzes disagreements between agents.
"""

from typing import List, Dict, Any
from schemas.agent_output import AgentOutput, RiskLevel
from schemas.final_report import ConflictInfo


class ConflictResolver:
    """
    Detects and analyzes conflicts between agent outputs.
    Does NOT force resolution - flags conflicts for deferral.
    """
    
    def __init__(self, disagreement_threshold: float = 0.3):
        """
        Initialize conflict resolver.
        
        Args:
            disagreement_threshold: Minimum disagreement level to flag conflict
        """
        self.disagreement_threshold = disagreement_threshold
    
    def detect_conflicts(self, outputs: List[AgentOutput]) -> List[ConflictInfo]:
        """
        Detect conflicts between agent outputs.
        
        Args:
            outputs: List of agent outputs
        
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check risk level disagreements
        risk_conflicts = self._detect_risk_disagreements(outputs)
        conflicts.extend(risk_conflicts)
        
        # Check finding contradictions
        finding_conflicts = self._detect_finding_contradictions(outputs)
        conflicts.extend(finding_conflicts)
        
        return conflicts
    
    def _detect_risk_disagreements(self, outputs: List[AgentOutput]) -> List[ConflictInfo]:
        """
        Detect disagreements in risk levels.
        
        Args:
            outputs: Agent outputs
        
        Returns:
            List of risk conflicts
        """
        conflicts = []
        
        # Map risk levels to numeric values
        risk_values = {
            RiskLevel.NONE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        # Get risk assessments from successful security and logic agents
        security_outputs = [o for o in outputs if o.success and o.agent_type.value == "security_analysis"]
        logic_outputs = [o for o in outputs if o.success and o.agent_type.value == "logic_analysis"]
        
        if security_outputs and logic_outputs:
            for sec_out in security_outputs:
                for log_out in logic_outputs:
                    sec_risk = risk_values.get(sec_out.risk_level, 0)
                    log_risk = risk_values.get(log_out.risk_level, 0)
                    
                    # Check if disagreement is significant
                    if abs(sec_risk - log_risk) >= 2:
                        disagreement_level = abs(sec_risk - log_risk) / 4.0
                        
                        conflicts.append(ConflictInfo(
                            agents_involved=["security_analysis", "logic_analysis"],
                            disagreement_level=disagreement_level,
                            conflicting_findings=[
                                {
                                    "agent": "security_analysis",
                                    "risk_level": sec_out.risk_level.value,
                                    "confidence": sec_out.confidence
                                },
                                {
                                    "agent": "logic_analysis",
                                    "risk_level": log_out.risk_level.value,
                                    "confidence": log_out.confidence
                                }
                            ]
                        ))
        
        return conflicts
    
    def _detect_finding_contradictions(self, outputs: List[AgentOutput]) -> List[ConflictInfo]:
        """
        Detect contradictory findings.
        
        Args:
            outputs: Agent outputs
        
        Returns:
            List of finding conflicts
        """
        conflicts = []
        
        # Compare findings between agents (placeholder logic)
        # In production, use semantic similarity or keyword matching
        
        for i, output1 in enumerate(outputs):
            for output2 in outputs[i+1:]:
                if output1.agent_type != output2.agent_type:
                    # Check for contradictions
                    contradiction = self._check_contradiction(
                        output1.findings,
                        output2.findings
                    )
                    
                    if contradiction:
                        conflicts.append(ConflictInfo(
                            agents_involved=[
                                output1.agent_type.value,
                                output2.agent_type.value
                            ],
                            disagreement_level=contradiction["level"],
                            conflicting_findings=contradiction["details"]
                        ))
        
        return conflicts
    
    def _check_contradiction(
        self,
        findings1: List[Dict[str, Any]],
        findings2: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if two sets of findings contradict each other.
        
        Args:
            findings1: First set of findings
            findings2: Second set of findings
        
        Returns:
            Contradiction info if found, None otherwise
        """
        # Placeholder: simple keyword-based contradiction detection
        # In production, use more sophisticated comparison
        
        contradictory_pairs = [
            ("safe", "vulnerable"),
            ("correct", "incorrect"),
            ("valid", "invalid")
        ]
        
        for f1 in findings1:
            desc1 = str(f1.get("description", "")).lower()
            for f2 in findings2:
                desc2 = str(f2.get("description", "")).lower()
                
                for pair in contradictory_pairs:
                    if pair[0] in desc1 and pair[1] in desc2:
                        return {
                            "level": 0.8,
                            "details": [f1, f2]
                        }
                    if pair[1] in desc1 and pair[0] in desc2:
                        return {
                            "level": 0.8,
                            "details": [f1, f2]
                        }
        
        return None
    
    def prioritize_conflicts(self, conflicts: List[ConflictInfo]) -> List[ConflictInfo]:
        """
        Prioritize conflicts by disagreement level.
        
        Args:
            conflicts: List of conflicts
        
        Returns:
            Sorted list of conflicts (highest disagreement first)
        """
        return sorted(conflicts, key=lambda c: c.disagreement_level, reverse=True)
