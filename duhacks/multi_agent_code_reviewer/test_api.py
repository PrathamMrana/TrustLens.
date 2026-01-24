"""
Test Script for REST API
Quick test to verify all endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("1️⃣ Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_api_health():
    """Test API health endpoint"""
    print("\n" + "="*60)
    print("2️⃣ Testing API Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_github_clone():
    """Test GitHub clone endpoint"""
    print("\n" + "="*60)
    print("3️⃣ Testing GitHub Clone")
    print("="*60)
    
    data = {
        "repo_url": "https://github.com/example/repo",
        "branch": "main"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/repos/from-github",
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json().get("analysis_id")
    return None

def test_start_analysis(analysis_id):
    """Test start analysis endpoint"""
    print("\n" + "="*60)
    print("4️⃣ Starting Analysis")
    print("="*60)
    
    data = {
        "analysis_id": analysis_id,
        "config": {
            "min_confidence": 0.7
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/analysis/start",
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 202

def test_get_status(analysis_id):
    """Test status endpoint"""
    print("\n" + "="*60)
    print("5️⃣ Checking Analysis Status")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/status/{analysis_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_get_report(analysis_id):
    """Test report endpoint"""
    print("\n" + "="*60)
    print("6️⃣ Getting Analysis Report")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/report/{analysis_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        report = response.json()
        print(f"\n📊 REPORT SUMMARY:")
        print(f"  Final Decision: {report.get('final_decision')}")
        print(f"  Overall Confidence: {report.get('overall_confidence'):.2f}")
        print(f"  Risk Level: {report.get('overall_risk_level')}")
        print(f"  Disagreement: {report.get('disagreement_detected')}")
        print(f"  Deferred: {report.get('deferred')}")
        
        security = report.get('security_findings', [])
        print(f"\n  Security Findings: {len(security)}")
        for finding in security[:2]:
            print(f"    - {finding.get('type')}: {finding.get('severity')}")
        
        logic = report.get('logic_findings', [])
        print(f"\n  Logic Findings: {len(logic)}")
        for finding in logic[:2]:
            print(f"    - {finding.get('issue')}: {finding.get('severity')}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_agents(analysis_id):
    """Test agent details endpoint"""
    print("\n" + "="*60)
    print("7️⃣ Getting Agent Details")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/agents/{analysis_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        agents = data.get('agents', [])
        print(f"\n🤖 AGENTS ({len(agents)}):")
        for agent in agents:
            print(f"  - {agent.get('agent')}")
            print(f"    Confidence: {agent.get('confidence'):.2f}")
            print(f"    Risk: {agent.get('risk_level')}")
            print(f"    Findings: {agent.get('findings_count')}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_reliability(analysis_id):
    """Test reliability endpoint"""
    print("\n" + "="*60)
    print("8️⃣ Getting Reliability Metrics")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/reliability/{analysis_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🔒 RELIABILITY:")
        print(f"  Confidence Level: {data.get('confidence_level')}")
        print(f"  Overall Confidence: {data.get('overall_confidence'):.2f}")
        print(f"  Disagreement: {data.get('disagreement')}")
        print(f"  Safe to Automate: {data.get('safe_to_automate')}")
        print(f"  Conflicts: {data.get('conflict_count')}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_analyses():
    """Test list analyses endpoint"""
    print("\n" + "="*60)
    print("9️⃣ Listing All Analyses")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/list?limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 Total Analyses: {data.get('total')}")
        for analysis in data.get('analyses', []):
            print(f"  - {analysis.get('analysis_id')}: {analysis.get('status')}")
    else:
        print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("MULTI-AGENT CODE REVIEW API - TEST SUITE")
    print("🚀"*30)
    
    try:
        # Test 1: Health check
        if not test_health():
            print("\n❌ Health check failed!")
            return
        
        # Test 2: API health
        if not test_api_health():
            print("\n❌ API health check failed!")
            return
        
        # Test 3: Clone GitHub repo
        analysis_id = test_github_clone()
        if not analysis_id:
            print("\n❌ GitHub clone failed!")
            return
        
        print(f"\n✅ Got Analysis ID: {analysis_id}")
        
        # Test 4: Start analysis
        if not test_start_analysis(analysis_id):
            print("\n❌ Failed to start analysis!")
            return
        
        # Wait a moment for analysis
        print("\n⏳ Waiting for analysis to complete...")
        time.sleep(2)
        
        # Test 5: Check status
        status = test_get_status(analysis_id)
        
        # Test 6: Get report
        test_get_report(analysis_id)
        
        # Test 7: Get agent details
        test_get_agents(analysis_id)
        
        # Test 8: Get reliability
        test_get_reliability(analysis_id)
        
        # Test 9: List analyses
        test_list_analyses()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("Make sure the Flask server is running:")
        print("  python run_api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
