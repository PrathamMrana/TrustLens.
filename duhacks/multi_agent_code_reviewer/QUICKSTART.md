# 🎯 Quick Start Guide

## Multi-Agent AI Code Review System - REST API Backend

### ⚡ 3-Step Quick Start

#### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2️⃣ Start the Server
```bash
python run_api.py
```

You should see:
```
============================================================
Multi-Agent AI Code Review System - REST API
============================================================
Starting server on 0.0.0.0:5000
Debug mode: True
============================================================
API Documentation: See API_DOCUMENTATION.md
Health Check: http://localhost:5000/health
API Base: http://localhost:5000/api
============================================================
```

#### 3️⃣ Test the API
```bash
# In a new terminal
python test_api.py
```

---

## 🧪 Manual Testing with cURL

### Test 1: Health Check
```bash
curl http://localhost:5000/health
```

### Test 2: Clone GitHub Repo
```bash
curl -X POST http://localhost:5000/api/repos/from-github \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/example/repo",
    "branch": "main"
  }'
```

You'll get an `analysis_id` like `analysis-abc123`.

### Test 3: Start Analysis
```bash
curl -X POST http://localhost:5000/api/analysis/start \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_id": "analysis-abc123"
  }'
```

### Test 4: Check Status
```bash
curl http://localhost:5000/api/analysis/status/analysis-abc123
```

### Test 5: Get Report
```bash
curl http://localhost:5000/api/analysis/report/analysis-abc123
```

### Test 6: Get Agent Details
```bash
curl http://localhost:5000/api/analysis/agents/analysis-abc123
```

### Test 7: Get Reliability
```bash
curl http://localhost:5000/api/analysis/reliability/analysis-abc123
```

---

## 📱 API Response Examples

### GET /health
```json
{
  "status": "healthy",
  "service": "Multi-Agent Code Review System",
  "version": "1.0.0"
}
```

### POST /api/repos/from-github
```json
{
  "analysis_id": "analysis-abc123",
  "s3_path": "s3://code-review-bucket/analysis-abc123/",
  "status": "UPLOADED",
  "repo_url": "https://github.com/example/repo"
}
```

### GET /api/analysis/report/{id}
```json
{
  "final_decision": "Manual Review Required",
  "overall_confidence": 0.58,
  "overall_risk_level": "high",
  "disagreement_detected": true,
  "security_findings": [
    {
      "type": "sql_injection",
      "severity": "critical",
      "description": "Potential SQL injection..."
    }
  ],
  "logic_findings": [...],
  "quality_summary": {...},
  "system_reasoning": "Conflicting agent outputs with low confidence",
  "deferred": true
}
```

---

## 🎓 For Viva / Demo

### Question: Walk me through the architecture

**Answer:**
```
Frontend → REST API → Controller → Orchestrator → Agents
                                        ↓
                                    S3 + Gemini
```

1. **Frontend** uploads code via `/api/repos/upload`
2. **Controller** stores in S3, creates `analysis_id`
3. **Frontend** starts analysis via `/api/analysis/start`
4. **Orchestrator** coordinates 5 specialized agents
5. **Agents** analyze code from S3 (security, logic, quality)
6. **Orchestrator** aggregates results, detects conflicts
7. **Frontend** polls `/api/analysis/status/{id}` until complete
8. **Frontend** fetches report via `/api/analysis/report/{id}`

### Question: Why separate APIs for status and report?

**Answer:**
- **Status**: Lightweight, for polling (every 2-3 seconds)
- **Report**: Heavy, complete analysis (fetched once when done)
- Reduces server load and improves UX

### Question: What happens if an agent fails?

**Answer:**
Each agent returns `AgentOutput` with `success` flag. If agent fails:
1. Error stored in `error_message`
2. Orchestrator continues with other agents
3. Overall confidence reduced
4. System may defer if critical agent fails

### Question: How do you handle low confidence?

**Answer:**
System defers decision when:
- Overall confidence < 0.7 (configurable)
- Agents disagree (conflicts detected)
- Critical agent fails

Deferral means: "Human review required, not confident enough to automate"

---

## 🔧 Customization

### Change Confidence Threshold
Edit `api/controllers.py`:
```python
self.default_config = {
    "min_confidence": 0.8  # Change from 0.7 to 0.8
}
```

### Change Port
```bash
PORT=8080 python run_api.py
```

### Enable Production Mode
```bash
DEBUG=False python run_api.py
```

---

## 📚 Complete Documentation

- **API Reference**: See `API_DOCUMENTATION.md`
- **Project Overview**: See `README.md`
- **Architecture**: See main `README.md`

---

## 🚨 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Use different port
PORT=8080 python run_api.py
```

### ImportError
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Can't connect to API
- Make sure server is running
- Check firewall settings
- Try `http://127.0.0.1:5000` instead of `localhost:5000`

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Replace mocked S3 client with real boto3
- [ ] Add real Gemini API key
- [ ] Implement database (replace in-memory storage)
- [ ] Add authentication (JWT/OAuth)
- [ ] Enable rate limiting
- [ ] Add input validation
- [ ] Implement background tasks (Celery)
- [ ] Add logging to file
- [ ] Enable HTTPS
- [ ] Add monitoring

---

## 🎯 Next Steps

1. **Test all endpoints** with `test_api.py`
2. **Build frontend** that consumes these APIs
3. **Replace mocks** with real implementations
4. **Add database** for persistence
5. **Deploy** to cloud (AWS/Azure/GCP)

---

**Status**: ✅ Production-Ready API Skeleton  
**Version**: 1.0.0  
**Framework**: Flask REST API  
**Ready for**: Final Year Project Demo 🚀
