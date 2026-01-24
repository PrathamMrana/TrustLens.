"""
Enhanced API Routes
Complete REST endpoints for production-ready code review system
"""

from flask import Blueprint, request, jsonify
from api.controllers import CodeReviewController
from utils.logger import Logger

# Create blueprint
api_blueprint = Blueprint('api', __name__)
logger = Logger("APIRoutes")

# Initialize controller
controller = CodeReviewController()


# ==================== 1️⃣ REPOSITORY / CODE INGESTION APIs ====================

@api_blueprint.route('/repos/upload', methods=['POST'])
def upload_code():
    """
    POST /api/repos/upload
    
    Upload code (zip or files) and store in S3.
    Frontend uses this first.
    
    Request (multipart/form-data):
    - file: zip file
    - project_name: optional project name
    
    Response:
    {
        "analysis_id": "analysis-123",
        "s3_path": "s3://bucket/analysis-123/",
        "status": "UPLOADED",
        "message": "Code uploaded successfully"
    }
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided",
                "message": "Please upload a zip file"
            }), 400
        
        file = request.files['file']
        project_name = request.form.get('project_name', 'untitled-project')
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected",
                "message": "Please select a file to upload"
            }), 400
        
        # Process upload
        result = controller.upload_repository(file, project_name)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error in upload endpoint: {e}")
        return jsonify({
            "error": "Upload failed",
            "message": str(e)
        }), 500


@api_blueprint.route('/repos/from-github', methods=['POST'])
def clone_github():
    """
    POST /api/repos/from-github
    
    Clone GitHub repo and store in S3.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "branch": "main"
    }
    
    Response:
    {
        "analysis_id": "analysis-456",
        "s3_path": "s3://bucket/analysis-456/",
        "status": "UPLOADED",
        "repo_url": "https://github.com/user/repo"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('repo_url'):
            return jsonify({
                "error": "Missing repo_url",
                "message": "repo_url is required"
            }), 400
        
        repo_url = data['repo_url']
        branch = data.get('branch', 'main')
        
        # Clone repository
        result = controller.clone_from_github(repo_url, branch)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error in GitHub clone endpoint: {e}")
        return jsonify({
            "error": "Clone failed",
            "message": str(e)
        }), 500


@api_blueprint.route('/repos/snippet', methods=['POST'])
def analyze_snippet():
    """
    POST /api/repos/snippet
    
    Handle direct code snippet submission.
    
    Request Body:
    {
        "code": "...",
        "language": "python"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('code'):
            return jsonify({
                "error": "Missing code",
                "message": "Code snippet is required"
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        
        # Ingest snippet
        result = controller.analyze_snippet(code, language)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error in snippet endpoint: {e}")
        return jsonify({
            "error": "Snippet submission failed",
            "message": str(e)
        }), 500


# ==================== 2️⃣ ANALYSIS TRIGGER APIs ====================

@api_blueprint.route('/analysis/start', methods=['POST'])
def start_analysis():
    """
    POST /api/analysis/start
    
    Start multi-agent analysis.
    
    Request Body:
    {
        "analysis_id": "analysis-123",
        "config": {
            "min_confidence": 0.7,
            "enable_security": true,
            "enable_logic": true,
            "enable_quality": true
        }
    }
    
    Response:
    {
        "analysis_id": "analysis-123",
        "status": "IN_PROGRESS",
        "message": "Analysis started"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('analysis_id'):
            return jsonify({
                "error": "Missing analysis_id",
                "message": "analysis_id is required"
            }), 400
        
        analysis_id = data['analysis_id']
        config = data.get('config', {})
        
        # Start analysis
        result = controller.start_analysis(analysis_id, config)
        
        return jsonify(result), 202
    
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        return jsonify({
            "error": "Failed to start analysis",
            "message": str(e)
        }), 500


# ==================== 3️⃣ ANALYSIS STATUS APIs ====================

@api_blueprint.route('/analysis/status/<analysis_id>', methods=['GET'])
def get_analysis_status(analysis_id):
    """
    GET /api/analysis/status/<analysis_id>
    
    Frontend polls this API to check progress.
    
    Response:
    {
        "analysis_id": "analysis-123",
        "status": "COMPLETED|IN_PROGRESS|UPLOADED|FAILED",
        "progress": 100,
        "started_at": "2024-01-23T21:30:00",
        "completed_at": "2024-01-23T21:35:00"
    }
    """
    try:
        result = controller.get_analysis_status(analysis_id)
        
        if not result:
            return jsonify({
                "error": "Analysis not found",
                "message": f"No analysis found with ID: {analysis_id}"
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "error": "Failed to get status",
            "message": str(e)
        }), 500


# ==================== 4️⃣ RESULTS & REPORT APIs (MOST IMPORTANT) ====================

@api_blueprint.route('/analysis/report/<analysis_id>', methods=['GET'])
def get_analysis_report(analysis_id):
    """
    GET /api/analysis/report/<analysis_id>
    
    **MOST IMPORTANT API**
    Fetch final explainable result.
    
    Response:
    {
        "final_decision": "Manual Review Required",
        "overall_confidence": 0.58,
        "disagreement_detected": true,
        "overall_risk_level": "high",
        
        "security_findings": [...],
        "logic_findings": [...],
        "quality_summary": {...},
        
        "system_reasoning": "Conflicting agent outputs with low confidence",
        "deferred": true,
        "deferral_reason": "..."
    }
    """
    try:
        result = controller.get_detailed_report(analysis_id)
        
        if not result:
            return jsonify({
                "error": "Report not found",
                "message": f"No report found for analysis ID: {analysis_id}"
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting report: {e}")
        return jsonify({
            "error": "Failed to get report",
            "message": str(e)
        }), 500


# ==================== 5️⃣ AGENT-LEVEL DEBUG APIs ====================

@api_blueprint.route('/analysis/agents/<analysis_id>', methods=['GET'])
def get_agent_outputs(analysis_id):
    """
    GET /api/analysis/agents/<analysis_id>
    
    Show individual agent outputs (great for demo & viva).
    
    Response:
    {
        "agents": [
            {
                "agent": "FeatureExtractionAgent",
                "confidence": 0.95,
                "risk_level": "none",
                "failed": false,
                "findings_count": 0
            },
            {
                "agent": "SecurityAnalysisAgent",
                "confidence": 0.82,
                "risk_level": "critical",
                "failed": false,
                "findings_count": 2
            }
        ]
    }
    """
    try:
        result = controller.get_agent_details(analysis_id)
        
        if not result:
            return jsonify({
                "error": "Agent data not found",
                "message": f"No agent data found for analysis ID: {analysis_id}"
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting agent details: {e}")
        return jsonify({
            "error": "Failed to get agent details",
            "message": str(e)
        }), 500


# ==================== 6️⃣ CONFIDENCE & DISAGREEMENT APIs ====================

@api_blueprint.route('/analysis/reliability/<analysis_id>', methods=['GET'])
def get_reliability_info(analysis_id):
    """
    GET /api/analysis/reliability/<analysis_id>
    
    Expose trust signals to frontend.
    Makes system trustworthy, not flashy.
    
    Response:
    {
        "overall_confidence": 0.58,
        "confidence_level": "LOW|MEDIUM|HIGH",
        "disagreement": true,
        "safe_to_automate": false,
        "conflict_count": 2,
        "system_health": "degraded"
    }
    """
    try:
        result = controller.get_reliability_metrics(analysis_id)
        
        if not result:
            return jsonify({
                "error": "Reliability data not found",
                "message": f"No reliability data found for analysis ID: {analysis_id}"
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error getting reliability: {e}")
        return jsonify({
            "error": "Failed to get reliability",
            "message": str(e)
        }), 500


# ==================== 7️⃣ SYSTEM HEALTH API ====================

@api_blueprint.route('/health', methods=['GET'])
def system_health():
    """
    GET /api/health
    
    Check system health and service availability.
    
    Response:
    {
        "status": "OK",
        "services": {
            "s3": "connected",
            "gemini": "available",
            "orchestrator": "ready"
        },
        "timestamp": "2024-01-23T21:30:00"
    }
    """
    try:
        result = controller.check_system_health()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500


# ==================== ADDITIONAL UTILITY APIs ====================

@api_blueprint.route('/analysis/list', methods=['GET'])
def list_analyses():
    """
    GET /api/analysis/list
    
    List all analyses with pagination.
    
    Query params:
    - limit: Number of results (default: 10)
    - offset: Pagination offset (default: 0)
    - status: Filter by status (optional)
    
    Response:
    {
        "analyses": [...],
        "total": 50,
        "limit": 10,
        "offset": 0
    }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        status_filter = request.args.get('status')
        
        result = controller.list_analyses(limit, offset, status_filter)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        return jsonify({
            "error": "Failed to list analyses",
            "message": str(e)
        }), 500


@api_blueprint.route('/analysis/<analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    """
    DELETE /api/analysis/<analysis_id>
    
    Delete analysis and cleanup resources.
    
    Response:
    {
        "message": "Analysis deleted successfully",
        "analysis_id": "analysis-123"
    }
    """
    try:
        result = controller.delete_analysis(analysis_id)
        
        if not result:
            return jsonify({
                "error": "Analysis not found",
                "message": f"No analysis found with ID: {analysis_id}"
            }), 404
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        return jsonify({
            "error": "Failed to delete analysis",
            "message": str(e)
        }), 500


@api_blueprint.route('/repos/submit-git', methods=['POST'])
def submit_git_repository():
    """
    POST /api/repos/submit-git
    
    Submit a Git repository for cloning and S3 upload.
    Complete workflow endpoint that handles the entire process.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "shallow_clone": false,
        "metadata": {
            "project_description": "...",
            "custom_field": "value"
        }
    }
    
    Response:
    {
        "analysis_id": "analysis-xyz",
        "status": "COMPLETED",
        "s3_path": "s3://bucket/analysis-xyz/",
        "repo_url": "https://github.com/user/repo",
        "branch": "main",
        "statistics": {
            "files_uploaded": 150,
            "commits": 245,
            "snippets_extracted": 45
        },
        "workflow_status": "COMPLETED"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('repo_url'):
            return jsonify({
                "error": "Missing required fields",
                "message": "repo_url is required"
            }), 400
        
        repo_url = data['repo_url']
        branch = data.get('branch', 'main')
        metadata = data.get('metadata', {})
        
        # Clone using complete Git-S3 workflow
        result = controller.clone_from_github(
            repo_url=repo_url,
            branch=branch,
            metadata=metadata
        )
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error in Git submit endpoint: {e}")
        return jsonify({
            "error": "Repository submission failed",
            "message": str(e)
        }), 500


@api_blueprint.route('/repos/<analysis_id>/workflow-status', methods=['GET'])
def get_workflow_status(analysis_id):
    """
    GET /api/repos/{analysis_id}/workflow-status
    
    Get the Git-S3 workflow execution status.
    
    Response:
    {
        "analysis_id": "analysis-xyz",
        "status": "COMPLETED",
        "started_at": "2024-01-24T10:30:00",
        "completed_at": "2024-01-24T10:35:00",
        "stages": ["clone", "extraction", "upload", "cleanup"],
        "error": null
    }
    """
    try:
        from storage.git_s3_workflow import git_s3_workflow
        
        status = git_s3_workflow.get_workflow_status(analysis_id)
        
        if status["status"] == "NOT_FOUND":
            return jsonify({
                "error": "Workflow not found",
                "message": f"No workflow found for analysis_id: {analysis_id}"
            }), 404
        
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Error fetching workflow status: {e}")
        return jsonify({
            "error": "Failed to fetch workflow status",
            "message": str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@api_blueprint.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found"
    }), 404


@api_blueprint.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": "The HTTP method is not allowed for this endpoint"
    }), 405


@api_blueprint.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500
