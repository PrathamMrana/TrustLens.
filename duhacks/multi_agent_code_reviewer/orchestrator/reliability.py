"""
Reliability Engine
Tracks agent reliability, confidence aggregation, and failure handling.
Ensures the system never makes an unsafe or blind decision.
"""

from typing import List, Dict, Any, Tuple, Optional
from schemas.agent_output import AgentOutput, AgentType, RiskLevel
import statistics


class ReliabilityEngine:
    """
    Manages reliability tracking and confidence aggregation.
    Determines if the system is allowed to make a decision.
    """
    
    def __init__(self):
        # Static reliability scores per PRD Section 1.2
        self.agent_reliability: Dict[str, float] = {
            AgentType.SECURITY_ANALYSIS.value: 1.0,
            AgentType.LOGIC_ANALYSIS.value: 1.0,
            AgentType.CODE_QUALITY.value: 1.0,
            AgentType.FEATURE_EXTRACTION.value: 1.0
        }
    
    def aggregate_confidence(self, outputs: List[AgentOutput]) -> float:
        """
        Aggregate confidence using Reliability-Weighted Mean (PRD Section 1.1).
        ONLY includes successful agents.
        """
        successful_outputs = [o for o in outputs if o.success]
        
        if not successful_outputs:
            return 0.0
        
        sum_weighted_confidence = 0.0
        sum_reliability = 0.0
        
        for output in successful_outputs:
            agent_type = output.agent_type.value
            reliability = self.agent_reliability.get(agent_type, 1.0)
            
            sum_weighted_confidence += output.confidence * reliability
            sum_reliability += reliability
            
        if sum_reliability == 0:
            return 0.0
            
        return sum_weighted_confidence / sum_reliability
    
    def get_failures(self, outputs: List[AgentOutput]) -> Dict[str, Any]:
        """
        Track failed agents (PRD Section 1.4).
        """
        failed_agents = [o.agent_type.value for o in outputs if not o.success]
        
        # Security agent failure is a specific defer condition
        security_failed = any(
            o.agent_type == AgentType.SECURITY_ANALYSIS and not o.success 
            for o in outputs
        )
        
        return {
            "failed_agents": failed_agents,
            "security_failed": security_failed
        }

    def should_defer(
        self,
        overall_confidence: float,
        conflicts: List[Any],
        failures: Dict[str, Any],
        max_risk: RiskLevel,
        min_confidence_threshold: float = 0.7
    ) -> Tuple[bool, str]:
        """
        Safety Gate: Decide if system must defer to human (PRD Section 1.2).
        Enforces ordered safety rules.
        """
        # 1. If no successful agents -> DEFER
        if overall_confidence <= 0.0:
            return True, "No successful agent outputs received"
        
        # 2. If overall_confidence < 0.70 -> DEFER
        if overall_confidence < min_confidence_threshold:
            return True, f"Overall confidence {overall_confidence:.2f} below threshold {min_confidence_threshold}"
        
        # 3. If unresolved conflicts exist -> DEFER
        if conflicts:
            return True, f"{len(conflicts)} unresolved conflicts between agents"
        
        # 4. If critical agent (Security) failed -> DEFER
        if failures.get("security_failed"):
            return True, "Security analysis agent failed to complete"
            
        # 5. If CRITICAL risk detected AND confidence < 0.80 -> DEFER
        if max_risk == RiskLevel.CRITICAL and overall_confidence < 0.80:
            return True, "Critical risk detected but overall confidence is below safety threshold (0.80)"
        
        return False, ""

    def calculate_system_health(self, outputs: List[AgentOutput]) -> Dict[str, Any]:
        """Calculate system health for metadata."""
        total = len(outputs)
        successful = len([o for o in outputs if o.success])
        avg_conf = self.aggregate_confidence(outputs)
        
        return {
            "total_agents": total,
            "successful_agents": successful,
            "failed_agents": total - successful,
            "average_confidence": avg_conf,
            "health_status": "healthy" if successful == total and avg_conf >= 0.7 else "degraded"
        }
