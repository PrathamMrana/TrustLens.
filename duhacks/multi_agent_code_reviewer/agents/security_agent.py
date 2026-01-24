"""
Security Analysis Agent
Analyzes code for security risks using Gemini LLM.
Receives ONLY curated features and bounded snippets (PRD Section 5.1).
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from schemas.agent_output import AgentOutput, AgentType, RiskLevel
from schemas.code_snippet import CodeSnippet
from llm.gemini_client import GeminiClient


class SecurityAnalysisAgent(BaseAgent):
    """
    Detects security vulnerabilities using LLM.
    
    PRD Compliance (Section 5.1):
    - Receives structured features + max 3 security snippets
    - Max 300-500 chars per snippet
    - Snippets include source → sink patterns
    - NO S3 access
    - NO full files
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(AgentType.SECURITY_ANALYSIS, config)
        self.gemini_client = GeminiClient()
    
    def _validate_config(self) -> None:
        """Validate configuration"""
        pass
    
    def analyze(self, features: Dict[str, Any], snippets: List[CodeSnippet]) -> AgentOutput:
        """
        Analyze code for security risks.
        
        Args:
            features: Curated security features from routing policy
            snippets: Pre-extracted security-relevant snippets (max 3)
        
        Returns:
            AgentOutput with security findings
        
        PRD Constraints:
        - Max 3 snippets
        - Max 500 chars per snippet
        - No direct code access
        """
        try:
            # Validate inputs (PRD AC-2: Bounded context enforcement)
            if len(snippets) > 3:
                self.logger.warning(f"⚠️ Received {len(snippets)} snippets, expected max 3")
                snippets = snippets[:3]
            
            for snippet in snippets:
                if snippet.get_size() > 500:
                    self.logger.warning(
                        f"⚠️ Snippet {snippet.get_location()} exceeds 500 chars ({snippet.get_size()})"
                    )
            
            # Analyze snippets with LLM
            findings = []
            total_confidence = 0.0
            
            for snippet in snippets:
                result = self._analyze_snippet_with_llm(snippet, features)
                findings.extend(result["findings"])
                total_confidence += result["confidence"]
            
            # Calculate overall confidence
            avg_confidence = total_confidence / len(snippets) if snippets else 0.5
            
            # Determine risk level
            risk_level = self._determine_risk_level(findings)
            
            return self._create_output(
                confidence=avg_confidence,
                findings=findings,
                risk_level=risk_level,
                metadata={
                    "snippets_analyzed": len(snippets),
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
    
    def _analyze_snippet_with_llm(self, snippet: CodeSnippet, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code snippet using Gemini LLM.
        
        Args:
            snippet: CodeSnippet object with code and metadata
            features: Security features for context
        
        Returns:
            Dictionary with findings and confidence
        """
        prompt = f"""
        Analyze this code snippet for SECURITY RISKS ONLY.
        Location: {snippet.get_location()}
        Context: {snippet.context}
        Tags: {', '.join(snippet.tags)}
        
        Code:
        {snippet.content}
        
        Identify:
        1. SQL injection risks
        2. Authentication/authorization issues
        3. Input validation gaps
        4. Cryptographic weaknesses
        5. Code execution vulnerabilities
        
        Return JSON format:
        {{
            "findings": [
                {{"type": "...", "severity": "...", "description": "...", "line": "..."}}
            ],
            "confidence": 0.0-1.0
        }}
        """
        
        # Call LLM (mocked for skeleton)
        llm_response = self.gemini_client.generate(prompt)
        
        # Parse response (placeholder)
        return {
            "findings": llm_response.get("findings", []),
            "confidence": llm_response.get("confidence", 0.7)
        }
    
    def _determine_risk_level(self, findings: List[Dict[str, Any]]) -> RiskLevel:
        """
        Determine overall risk level from findings.
        
        Args:
            findings: List of security findings
        
        Returns:
            RiskLevel enum
        """
        if not findings:
            return RiskLevel.NONE
        
        severities = [f.get("severity", "low") for f in findings]
        
        if "critical" in severities:
            return RiskLevel.CRITICAL
        elif "high" in severities:
            return RiskLevel.HIGH
        elif "medium" in severities:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
