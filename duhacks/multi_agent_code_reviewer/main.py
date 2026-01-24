"""
Multi-Agent AI System for Risk-Aware Code Review
Main entry point for the system.
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from orchestrator.orchestrator import Orchestrator
from utils.logger import Logger

# Load .env file - search up the directory tree
def load_env_file():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).parent
    for _ in range(5):
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return
        current = current.parent

load_env_file()


def main():
    """
    Main entry point for code review system.
    """
    logger = Logger("Main")
    logger.info("Multi-Agent Code Review System Starting")
    
    # Configuration
    config = {
        "min_confidence": 0.7,
        "security_config": {
            "max_snippet_length": 500
        },
        "logic_config": {
            "max_snippet_length": 600
        },
        "quality_config": {
            "thresholds": {
                "max_function_length": 50,
                "max_file_length": 500,
                "min_comment_ratio": 0.1,
                "max_complexity": 10
            }
        },
        "decision_config": {
            "min_confidence": 0.7
        }
    }
    
    # Initialize orchestrator
    orchestrator = Orchestrator(config)
    
    # Example analysis
    # In production: get repo_url and s3_path from command line or API
    import os
    bucket = os.getenv("S3_BUCKET_NAME", "duhacks-s3-aicode")
    repo_url = "https://github.com/example/repo"
    s3_path = f"s3://{bucket}/repo-snapshot-2024/"
    
    logger.info(f"Analyzing repository: {repo_url}")
    logger.info(f"S3 snapshot: {s3_path}")
    
    # Run analysis
    try:
        report = orchestrator.analyze_repository(repo_url, s3_path)
        
        # Output report
        print("\n" + "="*80)
        print("CODE REVIEW REPORT")
        print("="*80)
        print(f"\nRepository: {report.repository_url}")
        print(f"S3 Path: {report.s3_snapshot_path}")
        print(f"Timestamp: {report.timestamp}")
        print(f"\nOverall Confidence: {report.overall_confidence:.2f}")
        print(f"Overall Risk Level: {report.overall_risk_level.value}")
        print(f"\nRecommendation: {report.recommendation}")
        print(f"Action: {report.action_recommended}")
        
        if report.deferred:
            print(f"\n⚠️  DEFERRED: {report.deferral_reason}")
        
        if report.conflicts:
            print(f"\n⚠️  CONFLICTS DETECTED: {len(report.conflicts)} conflicts")
            for i, conflict in enumerate(report.conflicts, 1):
                print(f"\n  Conflict {i}:")
                print(f"    Agents: {', '.join(conflict.agents_involved)}")
                print(f"    Disagreement: {conflict.disagreement_level:.2f}")
        
        print(f"\n\nAgent Outputs ({len(report.agent_outputs)}):")
        for output in report.agent_outputs:
            print(f"\n  - {output.agent_type.value}")
            print(f"    Success: {output.success}")
            print(f"    Confidence: {output.confidence:.2f}")
            print(f"    Risk Level: {output.risk_level.value}")
            print(f"    Findings: {len(output.findings)}")
            
            if output.findings:
                for finding in output.findings[:3]:  # Show first 3
                    print(f"      • {finding}")
        
        # Save report to JSON
        report_dict = report.to_dict()
        with open("code_review_report.json", "w") as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info("Report saved to code_review_report.json")
        
        print("\n" + "="*80)
        print("Report saved to: code_review_report.json")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error("Analysis failed", exception=e)
        print(f"\n❌ Analysis failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
