# Multi-Agent AI System for Risk-Aware Code Review

**Final Year Project - Complete Code Skeleton**

## 📋 Project Overview

A multi-agent AI system that analyzes source code for security, logic, and quality risks using specialized AI agents coordinated by an orchestrator. The system reads code from Amazon S3 snapshots and uses Google Gemini LLM for intelligent analysis.

## 🏗️ Architecture

### Core Principles
- **Agent Separation**: Agents NEVER make final decisions, only recommendations
- **S3-Only Access**: All code read from S3 snapshots, not direct Git access
- **LLM Isolation**: Gemini used ONLY inside agents, never by orchestrator
- **Confidence Tracking**: Every output includes confidence scores
- **Safe Deferral**: System defers when confidence is low or conflicts exist

### System Components

0. **REST API Backend** (Flask)
   - Complete RESTful API for frontend integration
   - Repository upload and GitHub cloning
   - Analysis job management
   - Real-time status polling
   - Detailed reporting endpoints

1. **Agents** (5 specialized agents)
   - `FeatureExtractionAgent`: Deterministic feature extraction (no LLM)
   - `SecurityAnalysisAgent`: Security vulnerability detection (uses Gemini)
   - `LogicAnalysisAgent`: Code logic correctness (uses Gemini)
   - `CodeQualityAgent`: Metric-based quality assessment (no LLM)
   - `DecisionAgent`: Action recommendation only (no execution)

2. **Orchestrator**
   - Coordinates all agents
   - Manages workflow
   - Aggregates results
   - Handles failures gracefully

3. **Support Systems**
   - `ConflictResolver`: Detects agent disagreements
   - `ReliabilityEngine`: Confidence aggregation and deferral logic

## 📁 Project Structure

```
multi_agent_code_reviewer/
│
├── api/                        # 🆕 REST API Backend
│   ├── app.py                  # Flask application
│   ├── routes.py               # API endpoints
│   └── controllers.py          # Business logic
│
├── agents/
│   ├── base_agent.py           # Abstract base class for all agents
│   ├── feature_agent.py        # Feature extraction (deterministic)
│   ├── security_agent.py       # Security analysis (Gemini)
│   ├── logic_agent.py          # Logic analysis (Gemini)
│   ├── code_quality_agent.py   # Quality metrics (deterministic)
│   └── decision_agent.py       # Decision recommendation
│
├── orchestrator/
│   ├── orchestrator.py         # Main orchestrator
│   ├── conflict_resolver.py    # Conflict detection
│   └── reliability.py          # Confidence & reliability tracking
│
├── schemas/
│   ├── agent_output.py         # Agent output schema
│   └── final_report.py         # Final report schema
│
├── storage/
│   ├── s3_reader.py            # S3 code reader utility
│   └── s3_uploader.py          # 🆕 S3 code uploader
│
├── llm/
│   └── gemini_client.py        # Gemini LLM wrapper
│
├── utils/
│   └── logger.py               # Logging utility
│
├── main.py                     # CLI entry point
├── run_api.py                  # 🆕 REST API server
├── requirements.txt            # Dependencies
└── API_DOCUMENTATION.md        # 🆕 Complete API docs
```

## 🚀 Setup & Usage

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Option 1: REST API Backend (Recommended)

**Start the Flask server:**
```bash
python run_api.py
```

Server will start on `http://localhost:5000`

**API Endpoints:**
- Health: `GET /health`
- Upload code: `POST /api/repos/upload`
- Start analysis: `POST /api/analysis/start`
- Check status: `GET /api/analysis/status/<id>`
- Get report: `GET /api/analysis/report/<id>`

**See `API_DOCUMENTATION.md` for complete API reference.**

### Option 2: Command Line Interface

**Configuration:**
Edit `main.py` to configure:
- Confidence thresholds
- Agent-specific parameters
- S3 paths
- Repository URLs

**Running CLI:**

```bash
python main.py
```

### Output

The system generates:
1. Console output with analysis summary
2. `code_review_report.json` with complete results

## 🔑 Key Features

### 1. Confidence-Based Deferral
- System defers decisions when confidence < threshold
- No forced recommendations on uncertain analysis

### 2. Conflict Detection
- Detects disagreements between agents
- Flags conflicts for manual review
- Never forces resolution

### 3. Explainable Output
- All findings include reasoning
- Confidence scores for transparency
- Clear recommendation path

### 4. Modular Design
- Easy to add new agents
- Configurable thresholds
- Exam-defensible architecture

## 📊 Sample Output

```
================================================================================
CODE REVIEW REPORT
================================================================================

Repository: https://github.com/example/repo
S3 Path: s3://code-review-bucket/repo-snapshot-2024/
Timestamp: 2024-01-23 21:30:00

Overall Confidence: 0.79
Overall Risk Level: high

Recommendation: review_required
Action: review_required

Agent Outputs (6):

  - feature_extraction
    Success: True
    Confidence: 1.00
    Risk Level: none
    Findings: 0

  - security_analysis
    Success: True
    Confidence: 0.85
    Risk Level: critical
    Findings: 2
      • SQL injection vulnerability detected
      • Missing input validation

  - logic_analysis
    Success: True
    Confidence: 0.75
    Risk Level: high
    Findings: 2
      • Potential infinite loop
      • Unreachable code detected

...
```

## 🔒 Security Notes

- **NO API KEYS** are included in code
- S3 and Gemini clients use mocked implementations
- Replace with actual credentials for production use

## 🎯 Exam Defense Points

1. **Architecture**: Clean separation of concerns, modular design
2. **Agent Autonomy**: Each agent is independent and specialized
3. **Deterministic Features**: Feature extraction before any LLM usage
4. **No Force Decisions**: System can defer when uncertain
5. **Conflict Handling**: Explicit disagreement detection and reporting
6. **Explainability**: All outputs include confidence and reasoning
7. **Extensibility**: Easy to add new agents or modify behavior

## 📝 Implementation Status

This is a **CODE SKELETON** with:
- ✅ Complete architecture
- ✅ All modules and classes defined
- ✅ Placeholder business logic
- ✅ Mocked external services (S3, Gemini)
- ✅ Working demonstration flow

**NOT INCLUDED**:
- Real AWS S3 integration
- Actual Gemini API calls
- Production error handling
- CI/CD pipeline
- Deployment scripts

## 🔧 Next Steps for Production

1. Replace mocked S3Reader with boto3 implementation
2. Configure actual Gemini API with proper credentials
3. Implement robust error handling and retry logic
4. Add comprehensive logging and monitoring
5. Create API endpoints if needed
6. Add unit tests and integration tests
7. Implement Git → S3 ingestion pipeline

## 📚 Technologies Used

- **Python**: Core language
- **boto3**: AWS S3 integration (mocked)
- **Google Gemini**: LLM for analysis (mocked)
- **Dataclasses**: Schema definitions
- **Logging**: System observability

## 👨‍💻 Developer Notes

- All agents inherit from `BaseAgent`
- Use `AgentOutput` schema for all agent returns
- Orchestrator manages workflow, never calls LLM directly
- Confidence must always be 0.0-1.0
- System defers on low confidence or conflicts

---

**Project Type**: Final Year Project  
**Domain**: AI + Software Engineering  
**Complexity**: Multi-agent system with LLM integration  
**Status**: Code skeleton ready for implementation
