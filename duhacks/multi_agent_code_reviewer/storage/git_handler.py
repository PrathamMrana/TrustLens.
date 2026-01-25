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
    
    class GitProgress(git.RemoteProgress):
        """Progress handler for Git operations"""
        
        def __init__(self, logger: Logger):
            super().__init__()
            self.logger = logger
        
        def update(self, op_code, cur_count, max_count=None, message=''):
            """Update progress"""
            if message:
                self.logger.info(f"Git: {message}")
                
except ImportError:
    GIT_AVAILABLE = False
    GitProgress = None  # Define as None when git is not available



class GitHandler:
    """
    Handles Git operations for repository cloning and management.
    Supports GitHub, GitLab, Bitbucket, and self-hosted Git servers.
    """
    
    def __init__(self, base_temp_dir: Optional[str] = None):
        """
        Initialize Git handler.
        
        Args:
            base_temp_dir: Base directory for temporary clones (uses system temp if None)
        """
        self.logger = Logger("GitHandler")
        self.base_temp_dir = base_temp_dir or tempfile.gettempdir()
        self.cloned_repos = {}  # Track cloned repositories
        
        if not GIT_AVAILABLE:
            self.logger.warning("GitPython not installed - some features will be limited")
    
    def validate_repo_url(self, repo_url: str) -> bool:
        """
        Validate Git repository URL format.
        
        Args:
            repo_url: Repository URL to validate
        
        Returns:
            True if valid, False otherwise
        """
        # Check if it's a valid Git URL
        valid_patterns = [
            'https://github.com/',
            'https://gitlab.com/',
            'https://bitbucket.org/',
            'git@github.com:',
            'git@gitlab.com:',
            'git@bitbucket.org:',
            'https://',
            'ssh://',
            'git://'
        ]
        
        is_valid = any(repo_url.startswith(pattern) for pattern in valid_patterns)
        
        if is_valid:
            self.logger.info(f"✅ Valid Git URL: {repo_url}")
        else:
            self.logger.error(f"❌ Invalid Git URL format: {repo_url}")
        
        return is_valid
    
    def extract_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from URL.
        
        Args:
            repo_url: Repository URL
        
        Returns:
            Repository name
        """
        # Handle both HTTPS and SSH URLs
        name = repo_url.rstrip('/').split('/')[-1]
        name = name.replace('.git', '')
        return name
    
    def clone_repository(
        self,
        repo_url: str,
        branch: str = "main",
        depth: Optional[int] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Clone a Git repository.
        
        Args:
            repo_url: Repository URL (HTTPS or SSH)
            branch: Branch to clone (default: main)
            depth: Shallow clone depth (for large repos)
            timeout: Operation timeout in seconds
        
        Returns:
            Dictionary with clone results
        """
        if not GIT_AVAILABLE:
            return {
                "success": False,
                "error": "GitPython not installed. Install with: pip install GitPython",
                "repo_url": repo_url
            }
        
        # Validate URL
        if not self.validate_repo_url(repo_url):
            return {
                "success": False,
                "error": f"Invalid repository URL: {repo_url}",
                "repo_url": repo_url
            }
        
        repo_name = self.extract_repo_name(repo_url)
        clone_dir = os.path.join(self.base_temp_dir, f"repo-{repo_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        try:
            self.logger.info(f"🔄 Starting clone: {repo_url}")
            self.logger.info(f"📁 Clone destination: {clone_dir}")
            
            # Prepare clone options
            clone_kwargs = {
                'to_path': clone_dir,
                'branch': branch,
                'progress': GitProgress(self.logger)
            }
            
            if depth:
                clone_kwargs['depth'] = depth
            
            # Clone repository
            repo = Repo.clone_from(repo_url, **clone_kwargs)
            
            # Verify clone
            if not os.path.exists(clone_dir):
                raise ValueError("Clone directory not created")
            
            # Get repo info
            repo_info = self._get_repo_info(repo, clone_dir)
            
            self.logger.info(f"✅ Successfully cloned: {repo_name}")
            self.logger.info(f"📊 Commits: {repo_info['commit_count']}, Files: {repo_info['file_count']}")
            
            # Track clone
            self.cloned_repos[repo_name] = {
                "url": repo_url,
                "local_path": clone_dir,
                "branch": branch,
                "cloned_at": datetime.now().isoformat(),
                "repo_info": repo_info
            }
            
            return {
                "success": True,
                "repo_name": repo_name,
                "local_path": clone_dir,
                "repo_url": repo_url,
                "branch": branch,
                "repo_info": repo_info,
                "message": f"Successfully cloned {repo_name}"
            }
        
        except git.exc.GitCommandError as e:
            self.logger.error(f"❌ Git command error: {e}")
            self._cleanup_dir(clone_dir)
            return {
                "success": False,
                "error": f"Git operation failed: {str(e)}",
                "repo_url": repo_url,
                "details": str(e)
            }
        
        except Exception as e:
            self.logger.error(f"❌ Clone failed: {e}")
            self._cleanup_dir(clone_dir)
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }
    
    def _get_repo_info(self, repo: 'Repo', repo_path: str) -> Dict[str, Any]:
        """
        Get repository information.
        
        Args:
            repo: GitPython Repo object
            repo_path: Local path to repository
        
        Returns:
            Repository information dictionary
        """
        try:
            # Count commits
            commit_count = sum(1 for _ in repo.iter_commits(repo.active_branch))
            
            # Count files and lines of code
            file_count = 0
            total_loc = 0
            language_extensions = {}
            
            for root, _, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in root:
                    continue
                    
                for file in files:
                    file_count += 1
                    file_path = os.path.join(root, file)
                    
                    # Count lines of code
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            total_loc += lines
                    except:
                        pass
                    
                    # Track language by extension
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        language_extensions[ext] = language_extensions.get(ext, 0) + 1
            
            # Map extensions to language names
            ext_to_lang = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.cs': 'C#',
                '.go': 'Go', '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift',
                '.kt': 'Kotlin', '.rs': 'Rust', '.html': 'HTML', '.css': 'CSS',
                '.jsx': 'React', '.tsx': 'TypeScript React', '.vue': 'Vue',
                '.json': 'JSON', '.xml': 'XML', '.yaml': 'YAML', '.yml': 'YAML',
                '.md': 'Markdown', '.sh': 'Shell', '.sql': 'SQL'
            }
            
            # Get top languages
            languages = []
            sorted_exts = sorted(language_extensions.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_exts[:5]:  # Top 5 languages
                lang_name = ext_to_lang.get(ext, ext[1:].upper() if ext else 'Unknown')
                languages.append(lang_name)
            
            # Get repository name from remote URL or path
            repo_name = "Unknown Repository"
            try:
                if repo.remote():
                    remote_url = repo.remote().url
                    repo_name = remote_url.rstrip('/').split('/')[-1].replace('.git', '')
                else:
                    repo_name = os.path.basename(repo_path)
            except:
                repo_name = os.path.basename(repo_path)
            
            # Get commit info
            latest_commit = repo.head.commit
            
            return {
                "commit_count": commit_count,
                "file_count": file_count,
                "total_loc": total_loc,
                "languages": languages,
                "repo_name": repo_name,
                "latest_commit": latest_commit.hexsha[:7],
                "latest_author": latest_commit.author.name,
                "latest_message": latest_commit.message.split('\n')[0],
                "active_branch": repo.active_branch.name,
                "remote_url": repo.remote().url if repo.remote() else None
            }
        except Exception as e:
            self.logger.warning(f"Could not get full repo info: {e}")
            # Return minimal info on error
            file_count = sum([len(files) for _, _, files in os.walk(repo_path) if '.git' not in _])
            return {
                "commit_count": 0,
                "file_count": file_count,
                "total_loc": 0,
                "languages": [],
                "repo_name": os.path.basename(repo_path),
                "latest_commit": "unknown",
                "latest_author": "unknown"
            }
    
    def get_clone_directory(self, repo_name: str) -> Optional[str]:
        """
        Get local path of cloned repository.
        
        Args:
            repo_name: Repository name
        
        Returns:
            Local path if exists, None otherwise
        """
        if repo_name in self.cloned_repos:
            return self.cloned_repos[repo_name]['local_path']
        return None
    
    def list_cloned_repos(self) -> Dict[str, Dict[str, Any]]:
        """
        List all cloned repositories.
        
        Returns:
            Dictionary of cloned repositories
        """
        return self.cloned_repos.copy()
    
    def cleanup_repository(self, repo_name: str, force: bool = False) -> bool:
        """
        Clean up cloned repository.
        
        Args:
            repo_name: Repository name to clean up
            force: Force cleanup even if errors occur
        
        Returns:
            True if successful, False otherwise
        """
        if repo_name not in self.cloned_repos:
            self.logger.warning(f"Repository not tracked: {repo_name}")
            return False
        
        repo_path = self.cloned_repos[repo_name]['local_path']
        
        if self._cleanup_dir(repo_path, force):
            del self.cloned_repos[repo_name]
            self.logger.info(f"✅ Cleaned up repository: {repo_name}")
            return True
        
        return False
    
    def _cleanup_dir(self, directory: str, force: bool = True) -> bool:
        """
        Delete a directory safely.
        
        Args:
            directory: Directory path to delete
            force: Force delete even if errors occur
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=force)
                self.logger.info(f"Deleted directory: {directory}")
            return True
        except Exception as e:
            self.logger.error(f"Could not delete directory {directory}: {e}")
            return False
    
    def cleanup_all(self) -> bool:
        """
        Clean up all cloned repositories.
        
        Returns:
            True if all cleaned successfully
        """
        all_success = True
        for repo_name in list(self.cloned_repos.keys()):
            if not self.cleanup_repository(repo_name):
                all_success = False
        
        return all_success
