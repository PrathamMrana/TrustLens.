"""
Base Agent
Abstract base class for all agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from schemas.agent_output import AgentOutput, AgentType


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    All agents MUST inherit from this.
    """
    
    def __init__(self, agent_type: AgentType, config: Dict[str, Any] = None):
        """
        Initialize agent.
        
        Args:
            agent_type: Type of agent
            config: Agent-specific configuration
        """
        self.agent_type = agent_type
        self.config = config or {}
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate agent configuration. Override in subclasses."""
        pass
    
    @abstractmethod
    def analyze(self, s3_path: str, features: Dict[str, Any] = None) -> AgentOutput:
        """
        Analyze code from S3.
        
        Args:
            s3_path: Path to code in S3
            features: Pre-extracted features (optional, from FeatureExtractionAgent)
        
        Returns:
            AgentOutput with analysis results
        """
        pass
    
    def _create_output(
        self,
        confidence: float,
        findings: list,
        risk_level,
        metadata: dict,
        success: bool = True,
        error_message: str = None
    ) -> AgentOutput:
        """
        Helper to create standardized output.
        
        Args:
            confidence: Confidence level (0.0-1.0)
            findings: List of findings
            risk_level: Risk level enum
            metadata: Additional metadata
            success: Whether analysis succeeded
            error_message: Error message if failed
        
        Returns:
            AgentOutput object
        """
        return AgentOutput(
            agent_type=self.agent_type,
            confidence=confidence,
            findings=findings,
            risk_level=risk_level,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
