import sys
import os

# Add the project root to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.gemini_client import GeminiClient

def test_llm():
    print("Initializing Gemini Client...")
    client = GeminiClient(api_key="TEST_KEY")
    
    print("\nTest 1: Security Prompt")
    security_response = client.generate("Please analyze this code for SECURITY vulnerabilities")
    print(f"Response: {security_response}")
    
    print("\nTest 2: Logic Prompt")
    logic_response = client.generate("Please analyze this code for LOGIC errors")
    print(f"Response: {logic_response}")
    
    print("\nStatus: The LLM client runs successfully but is returning MOCK data.")

if __name__ == "__main__":
    test_llm()
