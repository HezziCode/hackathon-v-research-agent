# Quickstart: Research Analyst Digital FTE

**Feature**: 001-research-analyst-fte | **Date**: 2026-02-19

## Prerequisites

- Python 3.12+
- Docker + Docker Compose (for Redis, Kafka, Dapr)
- API keys: `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`
- Optional: `OPENAI_API_KEY` (for OpenAI models), `GEMINI_API_KEY` (for Gemini fact-checker)

## 1. Clone & Install

```bash
# Install Python dependencies
pip install -r requirements.txt
```

**requirements.txt** (key packages):
```
fastapi>=0.115.0
uvicorn>=0.30.0
openai-agents[litellm]>=0.7.0
anthropic>=0.40.0
dapr>=1.14.0
dapr-ext-workflow>=1.14.0
dapr-ext-fastapi>=1.14.0
pydantic>=2.0.0
httpx>=0.27.0
weasyprint>=62.0
markdown>=3.7
prometheus-client>=0.21.0
```

## 2. Start Infrastructure

```bash
docker-compose up -d
```

**docker-compose.yaml** starts:
- **Redis** (port 6379) — Dapr state store for workflow checkpointing
- **Kafka** (port 9092) — Event backbone via Dapr Pub/Sub
- **Zookeeper** (port 2181) — Kafka dependency

## 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# TAVILY_API_KEY=tvly-...
# GEMINI_API_KEY=... (optional)
```

## 4. Run with Dapr

```bash
dapr run --app-id research-analyst \
         --app-port 8000 \
         --dapr-http-port 3500 \
         --dapr-grpc-port 50001 \
         --resources-path ./kubernetes/dapr \
         -- uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## 5. Submit a Research Task

```bash
# Submit task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current state of AI agents market in 2026?",
    "require_approval": false,
    "budget_limit_usd": 1.0
  }'
# Response: {"task_id": "abc-123", "status": "accepted", ...}

# Check status
curl http://localhost:8000/tasks/abc-123/status

# Download artifacts (after completion)
curl http://localhost:8000/tasks/abc-123/artifacts
```

## 6. With Human Approval

```bash
# Submit with approval gates
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents market analysis", "require_approval": true}'

# Check status (will show "awaiting_approval")
curl http://localhost:8000/tasks/{id}/status

# Approve the research plan
curl -X POST http://localhost:8000/workflows/{workflow_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true, "reason": "Plan looks good"}'
```

## 7. A2A Discovery

```bash
# Get Agent Card
curl http://localhost:8000/.well-known/agent.json

# Send task via A2A protocol
curl -X POST http://localhost:8000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-1",
    "method": "tasks/send",
    "params": {
      "id": "task-001",
      "sessionId": "sess-001",
      "message": {
        "role": "user",
        "parts": [{"type": "text", "text": "Research AI agents market"}]
      }
    }
  }'
```

## 8. Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires running infrastructure)
pytest tests/integration/ -v

# Contract tests (A2A protocol compliance)
pytest tests/contract/ -v
```

## Architecture Quick Reference

```
Request → FastAPI (L3)
       → Dapr Workflow (L2) starts
       → OpenAI Agents SDK Coordinator (L4)
           → Research Planner (via LiteLLM → Claude)
           → [Approval Gate if enabled]
           → Source Finder (via Claude Agent SDK → Tavily MCP)
           → Content Analyzer (via Claude Agent SDK)
           → Fact Checker (via LiteLLM → Gemini)
           → Report Writer (via LiteLLM → Claude)
       → Artifacts stored
       → Kafka events published (L1)
       → Response via REST or A2A (L7)
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /tasks` | Submit | Start a research task |
| `GET /tasks/{id}/status` | Poll | Check task progress |
| `GET /tasks/{id}/artifacts` | Download | Get output files |
| `POST /workflows/{id}/approve` | Approve | Human approval gate |
| `GET /.well-known/agent.json` | Discovery | A2A Agent Card |
| `POST /a2a` | A2A | JSON-RPC 2.0 endpoint |
| `GET /health` | Health | Service health check |
| `GET /metrics` | Monitor | Prometheus metrics |
