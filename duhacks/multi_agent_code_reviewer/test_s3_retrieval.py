import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from storage.s3_reader import S3Reader
from storage.s3_uploader import S3Uploader
from schemas.code_snippet import CodeSnippet

def test_retrieval():
    print("="*60)
    print("TESTING S3 SNIPPET RETRIEVAL")
    print("="*60)
    
    project_name = "test-retrieval-project"
    analysis_id = "test-analysis-999"
    
    # 1. Setup: Upload some dummy snippets first
    print("\n1. Seeding S3 with test data...")
    uploader = S3Uploader()
    
    # Create manual snippets
    snippet1 = CodeSnippet(
        filename="auth.js",
        start_line=10,
        end_line=15,
        content="function login() { eval(input); }",
        context="function login",
        relevance_score=0.9,
        tags=["security", "eval"]
    )
    
    snippet2 = CodeSnippet(
        filename="db.py",
        start_line=20,
        end_line=25,
        content="cursor.execute(f'SELECT * FROM {table}')",
        context="function query",
        relevance_score=0.8,
        tags=["security", "sql"]
    )
    
    snippets = {
        "security": [snippet1, snippet2]
    }
    
    # Upload
    uploader.upload_categorized_snippets(snippets, project_name, analysis_id)
    
    # 2. Test Retrieval
    print("\n2. Retrieving snippets via S3Reader...")
    reader = S3Reader()
    
    # Construct s3 path (mock or real)
    s3_path = f"s3://{reader.bucket_name}/{project_name}/"
    
    formatted_context = reader.get_snippets(s3_path, "security")
    
    print("\n--- RETRIEVED CONTEXT START ---")
    print(formatted_context)
    print("--- RETRIEVED CONTEXT END ---")
    
    if "auth.js" in formatted_context and "db.py" in formatted_context:
        print("\n✅ SUCCESS: Retrieved and formatted both snippets.")
    else:
        print("\n❌ FAILED: Missing content.")

if __name__ == "__main__":
    test_retrieval()
