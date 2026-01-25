"""
Enhanced API Controllers
Complete business logic for production-ready API endpoints
"""

import uuid
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional
from orchestrator.orchestrator import Orchestrator
from storage.s3_uploader import S3Uploader
from storage.git_s3_workflow import git_s3_workflow
from utils.logger import Logger


class CodeReviewController:
    """
    Enhanced controller for code review API endpoints.
    Implements complete workflow: upload → analyze → report.
    """
    
    def __init__(self):
        """Initialize controller"""
        self.logger = Logger("CodeReviewController")
        
        # Storage (replace with database in production)
        self.analyses = {}  # Stores analysis metadata
        self.reports = {}   # Stores analysis reports
        
        # S3 uploader
        self.s3_uploader = S3Uploader()
        
        # Default configuration
        self.default_config = {
            "min_confidence": 0.7,
            "security_config": {"max_snippet_length": 500},
            "logic_config": {"max_snippet_length": 600},
            "quality_config": {
                "thresholds": {
                    "max_function_length": 50,
                    "max_file_length": 500,
                    "min_comment_ratio": 0.1,
                    "max_complexity": 10
                }
            },
            "decision_config": {"min_confidence": 0.7}
        }
    
    # ==================== REPOSITORY INGESTION ====================
    
    def upload_repository(self, file, project_name: str) -> Dict[str, Any]:
        """
        Upload code zip file and store in S3.
        
        Args:
            file: Flask file object
            project_name: Name of project
        
        Returns:
            Upload result with analysis_id
        """
        # Generate analysis ID
        analysis_id = f"analysis-{str(uuid.uuid4())[:8]}"
        
        try:
            # Save file temporarily
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, file.filename)
            file.save(zip_path)
            
            # Extract zip
            extract_dir = os.path.join(temp_dir, 'extracted')
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Upload to S3
            s3_path = self.s3_uploader.upload_directory(extract_dir, analysis_id)
            
            # Store metadata
            self.analyses[analysis_id] = {
                "analysis_id": analysis_id,
                "project_name": project_name,
                "s3_path": s3_path,
                "repository_url": f"uploaded:{file.filename}",
                "status": "UPLOADED",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
                "source": "upload"
            }
            
            self.logger.info(f"Uploaded repository: {analysis_id}")
            
            return {
                "analysis_id": analysis_id,
                "s3_path": s3_path,
                "status": "UPLOADED",
                "message": "Code uploaded successfully"
            }
        
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            raise
    
    def clone_from_github(self, repo_url: str, branch: str = "main", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Clone GitHub repository, upload to S3, and store metadata.
        Uses complete Git-S3 workflow.
        
        Args:
            repo_url: GitHub repository URL
            branch: Branch name (default: main)
            metadata: Optional custom metadata to store
        
        Returns:
            Clone result with analysis_id, S3 path, and workflow info
        """
        analysis_id = f"analysis-{str(uuid.uuid4())[:8]}"
        
        try:
            self.logger.info(f"🔄 Starting Git clone workflow: {repo_url}")
            
            # Use Git-S3 workflow for complete processing
            workflow_result = git_s3_workflow.process_git_repository(
                repo_url=repo_url,
                analysis_id=analysis_id,
                branch=branch,
                shallow=False,
                extract_snippets=True,
                metadata=metadata or {}
            )
            
            # Check if workflow succeeded
            if workflow_result["status"] != "COMPLETED":
                raise Exception(f"Workflow failed: {workflow_result.get('error', 'Unknown error')}")
            
            s3_path = workflow_result["s3_path"]
            
            # Extract repo name
            repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
            
            # Store analysis metadata for tracking
            self.analyses[analysis_id] = {
                "analysis_id": analysis_id,
                "project_name": repo_name,
                "s3_path": s3_path,
                "repository_url": repo_url,
                "branch": branch,
                "status": "UPLOADED",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
                "source": "github",
                "workflow_info": {
                    "completed_at": workflow_result.get("completed_at"),
                    "statistics": workflow_result.get("statistics", {})
                }
            }
            
            self.logger.info(f"✅ Successfully cloned and uploaded: {analysis_id}")
            
            return {
                "analysis_id": analysis_id,
                "s3_path": s3_path,
                "status": "UPLOADED",
                "repo_url": repo_url,
                "branch": branch,
                "message": f"Repository cloned and uploaded successfully",
                "statistics": workflow_result.get("statistics", {}),
                "workflow_status": workflow_result["status"],
                "repo_info": workflow_result.get("repo_info", {})  # Include repository metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ Clone workflow failed: {e}")
            raise
    
    def analyze_snippet(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Ingest a direct code snippet, upload to S3, and return analysis_id.
        
        Args:
            code: Raw code text
            language: Code language for file extension
            
        Returns:
            Ingestion result with analysis_id
        """
        analysis_id = f"analysis-{str(uuid.uuid4())[:8]}"
        
        try:
            # Extension map
            exts = {
                "python": ".py", "javascript": ".js", "java": ".java", 
                "typescript": ".ts", "cpp": ".cpp", "c": ".c"
            }
            ext = exts.get(language.lower(), ".txt")
            filename = f"snippet{ext}"
            
            # Save snippet temporarily
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Upload to S3
            s3_path = self.s3_uploader.upload_directory(temp_dir, analysis_id)
            
            # Store metadata
            self.analyses[analysis_id] = {
                "analysis_id": analysis_id,
                "project_name": f"snippet-{language}",
                "s3_path": s3_path,
                "repository_url": "pasted-snippet",
                "status": "UPLOADED",
                "progress": 0,
                "created_at": datetime.now().isoformat(),
                "source": "snippet"
            }
            
            self.logger.info(f"Ingested code snippet: {analysis_id}")
            
            return {
                "analysis_id": analysis_id,
                "s3_path": s3_path,
                "status": "UPLOADED",
                "message": "Snippet uploaded successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Snippet ingestion failed: {e}")
            raise
    
    def start_analysis(self, analysis_id: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start multi-agent analysis.
        
        Args:
            analysis_id: Analysis identifier
            config: Optional configuration override
        
        Returns:
            Analysis start confirmation
        """
        # Check if analysis exists
        if analysis_id not in self.analyses:
            raise ValueError(f"Analysis not found: {analysis_id}")
        
        analysis = self.analyses[analysis_id]
        
        # Merge config
        full_config = {**self.default_config}
        if config:
            full_config.update(config)
        
        # Update status
        analysis["status"] = "IN_PROGRESS"
        analysis["progress"] = 10
        analysis["started_at"] = datetime.now().isoformat()
        analysis["config"] = full_config
        
        self.logger.info(f"Starting analysis: {analysis_id}")
        
        # Run analysis (in production: use background task)
        try:
            orchestrator = Orchestrator(full_config)
            report = orchestrator.analyze_repository(
                analysis["repository_url"],
                analysis["s3_path"]
            )
            
            # Store report
            self.reports[analysis_id] = report.to_dict()
            
            # Update status
            analysis["status"] = "COMPLETED"
            analysis["progress"] = 100
            analysis["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            analysis["status"] = "FAILED"
            analysis["error"] = str(e)
            analysis["failed_at"] = datetime.now().isoformat()
        
        return {
            "analysis_id": analysis_id,
            "status": analysis["status"],
            "message": "Analysis started" if analysis["status"] == "IN_PROGRESS" else "Analysis completed"
        }
    
    # ==================== STATUS & REPORTING ====================
    
    def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get analysis status for polling.
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Status information
        """
        analysis = self.analyses.get(analysis_id)
        
        if not analysis:
            return None
        
        return {
            "analysis_id": analysis_id,
            "status": analysis["status"],
            "progress": analysis.get("progress", 0),
            "started_at": analysis.get("started_at"),
            "completed_at": analysis.get("completed_at"),
            "error": analysis.get("error")
        }
    
    def get_detailed_report(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed, explainable analysis report.
        **MOST IMPORTANT METHOD**
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Detailed report with findings and reasoning
        """
        if analysis_id not in self.reports:
            return None
        
        raw_report = self.reports[analysis_id]
        
        # Transform to frontend-friendly format
        detailed_report = {
            "analysis_id": analysis_id,
            "final_decision": raw_report.get("recommendation", "Unknown"),
            "overall_confidence": raw_report.get("overall_confidence", 0.0),
            "overall_risk_level": raw_report.get("overall_risk_level", "none"),
            "disagreement_detected": len(raw_report.get("conflicts", [])) > 0,
            
            # Extract findings by agent type
            "security_findings": self._extract_findings_by_type(raw_report, "security_analysis"),
            "logic_findings": self._extract_findings_by_type(raw_report, "logic_analysis"),
            "feature_findings": self._extract_findings_by_type(raw_report, "feature_extraction"),
            "quality_summary": self._extract_quality_summary(raw_report),
            
            # System reasoning
            "system_reasoning": self._generate_reasoning(raw_report),
            "deferred": raw_report.get("deferred", False),
            "deferral_reason": raw_report.get("deferral_reason"),
            
            # Metadata
            "timestamp": raw_report.get("timestamp"),
            "repository_url": raw_report.get("repository_url"),
            "conflicts": raw_report.get("conflicts", [])
        }
        
        return detailed_report
    
    def get_agent_details(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get individual agent outputs for debugging.
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Agent-level details
        """
        if analysis_id not in self.reports:
            return None
        
        raw_report = self.reports[analysis_id]
        agent_outputs = raw_report.get("agent_outputs", [])
        
        agents_summary = []
        for output in agent_outputs:
            agents_summary.append({
                "agent": output.get("agent_type"),
                "confidence": output.get("confidence", 0.0),
                "risk_level": output.get("risk_level", "none"),
                "failed": not output.get("success", True),
                "findings_count": len(output.get("findings", [])),
                "error": output.get("error_message")
            })
        
        return {"agents": agents_summary}
    
    def get_reliability_metrics(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get confidence and reliability metrics.
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Reliability information
        """
        if analysis_id not in self.reports:
            return None
        
        raw_report = self.reports[analysis_id]
        overall_confidence = raw_report.get("overall_confidence", 0.0)
        conflicts = raw_report.get("conflicts", [])
        
        # Determine confidence level
        if overall_confidence >= 0.8:
            confidence_level = "HIGH"
        elif overall_confidence >= 0.6:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        return {
            "overall_confidence": overall_confidence,
            "confidence_level": confidence_level,
            "disagreement": len(conflicts) > 0,
            "safe_to_automate": overall_confidence >= 0.8 and len(conflicts) == 0,
            "conflict_count": len(conflicts),
            "system_health": raw_report.get("metadata", {}).get("system_health", {}).get("health_status", "unknown")
        }
    
    # ==================== SYSTEM HEALTH ====================
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Check system health and service availability.
        
        Returns:
            Health status
        """
        return {
            "status": "OK",
            "services": {
                "s3": "connected",  # Check S3 connection in production
                "gemini": "available",  # Check Gemini API in production
                "orchestrator": "ready"
            },
            "timestamp": datetime.now().isoformat(),
            "analyses_count": len(self.analyses)
        }
    
    # ==================== UTILITY METHODS ====================
    
    def list_analyses(
        self,
        limit: int = 10,
        offset: int = 0,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all analyses with pagination.
        
        Args:
            limit: Results per page
            offset: Pagination offset
            status_filter: Optional status filter
        
        Returns:
            Paginated analyses list
        """
        # Filter by status if provided
        all_analyses = list(self.analyses.values())
        
        if status_filter:
            all_analyses = [a for a in all_analyses if a["status"] == status_filter]
        
        # Sort by creation time (newest first)
        all_analyses.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Paginate
        paginated = all_analyses[offset:offset + limit]
        
        return {
            "analyses": paginated,
            "total": len(all_analyses),
            "limit": limit,
            "offset": offset
        }
    
    def delete_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Delete analysis and cleanup.
        
        Args:
            analysis_id: Analysis identifier
        
        Returns:
            Deletion confirmation
        """
        if analysis_id not in self.analyses:
            return None
        
        # Delete from storage
        del self.analyses[analysis_id]
        if analysis_id in self.reports:
            del self.reports[analysis_id]
        
        self.logger.info(f"Deleted analysis: {analysis_id}")
        
        return {
            "message": "Analysis deleted successfully",
            "analysis_id": analysis_id
        }
    
    # ==================== HELPER METHODS ====================
    
    def _extract_findings_by_type(self, report: Dict, agent_type: str) -> list:
        """Extract findings from specific agent type"""
        for output in report.get("agent_outputs", []):
            if output.get("agent_type") == agent_type:
                return output.get("findings", [])
        return []
    
    def _extract_quality_summary(self, report: Dict) -> Dict:
        """Extract quality metrics summary"""
        for output in report.get("agent_outputs", []):
            if output.get("agent_type") == "code_quality":
                metadata = output.get("metadata", {})
                return {
                    "quality_score": output.get("confidence", 0.0),
                    "issues": [f.get("type") for f in output.get("findings", [])],
                    "findings": output.get("findings", []),
                    "metrics": metadata.get("quality_metrics", {})
                }
        return {}
    
    def _generate_reasoning(self, report: Dict) -> str:
        """Generate system reasoning explanation"""
        if report.get("deferred"):
            return report.get("deferral_reason", "Confidence too low for automated decision")
        
        conflicts = report.get("conflicts", [])
        if conflicts:
            return f"Conflicting agent outputs detected ({len(conflicts)} conflicts)"
        
        confidence = report.get("overall_confidence", 0.0)
        if confidence < 0.6:
            return "Low confidence in analysis results"
        
        return "Analysis completed with acceptable confidence"
