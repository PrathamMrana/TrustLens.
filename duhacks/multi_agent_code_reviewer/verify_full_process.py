
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
project_root = os.path.abspath(os.getcwd())
if project_root not in sys.path:
    sys.path.append(project_root)

from storage.git_s3_workflow import git_s3_workflow
from orchestrator.orchestrator import Orchestrator
from utils.logger import Logger

def verify_full_process():
    logger = Logger("FullVerification")
    logger.info("Starting Full Verification Process")
    
    # 1. Load Environment
    load_dotenv()
    
    # 2. Define target repository
    repo_url = "https://github.com/kavyacp123/test-demo.git"
    analysis_id = "test-demo-run"
    
    print("\n" + "="*80)
    print(f"STEP 1: CLONE & UPLOAD TO S3 - {repo_url}")
    print("="*80)
    
    # Process Git to S3 Workflow
    # This clones, extracts snippets, and uploads to S3
    workflow_result = git_s3_workflow.process_git_repository(
        repo_url=repo_url,
        analysis_id=analysis_id,
        branch="main",
        extract_snippets=True
    )
    
    if workflow_result["status"] != "COMPLETED":
        logger.error(f"Workflow failed: {workflow_result.get('error')}")
        print(f"\n❌ Workflow Failed: {workflow_result.get('error')}")
        return

    s3_path = workflow_result["s3_path"]
    print(f"\n✅ S3 Upload Successful: {s3_path}")
    print(f"📊 Snippets Extracted: {workflow_result['statistics']['snippets_extracted']}")
    
    print("\n" + "="*80)
    print("STEP 2: RUN ORCHESTRATOR ANALYSIS")
    print("="*80)
    
    # Configuration for Orchestrator
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
    orchestrator = Orchestrator(config)
    
    # Crucial: Ensure Orchestrator uses the real S3 Reader (not mock if credentials available)
    # The S3Reader in Orchestrator will be initialized with the same AWS credentials
    
    try:
        # Run central analysis
        # RoutingPolicy will now fetch pre-extracted snippets from S3
        report = orchestrator.analyze_repository(repo_url, s3_path)
        
        print("\n" + "="*80)
        print("FINAL CODE REVIEW REPORT")
        print("="*80)
        print(f"\nRepository: {report.repository_url}")
        print(f"Overall Confidence: {report.overall_confidence:.2f}")
        print(f"Overall Risk Level: {report.overall_risk_level.value}")
        print(f"\nRecommendation: {report.recommendation}")
        print(f"Action: {report.action_recommended}")
        
        print(f"\nAgent Analysis Summary ({len(report.agent_outputs)} agents):")
        for output in report.agent_outputs:
            print(f"\n  EXPERTS: {output.agent_type.value.upper()}")
            print(f"    - Success: {output.success}")
            print(f"    - Confidence: {output.confidence:.2f}")
            
            # Print Snippets used (from metadata)
            if "snippet_locations" in output.metadata and "snippets" in output.metadata:
                print(f"    - Snippets Evaluated:")
                for loc, content in zip(output.metadata["snippet_locations"], output.metadata["snippets"]):
                    print(f"       • LOCATION: {loc}")
                    print(f"         CODE:")
                    print("-" * 30)
                    for line in content.splitlines()[:5]: # Show first 5 lines
                        print(f"         {line}")
                    if len(content.splitlines()) > 5:
                        print(f"         ...")
                    print("-" * 30)
            
            # Print Findings
            if output.findings:
                print(f"    - Detailed Findings:")
                for i, finding in enumerate(output.findings, 1):
                    # Handle different finding formats for different agents
                    desc = finding.get("description") or finding.get("reasoning") or finding.get("issue")
                    sev = finding.get("severity") or finding.get("risk_level")
                    print(f"       {i}. [{str(sev).upper()}] {desc}")
            else:
                print(f"    - Findings: No issues detected.")
        
        # Save report
        report_file = "full_verification_report.json"
        with open(report_file, "w") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)
        
        print("\n" + "="*80)
        print(f"SUCCESS: Full process verified and report saved to {report_file}")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Analysis Failed: {e}", exception=e)
        print(f"\n❌ Analysis Failed: {str(e)}")

if __name__ == "__main__":
    verify_full_process()
