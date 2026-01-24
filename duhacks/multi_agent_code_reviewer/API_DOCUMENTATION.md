# Multi-Agent AI Code Review System - API Documentation

## 🚀 Complete Backend API Reference

### Base URL
```
http://localhost:5000/api
```

---

## 📦 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/repos/upload` | POST | Upload code zip file |
| `/api/repos/from-github` | POST | Clone GitHub repository |
| `/api/analysis/start` | POST | Start multi-agent analysis |
| `/api/analysis/status/<id>` | GET | Check analysis progress |
| `/api/analysis/report/<id>` | GET | Get detailed report |
| `/api/analysis/agents/<id>` | GET | View agent outputs |
| `/api/analysis/reliability/<id>` | GET | Get confidence metrics |
| `/api/health` | GET | System health check |
| `/api/analysis/list` | GET | List all analyses |
| `/api/analysis/<id>` | DELETE | Delete analysis |

---

## 🔹 1. Repository Upload

### POST `/api/repos/upload`

Upload code as zip file to start analysis.

**Request** (multipart/form-data):
```
file: <zip file>
project_name: "my-project" (optional)
```

**Response**:
```json
{
  "analysis_id": "analysis-abc123",
  "s3_path": "s3://code-review-bucket/analysis-abc123/",
  "status": "UPLOADED",
  "message": "Code uploaded successfully"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/api/repos/upload \
  -F "file=@project.zip" \
  -F "project_name=my-project"
```

---

### POST `/api/repos/from-github`

Clone GitHub repository.

**Request**:
```json
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main"
}
```

**Response**:
```json
{
  "analysis_id": "analysis-def456",
  "s3_path": "s3://code-review-bucket/analysis-def456/",
  "status": "UPLOADED",
  "repo_url": "https://github.com/user/repo"
}
```

---

## 🔹 2. Start Analysis

### POST `/api/analysis/start`

Trigger multi-agent code analysis.

**Request**:
```json
{
  "analysis_id": "analysis-abc123",
  "config": {
    "min_confidence": 0.7,
    "enable_security": true,
    "enable_logic": true,
    "enable_quality": true
  }
}
```

**Response**:
```json
{
  "analysis_id": "analysis-abc123",
  "status": "IN_PROGRESS",
  "message": "Analysis started"
}
```

---

## 🔹 3. Check Status (POLLING)

### GET `/api/analysis/status/<analysis_id>`

**Frontend should poll this every 2-3 seconds.**

**Response**:
```json
{
  "analysis_id": "analysis-abc123",
  "status": "COMPLETED",
  "progress": 100,
  "started_at": "2024-01-23T21:30:00",
  "completed_at": "2024-01-23T21:35:00"
}
```

**Status Values**:
- `UPLOADED` - Code uploaded, not analyzed
- `IN_PROGRESS` - Analysis running
- `COMPLETED` - Analysis done
- `FAILED` - Analysis failed

---

## 🔹 4. Get Report (MOST IMPORTANT)

### GET `/api/analysis/report/<analysis_id>`

**This is THE MAIN API for displaying results.**

**Response**:
```json
{
  "analysis_id": "analysis-abc123",
  "final_decision": "Manual Review Required",
  "overall_confidence": 0.58,
  "overall_risk_level": "high",
  "disagreement_detected": true,
  
  "security_findings": [
    {
      "type": "sql_injection",
      "severity": "critical",
      "description": "Potential SQL injection in authentication",
      "line": "query = f\"SELECT * FROM users...\""
    }
  ],
  
  "logic_findings": [
    {
      "issue": "infinite_loop",
      "severity": "high",
      "description": "Unconditional while True loop"
    }
  ],
  
  "quality_summary": {
    "quality_score": 0.62,
    "issues": ["long_functions", "low_documentation"],
    "metrics": {...}
  },
  
  "system_reasoning": "Conflicting agent outputs with low confidence",
  "deferred": true,
  "deferral_reason": "2 unresolved conflicts between agents",
  
  "timestamp": "2024-01-23T21:35:00",
  "repository_url": "uploaded:project.zip",
  "conflicts": [...]
}
```

---

## 🔹 5. Agent Details (DEBUG MODE)

### GET `/api/analysis/agents/<analysis_id>`

View individual agent performance.

**Response**:
```json
{
  "agents": [
    {
      "agent": "feature_extraction",
      "confidence": 1.0,
      "risk_level": "none",
      "failed": false,
      "findings_count": 0
    },
    {
      "agent": "security_analysis",
      "confidence": 0.85,
      "risk_level": "critical",
      "failed": false,
      "findings_count": 2
    },
    {
      "agent": "logic_analysis",
      "confidence": 0.75,
      "risk_level": "high",
      "failed": false,
      "findings_count": 2
    }
  ]
}
```

---

## 🔹 6. Reliability Metrics

### GET `/api/analysis/reliability/<analysis_id>`

Get trust and confidence signals.

**Response**:
```json
{
  "overall_confidence": 0.58,
  "confidence_level": "LOW",
  "disagreement": true,
  "safe_to_automate": false,
  "conflict_count": 2,
  "system_health": "degraded"
}
```

**Confidence Levels**:
- `HIGH` - >= 0.8
- `MEDIUM` - >= 0.6
- `LOW` - < 0.6

---

## 🔹 7. System Health

### GET `/api/health`

**Response**:
```json
{
  "status": "OK",
  "services": {
    "s3": "connected",
    "gemini": "available",
    "orchestrator": "ready"
  },
  "timestamp": "2024-01-23T21:30:00",
  "analyses_count": 15
}
```

---

## 🔹 8. List Analyses

### GET `/api/analysis/list?limit=10&offset=0&status=COMPLETED`

**Response**:
```json
{
  "analyses": [
    {
      "analysis_id": "analysis-abc123",
      "project_name": "my-project",
      "status": "COMPLETED",
      "created_at": "2024-01-23T21:30:00",
      "repository_url": "uploaded:project.zip"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

---

## 🔹 9. Delete Analysis

### DELETE `/api/analysis/<analysis_id>`

**Response**:
```json
{
  "message": "Analysis deleted successfully",
  "analysis_id": "analysis-abc123"
}
```

---

## 📊 Frontend Integration Flow

```
1. User uploads code → POST /api/repos/upload
   ↓
2. Get analysis_id → "analysis-abc123"
   ↓
3. Start analysis → POST /api/analysis/start
   ↓
4. Poll status → GET /api/analysis/status/analysis-abc123
   (Every 2-3 seconds until status = "COMPLETED")
   ↓
5. Fetch report → GET /api/analysis/report/analysis-abc123
   ↓
6. Display findings, confidence, reasoning
   ↓
7. Optional: Show agent details, reliability metrics
```

---

## 🧪 Testing with cURL

### Complete Workflow Example:

```bash
# 1. Upload code
curl -X POST http://localhost:5000/api/repos/upload \
  -F "file=@project.zip" \
  -F "project_name=test-project"

# 2. Start analysis (use analysis_id from step 1)
curl -X POST http://localhost:5000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{"analysis_id": "analysis-abc123"}'

# 3. Check status
curl http://localhost:5000/api/analysis/status/analysis-abc123

# 4. Get report
curl http://localhost:5000/api/analysis/report/analysis-abc123

# 5. Get agent details
curl http://localhost:5000/api/analysis/agents/analysis-abc123

# 6. Get reliability
curl http://localhost:5000/api/analysis/reliability/analysis-abc123
```

---

## 🎯 Viva Defense Points

### Q: Why separate upload and analysis?
**A:** Decouples ingestion from processing. Allows validation before expensive AI calls.

### Q: Why polling instead of webhooks?
**A:** Simpler frontend. Real production would use WebSockets or Server-Sent Events.

### Q: What if analysis takes too long?
**A:** Background task queue (Celery) + job status tracking.

### Q: How do you handle failures?
**A:** Each agent can fail independently. Orchestrator tracks failures, system defers on critical failures.

### Q: Why expose agent-level details?
**A:** Explainability. Users see which agent found what, with what confidence.

---

## 🔒 Security Considerations

1. **Authentication** - Add JWT/OAuth in production
2. **Rate Limiting** - Prevent abuse of analysis endpoints
3. **Input Validation** - Validate zip files, repo URLs
4. **S3 Permissions** - Use IAM roles, not hardcoded keys
5. **API Keys** - Never expose Gemini keys in responses

---

## 📈 Production Enhancements

- [ ] Add database (PostgreSQL/MongoDB)
- [ ] Implement background task queue (Celery + Redis)
- [ ] Add WebSocket for real-time updates
- [ ] Implement caching (Redis)
- [ ] Add API authentication
- [ ] Rate limiting
- [ ] Comprehensive error handling
- [ ] API versioning (/api/v1/...)
- [ ] Swagger/OpenAPI documentation

---

**Project**: Multi-Agent AI Code Review System  
**API Version**: 1.0.0  
**Backend**: Flask REST API  
**Status**: Production-Ready Skeleton 🚀
