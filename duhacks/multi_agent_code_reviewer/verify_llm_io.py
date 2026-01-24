
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from unittest.mock import patch

# Add project root to sys.path
project_root = os.path.abspath(os.getcwd())
if project_root not in sys.path:
    sys.path.append(project_root)

from storage.git_s3_workflow import git_s3_workflow
from orchestrator.orchestrator import Orchestrator
from llm.gemini_client import GeminiClient
from utils.logger import Logger

def verify_llm_io():
    load_dotenv()
    logger = Logger("LLM_Inspection")
    
    repo_url = "https://github.com/kavyacp123/trend-pulse-spark.git"
    analysis_id = "inspect-llm-io"
    
    print("\n" + "="*80)
    print(f"STEP 1: PREPARING DATA FROM {repo_url}")
    print("="*80)
    
    workflow_result = git_s3_workflow.process_git_repository(
        repo_url=repo_url,
        analysis_id=analysis_id,
        extract_snippets=True
    )
    
    if workflow_result["status"] != "COMPLETED":
        print(f"❌ Setup Failed: {workflow_result.get('error')}")
        return

    s3_path = workflow_result["s3_path"]
    
    print("\n" + "="*80)
    print("STEP 2: INSPECTING LLM INPUTS & OUTPUTS")
    print("="*80)

    # We will wrap GeminiClient.generate to intercept and print calls
    original_generate = GeminiClient.generate

    def logging_generate(self, prompt, **kwargs):
        print("\n" + "-"*40)
        print(">>> [LLM INPUT PROMPT] >>>")
        print(prompt.strip())
        print("<<< [END PROMPT] <<<")
        
        response = original_generate(self, prompt, **kwargs)
        
        print("\n<<< [LLM OUTPUT RESPONSE] <<<")
        print(json.dumps(response, indent=2))
        print("-"*40)
        return response

    with patch.object(GeminiClient, 'generate', logging_generate):
        config = {
            "min_confidence": 0.7,
            "security_config": {"max_snippet_length": 500},
            "logic_config": {"max_snippet_length": 600},
        }
        orchestrator = Orchestrator(config)
        
        # This will trigger the Security and Logic agents
        # Since we patched GeminiClient, we will see every prompt they send
        report = orchestrator.analyze_repository(repo_url, s3_path)
        
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    verify_llm_io()
