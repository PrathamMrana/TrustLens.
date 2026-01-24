
import sys
import os
from unittest.mock import MagicMock, patch

# Add the project root to sys.path
project_root = os.path.abspath(os.getcwd())
if project_root not in sys.path:
    sys.path.append(project_root)

from orchestrator.orchestrator import Orchestrator
from schemas.agent_output import AgentOutput, AgentType, RiskLevel
from schemas.final_report import FinalReport

def verify_orchestration():
    print("="*60)
    print("VERIFYING ORCHESTRATOR TASK DISTRIBUTION")
    print("="*60)

    # Configuration
    config = {
        "min_confidence": 0.7,
        "security_config": {"max_snippet_length": 500},
        "logic_config": {"max_snippet_length": 600},
        "quality_config": {
            "thresholds": {
                "max_function_length": 50,
                "max_file_length": 500,
                "min_comment_ratio": 0.1,
                "max_complexity": 10
            }
        },
        "decision_config": {"min_confidence": 0.7}
    }

    # Initialize Orchestrator
    # We'll use real classes but mock their analyze methods to see what they receive
    with patch('agents.feature_agent.FeatureExtractionAgent.analyze') as mock_feature, \
         patch('agents.security_agent.SecurityAnalysisAgent.analyze') as mock_security, \
         patch('agents.logic_agent.LogicAnalysisAgent.analyze') as mock_logic, \
         patch('agents.code_quality_agent.CodeQualityAgent.analyze') as mock_quality, \
         patch('agents.decision_agent.DecisionAgent.recommend_action') as mock_decision:

        # Mock Feature Agent response
        # It needs to return a valid AgentOutput with features in metadata
        mock_feature.return_value = AgentOutput(
            agent_type=AgentType.FEATURE_EXTRACTION,
            success=True,
            confidence=1.0,
            findings=[],
            risk_level=RiskLevel.NONE,
            metadata={
                "features": {
                    "total_loc": 100,
                    "complexity_indicators": {
                        "nested_depth": 5,
                        "function_count": 10,
                        "class_count": 2
                    }
                }
            }
        )

        # Mock other agents to return successful but empty outputs
        mock_security.return_value = AgentOutput(
            agent_type=AgentType.SECURITY_ANALYSIS, 
            confidence=0.9, 
            findings=[], 
            risk_level=RiskLevel.LOW,
            metadata={},
            success=True
        )
        mock_logic.return_value = AgentOutput(
            agent_type=AgentType.LOGIC_ANALYSIS, 
            confidence=0.8, 
            findings=[], 
            risk_level=RiskLevel.NONE,
            metadata={},
            success=True
        )
        mock_quality.return_value = AgentOutput(
            agent_type=AgentType.CODE_QUALITY, 
            confidence=0.95, 
            findings=[], 
            risk_level=RiskLevel.NONE,
            metadata={},
            success=True
        )
        mock_decision.return_value = AgentOutput(
            agent_type=AgentType.DECISION, 
            confidence=1.0, 
            findings=[{"recommendation": "acceptable"}], 
            risk_level=RiskLevel.NONE, 
            metadata={"recommendation": "acceptable"},
            success=True
        )

        orchestrator = Orchestrator(config)
        
        # Override S3Reader to use mock mode and provide dummy snippets
        orchestrator.s3_reader.use_mock = True
        
        from schemas.code_snippet import CodeSnippet
        dummy_snippets = [
            CodeSnippet("file1.py", 1, 10, "code1", "ctx", 0.9, ["tag1"]),
            CodeSnippet("file2.py", 1, 10, "code2", "ctx", 0.8, ["tag2"]),
            CodeSnippet("file3.py", 1, 10, "code3", "ctx", 0.7, ["tag3"]),
            CodeSnippet("file4.py", 1, 10, "code4", "ctx", 0.6, ["tag4"]),
            CodeSnippet("file5.py", 1, 10, "code5", "ctx", 0.5, ["tag5"]),
            CodeSnippet("file6.py", 1, 10, "code6", "ctx", 0.4, ["tag6"]), # Extra to test clamping
        ]
        orchestrator.s3_reader.get_code_snippets = MagicMock(return_value=dummy_snippets)
        
        print("\nRunning analysis...")
        report = orchestrator.analyze_repository("https://github.com/test/repo", "s3://mock-bucket/test/")
        
        print("\nVerification Results:")
        
        # 1. Check Feature Agent call
        print(f"\n1. Feature Agent called: {mock_feature.called}")
        if mock_feature.called:
            args = mock_feature.call_args[0]
            print(f"   Received {len(args[0])} files from S3")

        # 2. Check Security Agent call
        print(f"2. Security Agent called: {mock_security.called}")
        if mock_security.called:
            features, snippets = mock_security.call_args[0]
            print(f"   Received curated features: {list(features.keys())}")
            print(f"   Received {len(snippets)} snippets")
            for i, s in enumerate(snippets):
                print(f"     Snippet {i+1}: {s.filename}:{s.start_line} (Tags: {s.tags})")

        # 3. Check Logic Agent call
        print(f"3. Logic Agent called: {mock_logic.called}")
        if mock_logic.called:
            features, snippets = mock_logic.call_args[0]
            print(f"   Received curated features: {list(features.keys())}")
            print(f"   Received {len(snippets)} snippets")
            for i, s in enumerate(snippets):
                print(f"     Snippet {i+1}: {s.filename}:{s.start_line} (Tags: {s.tags})")

        # 4. Check Quality Agent call
        print(f"4. Quality Agent called: {mock_quality.called}")
        if mock_quality.called:
            metrics = mock_quality.call_args[0][0]
            print(f"   Received metrics: {list(metrics.keys())}")

        # 5. Check Decision Agent call
        print(f"5. Decision Agent called: {mock_decision.called}")
        if mock_decision.called:
            outputs, confidence, conflicts = mock_decision.call_args[0]
            print(f"   Received {len(outputs)} agent outputs")
            print(f"   Overall confidence: {confidence:.2f}")

        print("\nFinal Report Generation:")
        print(f"   Report success: {report is not None}")
        print(f"   Action recommended: {report.action_recommended}")

if __name__ == "__main__":
    verify_orchestration()
