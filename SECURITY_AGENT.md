# Security Analysis Agent Documentation

## 1. Input & Callers
*   **Called By**: `Orchestrator._run_analysis_agents` (in `backend/orchestrator/orchestrator.py`)
*   **Input Data**:
    *   `features`: A dictionary of curated security features (from `RoutingPolicy`).
    *   `snippets`: A list of `CodeSnippet` objects (max 3). These contain the actual source code to analyze.
*   **Who Feeds It**: The `RoutingPolicy` extracts these inputs from the raw codebase and passes them to the Orchestrator, which then passes them to the agent.
*   **Restrictions**: This agent **CANNOT** access S3 or the full codebase directly. It only sees what it is fed.

## 2. Internals & Logic
*   **Core Library**: `google.generativeai` (via `GeminiClient` wrapper).
*   **Logic Flow**:
    1.  **Validation**: Checks if it received too many snippets (>5) or if snippets are too large (>500 chars).
    2.  **LLM Call**: For each snippet, it calls `GeminiClient.generate()` with a specific prompt.
    3.  **Prompt Strategy**: "Analyze this code snippet for SECURITY RISKS ONLY." It specifically asks for SQL injection, auth issues, etc.
    4.  **Parsing**: It expects a JSON response containing `findings` and `confidence`.

## 3. The LLM Call (Detail)
The agent constructs a prompt similar to this:
```text
Analyze this code snippet for SECURITY RISKS ONLY.
Location: {filename}:{line}
Context: {function name, etc}

Code:
{snippet content}

Identify:
1. SQL injection
2. Auth issues
...

Return JSON:
{
    "findings": [{"type": "...", "severity": "..."}],
    "confidence": 0.0-1.0
}
```
The LLM acts as the reasoning engine to detect vulnerabilities based on the text provided.

## 4. Confidence Calculation
*   **Source**: The confidence score comes **directly from the LLM's JSON response**.
*   **Aggregation**: If multiple snippets are analyzed, the agent **averages** the confidence scores from all LLM calls.
*   **Fallback**: If the LLM fails to return a confidence score, it defaults to `0.7`.

## 5. Output
Returns an `AgentOutput` object containing:
*   `agent_type`: `SECURITY_ANALYSIS`
*   `confidence`: (Float 0.0-1.0) Validated confidence score.
*   `findings`: List of security issues found (e.g., "SQL Injection detected at line 45").
*   `risk_level`: The highest severity found (e.g., `CRITICAL`, `HIGH`).
