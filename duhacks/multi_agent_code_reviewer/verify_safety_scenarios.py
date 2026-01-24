
import os
import sys
import json
from unittest.mock import MagicMock, patch

# Add project root to sys.path
project_root = os.path.abspath(os.getcwd())
if project_root not in sys.path:
    sys.path.append(project_root)

from orchestrator.orchestrator import Orchestrator
from schemas.agent_output import AgentOutput, AgentType, RiskLevel

def run_safety_scenario(name, outputs, expected_decision, expected_deferred):
    print(f"\n>>> RUNNING SCENARIO: {name}")
    
    config = {"min_confidence": 0.7}
    orchestrator = Orchestrator(config)
    orchestrator.s3_reader.use_mock = True
    
    # Patch all agents to return our controlled outputs
    with patch('agents.feature_agent.FeatureExtractionAgent.analyze') as mock_feat, \
         patch('orchestrator.orchestrator.Orchestrator._run_analysis_agents') as mock_run:
        
        mock_feat.return_value = AgentOutput(AgentType.FEATURE_EXTRACTION, 1.0, [], RiskLevel.NONE, {"features": {}}, True)
        mock_run.return_value = outputs
        
        report = orchestrator.analyze_repository("https://github.com/test/repo", "s3://mock/")
        
        print(f"  Decision: {report.action_recommended}")
        print(f"  Deferred: {report.deferred}")
        if report.deferred:
            print(f"  Reason:   {report.deferral_reason}")
        print(f"  Analytics Confidence: {report.metadata['analysis_confidence']:.2f}")
        print(f"  Decision Confidence:  {report.metadata['decision_confidence']:.2f}")
        print(f"  Explainability:       {report.metadata['confidence_reasoning']}")
        print(f"  Agent Traces:")
        for trace in report.metadata.get('agent_traces', []):
            print(f"    - {trace['agent']}: success={trace['success']}, risk={trace['risk']}, conf={trace['confidence']:.2f}, snippets={trace['snippets_used']}")
        assert report.deferred == expected_deferred, f"Expected deferred={expected_deferred}, got {report.deferred}"
        print(f"  ✅ Scenario Passed")

def main():
    print("="*80)
    print("TRUSTLENS SAFETY & DECISION VALIDATION")
    print("="*80)

    # Scenario A: CLEAN REPO
    outputs_a = [
        AgentOutput(AgentType.SECURITY_ANALYSIS, 0.95, [], RiskLevel.NONE, {}, True),
        AgentOutput(AgentType.LOGIC_ANALYSIS, 0.90, [], RiskLevel.NONE, {}, True)
    ]
    run_safety_scenario("CLEAN REPO (High Confidence)", outputs_a, "acceptable", False)

    # Scenario B: CONFLICTING SIGNALS
    # Note: Orchestrator currently uses ConflictResolver which detects conflicts.
    # We need to simulate a conflict.
    from orchestrator.conflict_resolver import ConflictResolver
    with patch('orchestrator.conflict_resolver.ConflictResolver.detect_conflicts') as mock_冲突:
        mock_冲突.return_value = [{"agents_involved": ["security", "logic"], "disagreement_level": 1.0}]
        outputs_b = [
            AgentOutput(AgentType.SECURITY_ANALYSIS, 0.9, [], RiskLevel.HIGH, {}, True),
            AgentOutput(AgentType.LOGIC_ANALYSIS, 0.9, [], RiskLevel.NONE, {}, True)
        ]
        run_safety_scenario("CONFLICTING SIGNALS", outputs_b, "defer", True)

    # Scenario C: CRITICAL VULNERABILITY (High Confidence)
    outputs_c = [
        AgentOutput(AgentType.SECURITY_ANALYSIS, 0.85, [{"issue": "SQLi"}], RiskLevel.CRITICAL, {}, True),
        AgentOutput(AgentType.LOGIC_ANALYSIS, 0.85, [], RiskLevel.HIGH, {}, True)
    ]
    run_safety_scenario("CRITICAL VULNERABILITY (High Confidence)", outputs_c, "manual_review_required", False)

    # Scenario D: CRITICAL VULNERABILITY (Low Confidence -> Defer)
    outputs_d = [
        AgentOutput(AgentType.SECURITY_ANALYSIS, 0.75, [{"issue": "SQLi"}], RiskLevel.CRITICAL, {}, True),
        AgentOutput(AgentType.LOGIC_ANALYSIS, 0.70, [], RiskLevel.NONE, {}, True)
    ]
    run_safety_scenario("CRITICAL VULNERABILITY (Low Confidence)", outputs_d, "defer", True)

    # Scenario E: SECURITY AGENT FAILURE
    outputs_e = [
        AgentOutput(AgentType.SECURITY_ANALYSIS, 0.0, [], RiskLevel.NONE, {}, False),
        AgentOutput(AgentType.LOGIC_ANALYSIS, 0.95, [], RiskLevel.NONE, {}, True)
    ]
    run_safety_scenario("SECURITY AGENT FAILURE", outputs_e, "defer", True)

    print("\n" + "="*80)
    print("ALL SAFETY SCENARIOS VALIDATED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    main()
