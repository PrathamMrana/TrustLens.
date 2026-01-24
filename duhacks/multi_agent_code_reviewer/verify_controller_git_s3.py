import sys
import os
import json
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load .env variables manually for this script
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from api.controllers import CodeReviewController
from utils.logger import Logger

def main():
    logger = Logger("TestScript")
    logger.info("=" * 60)
    logger.info("DIRECT CONTROLLER TEST: Git -> S3")
    logger.info("=" * 60)
    
    controller = CodeReviewController()
    
    repo_url = "https://github.com/octocat/Hello-World"
    branch = "master"
    
    logger.info(f"Cloning and uploading: {repo_url} (branch: {branch})")
    
    try:
        # This calls the full workflow: clone -> extract snippets -> upload to S3 -> cleanup
        result = controller.clone_from_github(repo_url, branch)
        
        logger.info("✅ SUCCESS!")
        print("\nResult Summary:")
        print(json.dumps(result, indent=2))
        
        # Check if snippets were created
        analysis_id = result.get('analysis_id')
        logger.info(f"Process completed with Analysis ID: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
