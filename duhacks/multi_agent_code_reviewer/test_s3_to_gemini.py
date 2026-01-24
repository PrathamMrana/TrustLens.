import sys
import os
import json

# Add the project root to python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.s3_reader import S3Reader
from llm.gemini_client import GeminiClient
from utils.logger import Logger

def main():
    logger = Logger("S3ToGeminiTest")
    
    # Initialize components
    logger.info("Initializing S3 Reader and Gemini Client...")
    s3_reader = S3Reader()
    gemini = GeminiClient()
    
    # We'll use a test path. If mock is enabled, it returns mock code.
    # If real S3 is used, it will try to find snippets.
    test_s3_path = "s3://duhacks-s3-aicode/test-project/"
    
    logger.info(f"Retrieving snippets from {test_s3_path}...")
    
    # Get security snippets
    # Note: in mock mode, get_snippets might need a bit of adjustment or it will return empty if files aren't found
    # Actually S3Reader.get_snippets calls _read_from_s3 which falls back to mock if no files found.
    # But _mock_read_snapshot returns {filename: content} of full files, not snippet JSONs.
    
    # Let's try to get full files if we are in mock mode for a better demo
    if s3_reader.use_mock:
        logger.info("MOCK mode detected. Retrieving mock files instead of snippets.")
        files = s3_reader.read_code_snapshot(test_s3_path)
        
        # Combine files into a prompt context
        context = ""
        for filename, content in files.items():
            context += f"FILE: {filename}\nCODE:\n{content}\n" + "-"*20 + "\n"
    else:
        # Real S3 mode
        logger.info("REAL S3 mode. Attempting to get snippets...")
        context = s3_reader.get_snippets(test_s3_path, "security")
        if not context:
            logger.warning("No snippets found. Falling back to reading full snapshot.")
            files = s3_reader.read_code_snapshot(test_s3_path)
            context = ""
            for filename, content in files.items():
                context += f"FILE: {filename}\nCODE:\n{content}\n" + "-"*20 + "\n"

    if not context:
        logger.error("No code content retrieved to analyze.")
        return

    # Call Gemini
    logger.info("Sending code to Gemini for analysis...")
    
    # Create a prompt
    prompt = f"""
    Analyze the following code for security vulnerabilities. 
    Return a JSON response with a list of findings, each having 'type', 'severity', 'description', and 'line'.
    
    CODE TO ANALYZE:
    {context}
    """
    
    # Since gemini_client.py generate() is ALSO mocked, it will return mock findings if "SECURITY" is in prompt.
    response = gemini.generate(prompt)
    
    logger.info("Analysis Complete!")
    print("\n" + "="*50)
    print("ANALYSIS RESULTS:")
    print("="*50)
    print(json.dumps(response, indent=2))
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
