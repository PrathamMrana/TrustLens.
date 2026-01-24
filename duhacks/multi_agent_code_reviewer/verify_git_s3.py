import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_git_to_s3():
    print("=" * 60)
    print("TEST: Git Repo -> Clone -> S3 Upload")
    print("=" * 60)
    
    payload = {
        "repo_url": "https://github.com/octocat/Hello-World",
        "branch": "master"
    }
    
    print(f"Sending request to clone: {payload['repo_url']}")
    try:
        response = requests.post(f"{BASE_URL}/api/repos/from-github", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Success!")
            print(f"Analysis ID: {result.get('analysis_id')}")
            print(f"S3 Path: {result.get('s3_path')}")
            print(f"Workflow Status: {result.get('workflow_status')}")
            print("\nStatistics:")
            print(json.dumps(result.get('statistics', {}), indent=2))
            
            # Verify status
            analysis_id = result.get('analysis_id')
            status_response = requests.get(f"{BASE_URL}/api/repos/{analysis_id}/workflow-status")
            if status_response.status_code == 200:
                print("\nWorkflow Execution Details:")
                print(json.dumps(status_response.json(), indent=2))
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    test_git_to_s3()
