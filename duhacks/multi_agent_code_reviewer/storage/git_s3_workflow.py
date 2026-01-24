"""
Git to S3 Workflow
Complete orchestration of cloning Git repos and uploading to S3
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from storage.git_handler import GitHandler
from storage.s3_uploader import S3Uploader
from storage.snippet_extractor import SnippetExtractor
from utils.logger import Logger


class GitS3Workflow:
    """
    Complete workflow: Clone Git repo → Extract code → Upload to S3
    Handles all stages of Git repository processing
    """
    
    def __init__(self):
        """Initialize Git-S3 workflow components"""
        self.logger = Logger("GitS3Workflow")
        self.git_handler = GitHandler()
        self.s3_uploader = S3Uploader()
        self.snippet_extractor = SnippetExtractor()
        self.workflow_history = {}
    
    def process_git_repository(
        self,
        repo_url: str,
        analysis_id: str,
        branch: str = "main",
        shallow: bool = False,
        extract_snippets: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Clone → Extract → Upload to S3
        
        Args:
            repo_url: Git repository URL
            analysis_id: Unique analysis identifier
            branch: Branch to clone
            shallow: Use shallow clone (faster, less storage)
            extract_snippets: Extract code snippets for analysis
            metadata: Additional metadata to store with upload
        
        Returns:
            Complete workflow result
        """
        workflow_result = {
            "analysis_id": analysis_id,
            "repo_url": repo_url,
            "branch": branch,
            "status": "INITIALIZED",
            "stages": {},
            "started_at": datetime.now().isoformat()
        }
        
        try:
            # Stage 1: Clone Repository
            self.logger.info(f"🚀 Starting Git-S3 workflow for {analysis_id}")
            clone_result = self._stage_clone(repo_url, branch, shallow)
            workflow_result["stages"]["clone"] = clone_result
            
            if not clone_result["success"]:
                workflow_result["status"] = "FAILED"
                workflow_result["error"] = "Clone stage failed"
                return workflow_result
            
            local_repo_path = clone_result["local_path"]
            repo_info = clone_result.get("repo_info", {})
            
            # Stage 2: Extract Code Snippets (Optional)
            snippets = {}
            if extract_snippets:
                extraction_result = self._stage_extract_snippets(local_repo_path)
                workflow_result["stages"]["extraction"] = extraction_result
                snippets = extraction_result.get("snippets", {})
            
            # Stage 3: Upload to S3
            upload_result = self._stage_upload_to_s3(
                local_repo_path,
                analysis_id,
                repo_url,
                branch,
                repo_info,
                snippets,
                metadata
            )
            workflow_result["stages"]["upload"] = upload_result
            
            if not upload_result["success"]:
                workflow_result["status"] = "FAILED"
                workflow_result["error"] = "Upload stage failed"
                return workflow_result
            
            # Stage 4: Cleanup
            cleanup_result = self._stage_cleanup(clone_result.get("repo_name"))
            workflow_result["stages"]["cleanup"] = cleanup_result
            
            # Final Status
            workflow_result["status"] = "COMPLETED"
            workflow_result["s3_path"] = upload_result.get("s3_path")
            workflow_result["statistics"] = {
                "files_uploaded": upload_result.get("file_count", 0),
                "commits": repo_info.get("commit_count", 0),
                "snippets_extracted": len(snippets) if snippets else 0
            }
            workflow_result["completed_at"] = datetime.now().isoformat()
            
            # Store history
            self.workflow_history[analysis_id] = workflow_result
            
            self.logger.info(f"✅ Workflow completed: {analysis_id}")
            
            return workflow_result
        
        except Exception as e:
            self.logger.error(f"❌ Workflow failed: {e}")
            workflow_result["status"] = "FAILED"
            workflow_result["error"] = str(e)
            workflow_result["completed_at"] = datetime.now().isoformat()
            
            # Attempt cleanup
            self._safe_cleanup(workflow_result.get("stages", {}).get("clone", {}))
            
            return workflow_result
    
    def _stage_clone(
        self,
        repo_url: str,
        branch: str,
        shallow: bool
    ) -> Dict[str, Any]:
        """Clone repository stage"""
        self.logger.info("📥 Stage 1: Cloning repository...")
        
        depth = 1 if shallow else None
        
        result = self.git_handler.clone_repository(
            repo_url=repo_url,
            branch=branch,
            depth=depth
        )
        
        if result["success"]:
            self.logger.info(f"✅ Clone successful: {result['local_path']}")
        else:
            self.logger.error(f"❌ Clone failed: {result['error']}")
        
        return result
    
    def _stage_extract_snippets(self, local_repo_path: str) -> Dict[str, Any]:
        """Extract code snippets stage"""
        self.logger.info("📝 Stage 2: Extracting code snippets...")
        
        try:
            snippets = self.snippet_extractor.extract_from_directory(local_repo_path)
            
            self.logger.info(f"✅ Extracted {len(snippets)} code snippets")
            
            return {
                "success": True,
                "snippet_count": len(snippets),
                "snippets": snippets
            }
        
        except Exception as e:
            self.logger.warning(f"⚠️ Snippet extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "snippets": {}
            }
    
    def _stage_upload_to_s3(
        self,
        local_repo_path: str,
        analysis_id: str,
        repo_url: str,
        branch: str,
        repo_info: Dict[str, Any],
        snippets: Dict[str, Any],
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Upload to S3 stage"""
        self.logger.info("☁️ Stage 3: Uploading to S3...")
        
        try:
            # Extract project name from repo_url or use default
            project_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            
            # Upload directory using new structured format
            s3_path = self.s3_uploader.upload_project_structure(local_repo_path, project_name, analysis_id)
            
            # Create and upload metadata
            metadata_obj = {
                "analysis_id": analysis_id,
                "project_name": project_name,
                "repo_url": repo_url,
                "branch": branch,
                "uploaded_at": datetime.now().isoformat(),
                "repo_info": repo_info,
                "snippet_count": sum(len(s) for s in snippets.values()) if isinstance(snippets, dict) else 0,
                "custom_metadata": metadata or {}
            }
            
            # Upload metadata.json to project root
            self.s3_uploader.upload_json(
                metadata_obj,
                f"{project_name}/metadata.json"
            )
            
            # Upload categorized snippets if available
            if snippets:
                self.s3_uploader.upload_categorized_snippets(
                    snippets,
                    project_name,
                    analysis_id
                )
            
            file_count = self.s3_uploader.count_files_in_directory(local_repo_path)
            
            self.logger.info(f"✅ Upload successful to S3: {s3_path}")
            
            return {
                "success": True,
                "s3_path": s3_path,
                "file_count": file_count,
                "metadata_uploaded": True
            }
        
        except Exception as e:
            self.logger.error(f"❌ S3 upload failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _stage_cleanup(self, repo_name: Optional[str]) -> Dict[str, Any]:
        """Cleanup stage"""
        self.logger.info("🧹 Stage 4: Cleaning up local files...")
        
        if not repo_name:
            return {"success": True, "message": "No cleanup needed"}
        
        try:
            success = self.git_handler.cleanup_repository(repo_name, force=True)
            
            if success:
                self.logger.info(f"✅ Cleanup successful for {repo_name}")
            else:
                self.logger.warning(f"⚠️ Cleanup incomplete for {repo_name}")
            
            return {
                "success": success,
                "repo_name": repo_name
            }
        
        except Exception as e:
            self.logger.warning(f"⚠️ Cleanup error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _safe_cleanup(self, clone_result: Dict[str, Any]):
        """Safely cleanup on error"""
        try:
            repo_name = clone_result.get("repo_name")
            if repo_name:
                self.git_handler.cleanup_repository(repo_name, force=True)
        except Exception as e:
            self.logger.warning(f"Could not cleanup on error: {e}")
    
    def get_workflow_history(self, analysis_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get workflow execution history.
        
        Args:
            analysis_id: Specific analysis ID (or None for all)
        
        Returns:
            Workflow history
        """
        if analysis_id:
            return self.workflow_history.get(analysis_id)
        return self.workflow_history.copy()
    
    def get_workflow_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get current workflow status for analysis.
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Status information
        """
        if analysis_id in self.workflow_history:
            history = self.workflow_history[analysis_id]
            return {
                "analysis_id": analysis_id,
                "status": history.get("status"),
                "started_at": history.get("started_at"),
                "completed_at": history.get("completed_at"),
                "stages": list(history.get("stages", {}).keys()),
                "error": history.get("error")
            }
        
        return {
            "analysis_id": analysis_id,
            "status": "NOT_FOUND"
        }


# Global workflow instance
git_s3_workflow = GitS3Workflow()
