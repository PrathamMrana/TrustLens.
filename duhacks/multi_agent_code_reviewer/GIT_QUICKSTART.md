# Git Workflow Quick Start

Complete workflow for cloning Git repositories and pushing to S3 bucket.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Install new packages
pip install GitPython==3.1.40 python-dotenv==1.0.0

# Or install all requirements
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure your `.env` file has AWS credentials:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=duhacks-s3-aicode

# GitHub Token (optional, for private repos)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 3. Start API Server

```bash
python run_api.py
```

## 📝 Usage Examples

### Option 1: Using cURL

```bash
# Submit a repository
curl -X POST http://localhost:5000/api/repos/submit-git \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo.git",
    "branch": "main",
    "metadata": {
      "description": "My project",
      "team": "backend"
    }
  }'

# Response:
# {
#   "analysis_id": "analysis-abc123",
#   "status": "UPLOADED",
#   "s3_path": "s3://duhacks-s3-aicode/analysis-abc123/",
#   "statistics": {
#     "files_uploaded": 150,
#     "commits": 245,
#     "snippets_extracted": 45
#   }
# }

# Check workflow status
curl http://localhost:5000/api/repos/analysis-abc123/workflow-status
```

### Option 2: Using Python

```python
import requests

# Submit repository
response = requests.post(
    "http://localhost:5000/api/repos/submit-git",
    json={
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main"
    }
)

result = response.json()
analysis_id = result["analysis_id"]
print(f"Analysis ID: {analysis_id}")
print(f"S3 Path: {result['s3_path']}")
print(f"Uploaded {result['statistics']['files_uploaded']} files")

# Check status
status = requests.get(
    f"http://localhost:5000/api/repos/{analysis_id}/workflow-status"
).json()
print(f"Status: {status['status']}")
```

### Option 3: Direct Python Usage

```python
from storage.git_s3_workflow import git_s3_workflow

# Process complete workflow
result = git_s3_workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="my-analysis-123",
    branch="main",
    shallow=False,
    extract_snippets=True,
    metadata={"custom": "data"}
)

print(f"Status: {result['status']}")
print(f"S3 Path: {result['s3_path']}")
print(f"Statistics: {result['statistics']}")
```

## 🔄 Workflow Stages

```
1. CLONE
   ✓ Validate Git URL
   ✓ Clone repository
   ✓ Extract repo info

2. EXTRACT
   ✓ Extract code snippets
   ✓ Analyze structure

3. UPLOAD
   ✓ Upload files to S3
   ✓ Upload metadata
   ✓ Upload snippets

4. CLEANUP
   ✓ Remove temporary files
   ✓ Update status
```

## 📊 API Endpoints

### Submit Git Repository
- **POST** `/api/repos/submit-git`
- **Body**: `{ "repo_url": "...", "branch": "main", "metadata": {} }`
- **Returns**: `{ "analysis_id": "...", "s3_path": "...", "statistics": {...} }`

### Check Workflow Status
- **GET** `/api/repos/{analysis_id}/workflow-status`
- **Returns**: `{ "status": "COMPLETED", "stages": [...] }`

### Upload Code (Existing)
- **POST** `/api/repos/upload` - Upload ZIP files
- **POST** `/api/repos/from-github` - Legacy GitHub endpoint (now uses new workflow)

## 🎯 Key Features

✅ **Git Support**
- GitHub, GitLab, Bitbucket
- HTTPS and SSH URLs
- Branch selection
- Shallow cloning for large repos

✅ **S3 Integration**
- Automatic upload to configured bucket
- Metadata storage (metadata.json)
- Code snippets extraction
- Auto-cleanup on error

✅ **Error Handling**
- Invalid URL detection
- Network timeout handling
- AWS credential validation
- Automatic cleanup on failure

✅ **Tracking**
- Workflow history
- Statistics (files, commits, snippets)
- Status polling
- Detailed error messages

## 🔧 Configuration Options

### Shallow Clone (Faster)
```python
# Only clone latest commit - faster for large repos
result = git_s3_workflow.process_git_repository(
    repo_url="...",
    analysis_id="...",
    shallow=True
)
```

### Skip Snippet Extraction
```python
# Skip code snippet extraction if not needed
result = git_s3_workflow.process_git_repository(
    repo_url="...",
    analysis_id="...",
    extract_snippets=False
)
```

### Add Custom Metadata
```python
result = git_s3_workflow.process_git_repository(
    repo_url="...",
    analysis_id="...",
    metadata={
        "project_type": "python",
        "team": "backend",
        "description": "ML pipeline"
    }
)
```

## 📁 S3 Storage Structure

After processing, your S3 bucket will have:

```
s3://bucket-name/
├── analysis-abc123/
│   ├── metadata.json          # Analysis metadata
│   ├── snippets.json          # Code snippets
│   ├── src/                   # Source code
│   ├── README.md
│   ├── requirements.txt
│   └── ... (all repo files)
```

## ✅ Testing

Run the test suite:

```bash
python test_git_workflow.py
```

This will show:
- Git handler functionality
- Workflow structure
- API usage examples
- Python usage patterns
- Error scenarios
- Configuration requirements

## 🐛 Troubleshooting

### "Invalid Git URL"
- Use complete URLs: `https://github.com/user/repo.git`
- For SSH: Ensure keys are configured

### "AWS Credentials Error"
- Check `.env` file has credentials
- Verify IAM permissions on bucket
- Test with: `aws s3 ls s3://bucket-name`

### "Clone Timeout"
- Use shallow cloning: `shallow=True`
- Check internet connection
- Increase timeout parameter

### "S3 Upload Failed"
- Verify bucket name in `.env`
- Check AWS credentials and permissions
- Ensure bucket exists

## 📚 Complete Documentation

See `GIT_WORKFLOW_GUIDE.md` for:
- Detailed architecture overview
- Component documentation
- Advanced usage patterns
- Performance optimization
- Security considerations

## 💡 Common Workflows

### Clone and Analyze
```python
# 1. Clone repo and upload to S3
result = git_s3_workflow.process_git_repository(
    repo_url="https://github.com/user/repo.git",
    analysis_id="my-analysis"
)

# 2. Start analysis on uploaded code
response = requests.post(
    "http://localhost:5000/api/analysis/start",
    json={"analysis_id": "my-analysis"}
)

# 3. Get detailed report
report = requests.get(
    "http://localhost:5000/api/analysis/my-analysis/report"
).json()
```

### Batch Processing
```python
repos = [
    "https://github.com/user/repo1.git",
    "https://github.com/user/repo2.git",
    "https://github.com/user/repo3.git"
]

for i, repo in enumerate(repos):
    result = git_s3_workflow.process_git_repository(
        repo_url=repo,
        analysis_id=f"batch-{i}"
    )
    print(f"Processed {repo}: {result['s3_path']}")
```

## 🚦 Next Steps

1. ✅ Install dependencies
2. ✅ Configure AWS credentials
3. ✅ Test the workflow
4. ✅ Start analyzing repositories!

```bash
# Start API server
python run_api.py

# In another terminal, submit a repository
curl -X POST http://localhost:5000/api/repos/submit-git \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/user/repo.git"}'
```

---

**Made with ❤️ for TrustLens**

Need help? See `GIT_WORKFLOW_GUIDE.md` or check logs in `logs/` directory.
