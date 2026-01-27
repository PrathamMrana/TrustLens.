
import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Mock .env if not found (for CI/CD or environments without real S3)
def setup_mock_env():
    if not os.path.exists(".env"):
        print("⚠️  No .env file found. Setting up mock environment variables.")
        os.environ["S3_BUCKET_NAME"] = "mock-bucket"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["GITHUB_TOKEN"] = "" # Use public if none
        os.environ["GEMINI_API_KEY"] = "mock-key"

setup_mock_env()
load_dotenv()

from api.controllers import CodeReviewController
from utils.logger import Logger

def run_test(repo_url):
    logger = Logger("RealRepoTest")
    controller = CodeReviewController()
    
    print("\n" + "="*80)
    print(f"🚀 TESTING FULL WORKFLOW FOR: {repo_url}")
    print("="*80)
    
    try:
        # 1. Start Clone & Auto-Analysis
        print("\nStep 1: Triggering Clone & Auto-Analysis...")
        result = controller.clone_from_github(repo_url)
        analysis_id = result["analysis_id"]
        
        print(f"✅ Triggered successfully!")
        print(f"🆔 Analysis ID: {analysis_id}")
        print(f"📁 S3 Path: {result['s3_path']}")
        
        # 2. Wait for background analysis to finish (stateless check)
        print("\nStep 2: Polling for completion...")
        import time
        max_retries = 30
        for i in range(max_retries):
            status = controller.get_analysis_status(analysis_id)
            print(f"  [{i+1}/{max_retries}] Status: {status['status']} ({status.get('progress', 0)}%)")
            
            if status["status"] == "COMPLETED":
                print("✅ Analysis COMPLETED!")
                break
            elif status["status"] == "FAILED":
                print(f"❌ Analysis FAILED: {status.get('error')}")
                return
            
            time.sleep(2)
        else:
            print("⏳ Timeout waiting for analysis.")
            return

        # 3. Fetch Final Report
        print("\nStep 3: Fetching Detailed Report...")
        report = controller.get_detailed_report(analysis_id)
        
        if report:
            print("\n" + "-"*40)
            print("📋 REPORT SUMMARY")
            print("-"*40)
            print(f"Final Decision: {report['final_decision']}")
            print(f"Overall Risk: {report['overall_risk_level']}")
            print(f"Confidence: {report['overall_confidence']:.2f}")
            print(f"Security Findings: {len(report['security_findings'])}")
            print(f"Logic Findings: {len(report['logic_findings'])}")
            print("-"*40)
            
            if report['security_findings']:
                print("\nTop Security Finding:")
                f = report['security_findings'][0]
                print(f"  - [{f.get('type')}] {f.get('description')}")
        else:
            print("❌ Could not fetch report.")

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    repo = "https://github.com/kavyacp123/TrustLens.git"
    run_test(repo)
