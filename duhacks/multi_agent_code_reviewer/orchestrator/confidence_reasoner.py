"""
Confidence Reasoner
Translates system confidence metrics into human-readable explanations.
"""

from typing import List, Any


class ConfidenceReasoner:
    """
    Deterministic explains for transparency and auditability.
    """
    
    @staticmethod
    def generate_explanation(
        failed_count: int,
        conflict_count: int,
        analytic_confidence: float,
        final_decision_confidence: float
    ) -> str:
        """
        Generate plain-English explanation (PRD Section 2).
        """
        if analytic_confidence == 1.0 and failed_count == 0 and conflict_count == 0:
            return "High confidence achieved with no agent failures or conflicts."
            
        points = []
        
        if failed_count > 0:
            points.append(f"overall confidence reduced due to {failed_count} agent failure{'s' if failed_count > 1 else ''}")
            
        if conflict_count > 0:
            points.append(f"decision confidence penalized due to disagreement between agents")
            
        if analytic_confidence < 0.8:
            points.append("analytic certainty is moderate")
            
        if not points:
            return "Analysis complete with nominal confidence."
            
        # Capitalize first and join
        explanation = "; ".join(points)
        return explanation[0].upper() + explanation[1:] + "."
