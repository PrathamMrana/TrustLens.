
import os
import sys
from storage.git_handler import GitHandler
from utils.logger import Logger

def test_git():
    handler = GitHandler()
    repo_url = "https://github.com/kavyacp123/trend-pulse-spark.git"
    print(f"Testing clone of {repo_url}...")
    result = handler.clone_repository(repo_url=repo_url, branch="main", depth=1)
    if result["success"]:
        print(f"✅ Success! Cloned to {result['local_path']}")
        handler.cleanup_repository(result["repo_name"])
    else:
        print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    test_git()
