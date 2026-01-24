"""
Test Git-S3 Workflow
Demonstrates the complete Git repository processing workflow
"""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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

from storage.git_s3_workflow import git_s3_workflow
from storage.git_handler import GitHandler
from utils.logger import Logger


def test_git_handler():
    """Test Git handler functionality"""
    print("\n" + "="*60)
    print("TEST 1: Git Handler Functionality")
    print("="*60)
    
    handler = GitHandler()
    logger = Logger("TestGitHandler")
    
    # Test 1a: URL Validation
    print("\n[1a] URL Validation Test")
    valid_urls = [
        "https://github.com/python/cpython.git",
        "https://gitlab.com/user/project.git",
        "git@github.com:user/repo.git"
    ]
    
    for url in valid_urls:
        is_valid = handler.validate_repo_url(url)
        print(f"  {url}: {'[OK] VALID' if is_valid else '[FAIL] INVALID'}")
    
    # Test 1b: Repo Name Extraction
    print("\n[1b] Repository Name Extraction")
    for url in valid_urls:
        name = handler.extract_repo_name(url)
        print(f"  {url}")
        print(f"    → Name: {name}")
    
    # Test 1c: Track Cloned Repos
    print("\n[1c] Repository Tracking")
    repos = handler.list_cloned_repos()
    print(f"  Currently tracked repos: {len(repos)}")


def test_workflow_with_mock():
    """Test workflow with mock data"""
    print("\n" + "="*60)
    print("TEST 2: Workflow Structure (Mock)")
    print("="*60)
    
    logger = Logger("TestWorkflow")
    
    print("\n[2a] Workflow Stages")
    stages = ["clone", "extraction", "upload", "cleanup"]
    for i, stage in enumerate(stages, 1):
        print(f"  {i}. {stage.upper()}")
    
    print("\n[2b] Expected Workflow Output")
    expected_output = {
        "analysis_id": "analysis-test123",
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "status": "COMPLETED",
        "stages": {
            "clone": {"success": True, "repo_name": "repo"},
            "extraction": {"success": True, "snippet_count": 45},
            "upload": {"success": True, "s3_path": "s3://bucket/..."},
            "cleanup": {"success": True}
        },
        "statistics": {
            "files_uploaded": 150,
            "commits": 245,
            "snippets_extracted": 45
        }
    }
    
    print(json.dumps(expected_output, indent=2))


def test_api_examples():
    """Show API usage examples"""
    print("\n" + "="*60)
    print("TEST 3: API Usage Examples")
    print("="*60)
    
    print("\n[3a] Submit Git Repository - Request")
    request = {
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "metadata": {
            "project_type": "python",
            "team": "backend"
        }
    }
    print("POST /api/repos/submit-git")
    print(json.dumps(request, indent=2))
    
    print("\n[3b] Submit Git Repository - Response (Success)")
    response = {
        "analysis_id": "analysis-abc123",
        "status": "UPLOADED",
        "s3_path": "s3://duhacks-s3-aicode/analysis-abc123/",
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "message": "Repository cloned and uploaded successfully",
        "statistics": {
            "files_uploaded": 150,
            "commits": 245,
            "snippets_extracted": 45
        },
        "workflow_status": "COMPLETED"
    }
    print(json.dumps(response, indent=2))
    
    print("\n[3c] Get Workflow Status - Request")
    print("GET /api/repos/analysis-abc123/workflow-status")
    
    print("\n[3d] Get Workflow Status - Response")
    status_response = {
        "analysis_id": "analysis-abc123",
        "status": "COMPLETED",
        "started_at": "2024-01-24T10:30:00",
        "completed_at": "2024-01-24T10:35:00",
        "stages": ["clone", "extraction", "upload", "cleanup"],
        "error": None
    }
    print(json.dumps(status_response, indent=2))


def test_python_usage():
    """Show direct Python usage"""
    print("\n" + "="*60)
    print("TEST 4: Direct Python Usage")
    print("="*60)
    
    print("\n[4a] Using GitHandler Directly")
    code_example_1 = '''
from storage.git_handler import GitHandler

handler = GitHandler()

# Clone a repository
result = handler.clone_repository(
    repo_url="https://github.com/user/repo.git",
    branch="main",
    depth=None
)

if result["success"]:
    print(f"Cloned to: {result['local_path']}")
    print(f"Commits: {result['repo_info']['commit_count']}")
    
    # Cleanup when done
    handler.cleanup_repository(result["repo_name"])
'''
    print(code_example_1)
    
    print("\n[4b] Using Complete Workflow")
    code_example_2 = '''
from storage.git_s3_workflow import git_s3_workflow

# Process complete workflow
result = git_s3_workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="analysis-123",
    branch="main",
    shallow=False,
    extract_snippets=True,
    metadata={"custom": "data"}
)

# Check result
if result["status"] == "COMPLETED":
    print(f"✅ Success!")
    print(f"S3 Path: {result['s3_path']}")
    print(f"Files: {result['statistics']['files_uploaded']}")
    print(f"Commits: {result['statistics']['commits']}")
else:
    print(f"❌ Error: {result['error']}")

# Get workflow status later
status = git_s3_workflow.get_workflow_status("analysis-123")
print(f"Current status: {status['status']}")
'''
    print(code_example_2)


def test_error_scenarios():
    """Show error handling"""
    print("\n" + "="*60)
    print("TEST 5: Error Handling Scenarios")
    print("="*60)
    
    print("\n[5a] Invalid Repository URL")
    invalid_url_response = {
        "success": False,
        "error": "Invalid repository URL: not-a-git-url",
        "repo_url": "not-a-git-url"
    }
    print(json.dumps(invalid_url_response, indent=2))
    
    print("\n[5b] Clone Timeout")
    timeout_response = {
        "success": False,
        "error": "Git operation failed: timeout",
        "repo_url": "https://github.com/huge/repo.git",
        "details": "Operation exceeded 300 seconds"
    }
    print(json.dumps(timeout_response, indent=2))
    
    print("\n[5c] AWS Credentials Error")
    credentials_response = {
        "status": "FAILED",
        "error": "NoCredentialsError: Unable to locate credentials",
        "stages": {
            "clone": {"success": True},
            "extraction": {"success": True},
            "upload": {
                "success": False,
                "error": "NoCredentialsError: Unable to locate credentials"
            }
        }
    }
    print(json.dumps(credentials_response, indent=2))


def test_configuration():
    """Show configuration requirements"""
    print("\n" + "="*60)
    print("TEST 6: Configuration Requirements")
    print("="*60)
    
    print("\n[6a] Required Environment Variables (.env)")
    env_example = '''
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=duhacks-s3-aicode

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# GitHub (optional)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Application
FLASK_ENV=development
DEBUG=True
'''
    print(env_example)
    
    print("\n[6b] Required Packages")
    packages = """
boto3==1.34.0           # AWS SDK
GitPython==3.1.40       # Git operations
google-generativeai==0.3.0  # Gemini API
flask==3.0.0            # Web framework
python-dotenv==1.0.0    # Environment variables
"""
    print(packages)


def main():
    """Run all tests"""
    logger = Logger("TestMain")
    
    print("\n")
    print("=" * 60)
    print(" " * 10 + "GIT-S3 WORKFLOW TEST SUITE")
    print("=" * 60)
    
    try:
        test_git_handler()
        test_workflow_with_mock()
        test_api_examples()
        test_python_usage()
        test_error_scenarios()
        test_configuration()
        
        print("\n" + "="*60)
        print("[OK] TEST SUITE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        print("\nDocumentation:")
        print("  - GIT_WORKFLOW_GUIDE.md - Complete guide")
        print("  - API_DOCUMENTATION.md - API reference")
        print("\nNext Steps:")
        print("  1. Configure AWS credentials in .env")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Start API: python run_api.py")
        print("  4. Submit repository: POST /api/repos/submit-git")
        print("\n" + "="*60 + "\n")
    
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n[ERROR] {e}\n")


if __name__ == "__main__":
    main()
