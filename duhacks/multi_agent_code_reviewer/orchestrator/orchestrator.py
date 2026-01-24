"""
Orchestrator
Coordinates all agents and manages the analysis workflow.
Acts as a deterministic policy engine - decides what data each agent receives.
"""

from typing import Dict, Any, List
from datetime import datetime
from schemas.agent_output import AgentOutput, AgentType
from schemas.final_report import FinalReport, RiskLevel
from agents.feature_agent import FeatureExtractionAgent
from agents.security_agent import SecurityAnalysisAgent
from agents.logic_agent import LogicAnalysisAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.decision_agent import DecisionAgent
from .conflict_resolver import ConflictResolver
from .reliability import ReliabilityEngine
from .routing_policy import RoutingPolicy
from storage.s3_reader import S3Reader
from utils.logger import Logger


class Orchestrator:
    """
    Coordinates all agents and manages the analysis workflow.
    
    Core Principle (PRD Section 3.1):
    - Acts as a deterministic policy engine
    - Decides what data each agent receives
    - Passes only structured features and curated snippets
    - NEVER calls LLM directly
    - NEVER delegates input selection to agents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize orchestrator with all agents."""
        self.config = config or {}
        self.logger = Logger("Orchestrator")
        
        # Initialize agents
        self.feature_agent = FeatureExtractionAgent()
        self.security_agent = SecurityAnalysisAgent(config.get("security_config"))
        self.logic_agent = LogicAnalysisAgent(config.get("logic_config"))
        self.quality_agent = CodeQualityAgent(config.get("quality_config"))
        self.decision_agent = DecisionAgent(config.get("decision_config"))
        
        # Initialize support systems
        self.conflict_resolver = ConflictResolver()
        self.reliability_engine = ReliabilityEngine()
        
        # Initialize routing policy (PRD Section 6)
        self.routing_policy = RoutingPolicy(config.get("routing_config"))
        
        # Initialize S3 reader (orchestrator reads S3, agents do NOT)
        self.s3_reader = S3Reader()
    
    def analyze_repository(self, repo_url: str, s3_path: str) -> FinalReport:
        """
        Analyze a code repository.
        
        Flow (PRD Section 4):
        1. Read code from S3 (orchestrator only)
        2. Feature extraction (full scan)
        3. Routing policy curates inputs
        4. Agents receive explicit inputs (no S3 access)
        """
        self.logger.info(f"Starting analysis for {repo_url}")
        
        # Step 1: Read code from S3 ONCE (centralized)
        self.logger.info("📦 Reading code from S3...")
        code_files = self.s3_reader.read_code_snapshot(s3_path)
        self.logger.info(f"✅ Read {len(code_files)} files from S3")
        
        # Step 2: Feature Extraction (full scan - PRD Section 3.2)
        self.logger.info("🔍 Extracting features...")
        feature_output = self.feature_agent.analyze(code_files)
        if not feature_output.success:
            return self._create_error_report(repo_url, s3_path, "Feature extraction failed", feature_output.error_message)
        
        features = feature_output.metadata
        self.logger.info("✅ Feature extraction complete")
        
        # Step 3: Run analysis agents with curated inputs
        agent_outputs = self._run_analysis_agents(code_files, features)
        all_outputs = [feature_output] + agent_outputs
        
        # Step 4: Detect conflicts
        conflicts = self.conflict_resolver.detect_conflicts(agent_outputs)
        
        # Step 5: Aggregate confidence
        overall_confidence = self.reliability_engine.aggregate_confidence(agent_outputs)
        
        # Step 6: Check deferral
        should_defer, defer_reason = self.reliability_engine.should_defer(overall_confidence, conflicts)
        
        # Step 7: Get decision
        decision_output = self.decision_agent.recommend_action(agent_outputs, overall_confidence, conflicts)
        all_outputs.append(decision_output)
        
        # Step 8: Generate report
        risk_levels = [o.risk_level for o in agent_outputs if o.success]
        overall_risk = max(risk_levels) if risk_levels else RiskLevel.NONE
        
        report = FinalReport(
            repository_url=repo_url,
            s3_snapshot_path=s3_path,
            timestamp=datetime.now(),
            overall_confidence=overall_confidence,
            overall_risk_level=overall_risk,
            agent_outputs=all_outputs,
            conflicts=conflicts,
            recommendation=decision_output.metadata.get("recommendation", "unknown"),
            action_recommended=decision_output.metadata.get("recommendation"),
            deferred=should_defer,
            deferral_reason=defer_reason if should_defer else None,
            metadata={"system_health": self.reliability_engine.calculate_system_health(all_outputs)}
        )
        
        return report
    
    def _run_analysis_agents(self, code_files: Dict[str, str], features: Dict[str, Any]) -> List[AgentOutput]:
        """
        Run all analysis agents with curated inputs.
        
        PRD Compliance:
        - Routing policy curates inputs (PRD Section 6)
        - Agents receive explicit inputs only (PRD Section 7)
        - No agent accesses S3 directly (PRD AC-1)
        """
        outputs = []
        
        # Security Agent (PRD Section 5.1)
        try:
            self.logger.info("🔒 Running Security Agent...")
            security_features, security_snippets = self.routing_policy.route_for_security_agent(
                code_files, features
            )
            outputs.append(self.security_agent.analyze(security_features, security_snippets))
            self.logger.info("✅ Security analysis complete")
        except Exception as e:
            self.logger.error(f"Security agent failed: {e}")
        
        # Logic Agent (PRD Section 5.2)
        try:
            self.logger.info("🧠 Running Logic Agent...")
            logic_features, logic_snippets = self.routing_policy.route_for_logic_agent(
                code_files, features
            )
            outputs.append(self.logic_agent.analyze(logic_features, logic_snippets))
            self.logger.info("✅ Logic analysis complete")
        except Exception as e:
            self.logger.error(f"Logic agent failed: {e}")
        
        # Code Quality Agent (PRD Section 5.3 - metrics only, no code)
        try:
            self.logger.info("📊 Running Code Quality Agent...")
            quality_metrics = self.routing_policy.route_for_quality_agent(features)
            outputs.append(self.quality_agent.analyze(quality_metrics))
            self.logger.info("✅ Quality analysis complete")
        except Exception as e:
            self.logger.error(f"Quality agent failed: {e}")
        
        return outputs

    
    def _create_error_report(self, repo_url: str, s3_path: str, error_type: str, error_message: str) -> FinalReport:
        """Create error report when analysis fails."""
        return FinalReport(
            repository_url=repo_url,
            s3_snapshot_path=s3_path,
            timestamp=datetime.now(),
            overall_confidence=0.0,
            overall_risk_level=RiskLevel.NONE,
            agent_outputs=[],
            conflicts=[],
            recommendation="Analysis failed",
            action_recommended="defer",
            deferred=True,
            deferral_reason=f"{error_type}: {error_message}",
            metadata={"error": True}
        )
