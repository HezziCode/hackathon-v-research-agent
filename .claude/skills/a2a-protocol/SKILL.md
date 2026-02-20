---
name: a2a-protocol
description: |
  Use when implementing Agent-to-Agent (A2A) protocol for inter-FTE discovery and collaboration.
  Use when creating Agent Cards, handling A2A JSON-RPC endpoints, or enabling multi-FTE task delegation.
  NOT when building internal agent orchestration (use openai-agents-sdk instead).
---

# A2A Protocol — Inter-FTE Collaboration

## Overview

The A2A (Agent-to-Agent) Protocol (L7) enables Digital FTEs to discover and collaborate with each other. It uses Agent Cards for capability discovery and JSON-RPC over HTTP/SSE for communication. Supports long-running tasks (hours to days).

## Agent Card — Discovery Endpoint

Every Digital FTE MUST expose an Agent Card at `/.well-known/agent.json`:

```json
{
  "name": "Research Analyst FTE",
  "description": "Multi-step research, competitive analysis, report generation",
  "url": "https://research-fte.digital-ftes.svc.cluster.local/a2a",
  "version": "1.0.0",
  "capabilities": {
    "computer_use": false,
    "bash_execution": true,
    "mcp_servers": ["web-search", "github", "google-drive"],
    "skills": ["research-planner", "source-finder", "content-analyzer",
               "fact-checker", "report-writer"]
  },
  "skills": [
    {"id": "competitive-analysis", "description": "Analyze competitors in a market"},
    {"id": "market-research", "description": "Research market size and trends"},
    {"id": "tech-review", "description": "Evaluate technology solutions"}
  ],
  "authentication": {
    "type": "oauth2",
    "flows": ["client_credentials"]
  },
  "supportedModes": ["text", "artifacts", "streaming"]
}
```

## A2A JSON-RPC Endpoints

### Sending a Task

```python
@app.post("/a2a")
async def handle_a2a(request: dict, bg: BackgroundTasks):
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    if method == "tasks/send":
        task_id = str(uuid.uuid4())
        bg.add_task(start_workflow, task_id=task_id, task=params["message"])
        return {
            "jsonrpc": "2.0", "id": request_id,
            "result": {"task_id": task_id, "status": "accepted"}
        }

    elif method == "tasks/status":
        status = await get_workflow_status(params["task_id"])
        return {"jsonrpc": "2.0", "id": request_id, "result": status}
```

### Calling Another FTE

```python
import httpx

async def delegate_to_fte(fte_url: str, task: str, skill: str = None):
    """Send a task to another Digital FTE via A2A."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{fte_url}/a2a", json={
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tasks/send",
            "params": {"message": task, "skill": skill}
        })
        return response.json()["result"]
```

## Multi-FTE Collaboration Pattern

```
Research FTE ──publishes──→ fte.handoffs.research
                                    │
Writer FTE ──subscribes──→──────────┘
                                    │
                          ──publishes──→ fte.results.completed
```

## Key Rules

1. Agent Card MUST be at `/.well-known/agent.json`
2. A2A uses JSON-RPC 2.0 over HTTP/SSE
3. Long-running tasks return task_id immediately, poll for status
4. Authentication via OAuth2 client_credentials flow
5. Kafka for async handoffs between FTEs
6. Agent Cards describe capabilities — keep them accurate

## Dependencies

```
httpx>=0.27.0
fastapi>=0.115.0
```
