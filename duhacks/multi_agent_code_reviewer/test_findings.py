
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_detailed_findings():
    print("Testing detailed findings injection...")
    
    # 1. Ingest snippet
    code = """
def process_data(user_input):
    # Potential SQL injection
    query = "SELECT * FROM users WHERE id = " + user_input
    print(query)
    
    # Logic risk: infinite loop
    while True:
        if user_input:
            break
        # missing break for some paths
    
    return True
"""
    
    ingest_res = requests.post(f"{BASE_URL}/api/repos/snippet", json={
        "code": code,
        "language": "python"
    })
    
    analysis_id = ingest_res.json().get("analysis_id")
    print(f"Analysis ID: {analysis_id}")
    
    # 2. Start analysis
    requests.post(f"{BASE_URL}/api/analysis/start", json={"analysis_id": analysis_id})
    
    # 3. Wait and poll
    for _ in range(5):
        status = requests.get(f"{BASE_URL}/api/analysis/status/{analysis_id}").json()
        if status['status'] == 'COMPLETED':
            break
        print(f"Status: {status['status']}...")
        time.sleep(2)
        
    # 4. Get report and check findings
    report = requests.get(f"{BASE_URL}/api/analysis/report/{analysis_id}").json()
    
    print("\nSECURITY FINDINGS:")
    for f in report.get('security_findings', []):
        print(f"- {f.get('type')}: {f.get('filename')}:{f.get('line_number')}")
        print(f"  Code: {f.get('code')[:50]}...")
        
    print("\nLOGIC FINDINGS:")
    for f in report.get('logic_findings', []):
        print(f"- {f.get('type')}: {f.get('filename')}:{f.get('line_number')}")
        print(f"  Code: {f.get('code')[:50]}...")

    print("\nQUALITY SUMMARY FINDINGS:")
    for f in report.get('quality_summary', {}).get('findings', []):
        print(f"- {f.get('type')}: {f.get('filename')}:{f.get('line_number')}")

if __name__ == "__main__":
    test_detailed_findings()
