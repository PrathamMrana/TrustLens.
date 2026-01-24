# Git Repository Processing Workflow

Complete end-to-end workflow for cloning Git repositories and uploading them to AWS S3 for code analysis.

## Overview

The Git-S3 workflow provides a seamless integration between Git repositories (GitHub, GitLab, Bitbucket, etc.) and AWS S3 storage. It handles:

1. **Git Repository Cloning** - HTTPS and SSH URLs
2. **Code Snippet Extraction** - Automatic extraction of code for analysis
3. **S3 Upload** - Complete repository upload with metadata
4. **Local Cleanup** - Automatic cleanup of temporary files

## Architecture

```
User Request
    ↓
API Endpoint (/api/repos/submit-git)
    ↓
Git Handler (Clone Repository)
    ↓
Snippet Extractor (Extract Code)
    ↓
S3 Uploader (Upload to S3)
    ↓
Cleanup Handler (Remove Temp Files)
    ↓
Response with Analysis ID & S3 Path
```

## Components

### 1. **GitHandler** (`storage/git_handler.py`)

Manages all Git operations using GitPython.

**Features:**
- URL validation (supports HTTP, SSH, Git protocols)
- Repository cloning with progress tracking
- Shallow cloning for large repositories (optional)
- Repository info extraction (commits, files, authors)
- Automatic cleanup of cloned repositories

**Key Methods:**
```python
git_handler = GitHandler()

# Clone a repository
result = git_handler.clone_repository(
    repo_url="https://github.com/user/repo.git",
    branch="main",
    depth=None,  # None for full clone, 1 for shallow
    timeout=300
)

# Get repository info
repo_path = git_handler.get_clone_directory("repo-name")

# Cleanup
git_handler.cleanup_repository("repo-name", force=True)
```

### 2. **GitS3Workflow** (`storage/git_s3_workflow.py`)

Orchestrates the complete workflow across all stages.

**Features:**
- Four-stage pipeline: Clone → Extract → Upload → Cleanup
- Comprehensive error handling with rollback
- Workflow history tracking
- Detailed statistics and reporting

**Key Methods:**
```python
workflow = GitS3Workflow()

# Process complete workflow
result = workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="analysis-abc123",
    branch="main",
    shallow=False,
    extract_snippets=True,
    metadata={"custom": "data"}
)

# Get workflow status
status = workflow.get_workflow_status("analysis-abc123")

# Get history
history = workflow.get_workflow_history("analysis-abc123")
```

### 3. **S3Uploader Extensions** (`storage/s3_uploader.py`)

New helper methods added:
- `upload_json(data, s3_key)` - Upload JSON objects
- `count_files_in_directory(directory)` - Count files in a directory

## API Endpoints

### 1. Submit Git Repository

**Endpoint:** `POST /api/repos/submit-git`

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo.git",
  "branch": "main",
  "metadata": {
    "project_description": "My awesome project",
    "team": "backend"
  }
}
```

**Response:**
```json
{
  "analysis_id": "analysis-abc123",
  "status": "UPLOADED",
  "s3_path": "s3://duhacks-s3-aicode/analysis-abc123/",
  "repo_url": "https://github.com/user/repo.git",
  "branch": "main",
  "message": "Repository cloned and uploaded successfully",
  "statistics": {
    "files_uploaded": 150,
    "commits": 245,
    "snippets_extracted": 45
  },
  "workflow_status": "COMPLETED"
}
```

### 2. Get Workflow Status

**Endpoint:** `GET /api/repos/{analysis_id}/workflow-status`

**Response:**
```json
{
  "analysis_id": "analysis-abc123",
  "status": "COMPLETED",
  "started_at": "2024-01-24T10:30:00",
  "completed_at": "2024-01-24T10:35:00",
  "stages": ["clone", "extraction", "upload", "cleanup"],
  "error": null
}
```

## Usage Examples

### Using cURL

```bash
# Submit a GitHub repository
curl -X POST http://localhost:5000/api/repos/submit-git \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo.git",
    "branch": "main",
    "metadata": {
      "project_type": "python",
      "team": "data-science"
    }
  }'

# Check workflow status
curl http://localhost:5000/api/repos/analysis-abc123/workflow-status
```

### Using Python

```python
import requests

# Submit repository
response = requests.post(
    "http://localhost:5000/api/repos/submit-git",
    json={
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "metadata": {"custom": "data"}
    }
)

result = response.json()
analysis_id = result["analysis_id"]
print(f"Uploaded to: {result['s3_path']}")
print(f"Statistics: {result['statistics']}")

# Check status
status_response = requests.get(
    f"http://localhost:5000/api/repos/{analysis_id}/workflow-status"
)
print(f"Workflow status: {status_response.json()['status']}")
```

### Using Direct Python API

```python
from storage.git_s3_workflow import git_s3_workflow

# Process repository
result = git_s3_workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="my-analysis-123",
    branch="develop",
    shallow=False,
    extract_snippets=True,
    metadata={"project": "trustlens"}
)

print(f"Status: {result['status']}")
print(f"S3 Path: {result['s3_path']}")
print(f"Statistics: {result['statistics']}")
```

## Configuration

The workflow uses AWS credentials from `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=ap-south-1
S3_BUCKET_NAME=duhacks-s3-aicode

# GitHub (optional, for authenticated requests)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

## Supported Repository Types

- **GitHub** - HTTPS and SSH
- **GitLab** - HTTPS and SSH
- **Bitbucket** - HTTPS and SSH
- **Self-hosted Git** - Any Git server supporting HTTPS/SSH

## Performance Optimization

### Shallow Cloning

For large repositories, use shallow cloning to speed up processing:

```python
result = workflow.process_git_repository(
    repo_url="https://github.com/large/repo.git",
    analysis_id="analysis-large",
    shallow=True  # Only clone latest commit
)
```

### Disable Snippet Extraction

If you don't need code snippets:

```python
result = workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="analysis-no-snippets",
    extract_snippets=False  # Skip extraction step
)
```

## Error Handling

All errors are handled gracefully with detailed error messages:

```python
result = git_s3_workflow.process_git_repository(...)

if result["status"] == "FAILED":
    print(f"Error: {result['error']}")
    # Automatic cleanup is performed on failure
```

## S3 Storage Structure

```
s3://bucket-name/
├── analysis-abc123/
│   ├── metadata.json           # Analysis metadata
│   ├── snippets.json           # Extracted code snippets
│   ├── src/                    # Original repository files
│   ├── README.md
│   ├── requirements.txt
│   └── ... (all repo files)
```

## Workflow History

Track and inspect all workflow executions:

```python
# Get history for specific analysis
history = git_s3_workflow.get_workflow_history("analysis-abc123")

# Get all histories
all_histories = git_s3_workflow.get_workflow_history()

# Check history structure
print(history["stages"]["clone"]["success"])
print(history["stages"]["upload"]["s3_path"])
print(history["statistics"])
```

## Installation Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- `GitPython==3.1.40` - Git operations
- `boto3==1.34.0` - AWS S3 integration
- `python-dotenv==1.0.0` - Environment variables

## Troubleshooting

### Git Clone Fails

**Issue:** `fatal: could not read Username`

**Solution:** Use HTTPS URLs or configure SSH keys for SSH authentication.

### S3 Upload Fails

**Issue:** `NoCredentialsError: Unable to locate credentials`

**Solution:** Ensure AWS credentials are set in `.env`:
```env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### Large Repository Timeout

**Issue:** Clone operation times out

**Solution:** Use shallow cloning:
```python
result = workflow.process_git_repository(
    repo_url="...",
    shallow=True
)
```

## Security Considerations

1. **Credentials**: Never commit `.env` file with real credentials
2. **SSH Keys**: Configure SSH keys for authentication
3. **Permissions**: Ensure S3 bucket has proper access controls
4. **Cleanup**: Automatic cleanup prevents disk space issues
5. **Metadata**: Sensitive data should not be included in metadata

## Future Enhancements

- [ ] Webhook support for automatic trigger on push
- [ ] Branch comparison and diff analysis
- [ ] Commit history analysis
- [ ] Large repository streaming upload
- [ ] Parallel multi-repository processing
- [ ] Repository caching for repeated analysis

## License

MIT License - See LICENSE file
