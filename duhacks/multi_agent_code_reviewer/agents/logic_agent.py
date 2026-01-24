"""
Logic Analysis Agent
Analyzes code logic and correctness using Gemini LLM.
Receives ONLY logic-relevant snippets (PRD Section 5.2).
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from schemas.agent_output import AgentOutput, AgentType, RiskLevel
from schemas.code_snippet import CodeSnippet
from llm.gemini_client import GeminiClient


class LogicAnalysisAgent(BaseAgent):
    """
    Analyzes code logic for correctness.
    
    PRD Compliance (Section 5.2):
    - Receives logic features + max 3 logic snippets
    - Only loops, conditionals, deeply nested code
    - MUST NOT receive security code (SQL, auth, etc.)
    - NO S3 access
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.LOGIC_ANALYSIS, config)
        self.gemini_client = GeminiClient()
    
    def _validate_config(self) -> None:
        """Validate configuration"""
        pass
    
    def analyze(self, features: Dict[str, Any], snippets: List[CodeSnippet]) -> AgentOutput:
        """
        Analyze code logic.
        
        Args:
            features: Curated logic features from routing policy
            snippets: Pre-extracted logic-relevant snippets (max 3)
        
        Returns:
            AgentOutput with logic analysis
        
        PRD Constraints:
        - Max 3 snippets
        - Only logic-heavy code (no security patterns)
        """
        try:
            # Validate inputs (PRD AC-2)
            if len(snippets) > 5:
                self.logger.warning(f"⚠️ Received {len(snippets)} snippets, expected max 5")
                snippets = snippets[:5]
            
            # Verify no security snippets (PRD Section 5.2)
            for snippet in snippets:
                if any(tag in ['sql', 'auth', 'crypto'] for tag in snippet.tags):
                    self.logger.error(
                        f"❌ Logic agent received security snippet: {snippet.get_location()}"
                    )
            
            # Analyze with LLM
            findings = []
            total_confidence = 0.0
            
            for snippet in snippets:
                result = self._analyze_logic_with_llm(snippet, features)
                findings.extend(result["findings"])
                total_confidence += result["confidence"]
            
            avg_confidence = total_confidence / len(snippets) if snippets else 0.6
            
            # Logic issues map to risk levels
            risk_level = self._determine_risk_from_logic(findings)
            
            return self._create_output(
                confidence=avg_confidence,
                findings=findings,
                risk_level=risk_level,
                metadata={
                    "snippets_analyzed": len(snippets),
                    "snippet_locations": [s.get_location() for s in snippets],
                    "snippets": [s.content for s in snippets],
                    "features_used": list(features.keys())
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
    
    def _analyze_logic_with_llm(self, snippet: CodeSnippet, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze logic using LLM.
        
        Args:
            snippet: CodeSnippet object with code and metadata
            features: Logic features for context
        
        Returns:
            Analysis results
        """
        prompt = f"""
        Analyze this code for LOGIC CORRECTNESS ONLY.
        Location: {snippet.get_location()}
        Context: {snippet.context}
        Nesting: {[tag for tag in snippet.tags if 'nesting' in tag]}
        
        Code:
        {snippet.content}
        
        Check for:
        1. Infinite loops
        2. Unreachable code
        3. Logic contradictions
        4. Off-by-one errors
        5. Incorrect conditionals
        6. Missing edge case handling
        
        Do NOT check security or code quality.
        
        Return JSON:
        {{
            "findings": [
                {{"issue": "...", "severity": "...", "description": "..."}}
            ],
            "confidence": 0.0-1.0
        }}
        """
        
        llm_response = self.gemini_client.generate(prompt)
        
        return {
            "findings": llm_response.get("findings", []),
            "confidence": llm_response.get("confidence", 0.6)
        }
    
    def _determine_risk_from_logic(self, findings: List[Dict[str, Any]]) -> RiskLevel:
        """
        Map logic issues to risk levels.
        
        Args:
            findings: Logic findings
        
        Returns:
            Risk level
        """
        if not findings:
            return RiskLevel.NONE
        
        critical_issues = ["infinite_loop", "logic_contradiction"]
        high_issues = ["unreachable_code", "off_by_one"]
        
        for finding in findings:
            issue_type = finding.get("issue", "").lower()
            if any(critical in issue_type for critical in critical_issues):
                return RiskLevel.HIGH
            if any(high in issue_type for high in high_issues):
                return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
