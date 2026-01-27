"""
Git Repository Handler
Manages Git operations: clone, pull, branch handling
"""

import os
import shutil
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from utils.logger import Logger

try:
    import git
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class GitHandler:
    """
    Handles Git operations for repository cloning and management.
    Supports GitHub, GitLab, Bitbucket, and self-hosted Git servers.
    """

    def __init__(self, base_temp_dir: Optional[str] = None):
        self.logger = Logger("GitHandler")

        # Writable directory (Render-safe)
        self.base_temp_dir = base_temp_dir or "/tmp/trustlens_repos"

        try:
            os.makedirs(self.base_temp_dir, exist_ok=True)
            self.logger.info(f"📂 Git workspace ready at: {self.base_temp_dir}")
        except Exception as e:
            self.logger.warning(
                f"⚠️ Could not create custom temp dir: {e}. Falling back to system temp."
            )
            self.base_temp_dir = tempfile.gettempdir()

        self.cloned_repos: Dict[str, Dict[str, Any]] = {}

        if not GIT_AVAILABLE:
            self.logger.warning("⚠️ GitPython not installed")

        self._check_git_installed()

    # ------------------------------------------------------------------
    # Environment checks
    # ------------------------------------------------------------------
    def _check_git_installed(self) -> bool:
        try:
            import subprocess

            result = subprocess.run(
                ["git", "--version"], capture_output=True, timeout=5
            )
            if result.returncode == 0:
                self.logger.info(
                    f"✅ Git available: {result.stdout.decode().strip()}"
                )
                return True
            self.logger.error("❌ Git command failed")
            return False
        except FileNotFoundError:
            self.logger.error("❌ Git is NOT installed or not in PATH")
            return False
        except Exception as e:
            self.logger.warning(f"⚠️ Git check failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def validate_repo_url(self, repo_url: str) -> bool:
        valid_prefixes = (
            "https://",
            "ssh://",
            "git@github.com:",
            "git@gitlab.com:",
            "git@bitbucket.org:",
        )

        valid = repo_url.startswith(valid_prefixes)
        if valid:
            self.logger.info(f"✅ Valid Git URL: {repo_url}")
        else:
            self.logger.error(f"❌ Invalid Git URL: {repo_url}")
        return valid

    def extract_repo_name(self, repo_url: str) -> str:
        name = repo_url.rstrip("/").split("/")[-1]
        return name.replace(".git", "")

    # ------------------------------------------------------------------
    # Clone logic
    # ------------------------------------------------------------------
    def clone_repository(
        self,
        repo_url: str,
        branch: str = "main",
        depth: Optional[int] = None,
        timeout: int = 300,
    ) -> Dict[str, Any]:

        if not GIT_AVAILABLE:
            return {"success": False, "error": "GitPython not installed", "repo_url": repo_url}

        if not self.validate_repo_url(repo_url):
            return {"success": False, "error": "Invalid repository URL", "repo_url": repo_url}

        repo_name = self.extract_repo_name(repo_url)
        safe_name = "".join(c for c in repo_name if c.isalnum() or c in ("-", "_"))
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        clone_dir = os.path.join(self.base_temp_dir, f"repo-{safe_name}-{timestamp}")

        raw_token = os.environ.get("GITHUB_TOKEN")
        token = raw_token.strip() if raw_token else None

        # ✅ GitHub auth format
        if token and "github.com" in repo_url:
            auth_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
        else:
            auth_url = repo_url

        # Retry logic for network flakiness
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔄 Clone attempt {attempt + 1}/{max_retries} for {repo_name}...")
                
                clone_kwargs = {
                    "to_path": clone_dir,
                    "branch": branch,
                    "progress": GitProgress(self.logger),
                    "env": {"GIT_TERMINAL_PROMPT": "0"} 
                }

                if depth:
                    clone_kwargs["depth"] = depth

                repo = Repo.clone_from(auth_url, **clone_kwargs)
                
                if os.path.exists(clone_dir):
                    repo_info = self._get_repo_info(repo, clone_dir)
                    self.cloned_repos[repo_name] = {
                        "local_path": clone_dir,
                        "repo_url": repo_url,
                        "branch": branch,
                        "cloned_at": timestamp,
                    }
                    self.logger.info(f"✅ Successfully cloned: {repo_name}")
                    return {
                        "success": True,
                        "repo_name": repo_name,
                        "local_path": clone_dir,
                        "repo_url": repo_url,
                        "branch": branch,
                        "repo_info": repo_info,
                    }

            except git.exc.GitCommandError as e:
                import time
                stderr = getattr(e, "stderr", "") or str(e)
                last_error = self._diagnose_git_error(stderr.replace(token, "***") if token else stderr)
                self.logger.warning(f"⚠️ Attempt {attempt + 1} failed: {last_error}")
                self._cleanup_dir(clone_dir)
                if attempt < max_retries - 1:
                    time.sleep(2) # Wait before retry
            except Exception as e:
                self.logger.error(f"❌ Critical clone error: {e}")
                break

        return {
            "success": False,
            "error": last_error or "Clone failed after multiple attempts",
            "repo_url": repo_url
        }

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def _diagnose_git_error(self, error: str) -> str:
        err = error.lower()
        if "authentication" in err or "403" in err or "401" in err:
            return "Authentication failed – check GITHUB_TOKEN and scopes"
        if "not found" in err or "404" in err:
            return "Repository or branch not found"
        if "exit code(128)" in err:
            return "Git error 128 – usually auth, branch, or network issue"
        return f"Git operation failed: {error[:100]}..."

    # ------------------------------------------------------------------
    # Repo info
    # ------------------------------------------------------------------
    def _get_repo_info(self, repo: Repo, repo_path: str) -> Dict[str, Any]:
        try:
            commit_count = sum(1 for _ in repo.iter_commits(repo.active_branch))
            file_count = sum(len(files) for _, _, files in os.walk(repo_path))
            commit = repo.head.commit

            return {
                "commit_count": commit_count,
                "file_count": file_count,
                "latest_commit": commit.hexsha[:7],
                "latest_author": commit.author.name,
                "latest_message": commit.message.split("\n")[0],
                "active_branch": repo.active_branch.name,
            }
        except Exception as e:
            self.logger.warning(f"⚠️ Repo info incomplete: {e}")
            return {"file_count": 0}

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup_repository(self, repo_name: str, force: bool = False) -> bool:
        repo = self.cloned_repos.get(repo_name)
        if not repo:
            return False

        success = self._cleanup_dir(repo["local_path"])
        if success:
            del self.cloned_repos[repo_name]
        return success

    def cleanup_all(self) -> bool:
        ok = True
        for name in list(self.cloned_repos.keys()):
            if not self.cleanup_repository(name):
                ok = False
        return ok

    def _cleanup_dir(self, directory: str) -> bool:
        try:
            if directory and os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
                self.logger.info(f"🧹 Deleted: {directory}")
            return True
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return False


# ----------------------------------------------------------------------
# Progress logger
# ----------------------------------------------------------------------
class GitProgress(git.RemoteProgress):
    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger

    def update(self, op_code, cur_count, max_count=None, message=""):
        if message:
            self.logger.info(f"Git: {message}")
