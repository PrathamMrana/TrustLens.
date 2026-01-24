import os
import shutil
import json
from storage.snippet_extractor import SnippetExtractor
from storage.s3_uploader import S3Uploader

def create_dummy_repo(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    
    # Python file
    with open(os.path.join(path, "unsafe.py"), "w") as f:
        f.write("""
def run_command(cmd):
    import os
    os.system(cmd)  # Security risk
""")

    # Java file
    with open(os.path.join(path, "Service.java"), "w") as f:
        f.write("""
public class Service {
    public void exec(String cmd) {
        try {
            Runtime.getRuntime().exec(cmd);
        } catch(Exception e) {}
    }
}
""")

    # JS file
    with open(os.path.join(path, "app.js"), "w") as f:
        f.write("""
function init() {
    eval("console.log('loading')");
}
""")

def test_extraction_and_upload():
    print("="*60)
    print("TESTING FULL EXTRACTION & UPLOAD WORKFLOW")
    print("="*60)
    
    repo_path = "temp_multi_lang_repo"
    create_dummy_repo(repo_path)
    
    print(f"Created dummy repo at: {repo_path}")
    
    # 1. Extraction
    print("\n1. Running SnippetExtractor...")
    extractor = SnippetExtractor()
    snippets = extractor.extract_from_directory(repo_path)
    
    print(f"   Security Snippets: {len(snippets['security'])}")
    print(f"   Logic Snippets: {len(snippets['logic'])}")
    
    # 2. Upload to S3
    print("\n2. Uploading to S3...")
    uploader = S3Uploader()
    project_name = "test-multi-lang-project"
    analysis_id = "test-analysis-001"
    
    # Upload structure
    s3_base = uploader.upload_project_structure(repo_path, project_name, analysis_id)
    print(f"   Base S3 Path: {s3_base}")
    
    # Upload snippets
    uploader.upload_categorized_snippets(snippets, project_name, analysis_id)
    print("   Categorized snippets uploaded.")
    
    print("\n✅ SUCCESS: Workflow components validated.")

if __name__ == "__main__":
    test_extraction_and_upload()
