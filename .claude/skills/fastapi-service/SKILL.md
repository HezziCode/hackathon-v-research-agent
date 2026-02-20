---
name: fastapi-service
description: |
  Use when creating the HTTP interface layer for a Digital FTE including A2A protocol endpoints,
  task submission APIs, webhook handlers, human approval endpoints, and health checks.
  NOT when building agent logic or orchestration (use openai-agents-sdk or claude-agent-sdk).
---

# FastAPI Service — HTTP Interface Layer

## Overview

FastAPI serves as the HTTP interface layer (L3) for Digital FTEs. It handles A2A protocol endpoints for inter-FTE discovery and collaboration, task submission, webhook ingestion, human-in-the-loop approval gates, and Kubernetes health checks.

## Standard Endpoint Structure

| Endpoint Type | Route | Purpose |
|--------------|-------|---------|
| A2A Discovery | `GET /.well-known/agent.json` | Agent Card for FTE discovery |
| A2A Tasks | `POST /a2a` | Receive tasks from other FTEs |
| Task Submission | `POST /tasks` | Users/systems submit tasks |
| Task Status | `GET /tasks/{id}/status` | Query workflow status |
| Task Artifacts | `GET /tasks/{id}/artifacts` | Get completed task outputs |
| Human Approval | `POST /workflows/{id}/approve` | Manager approval gate |
| Webhooks | `POST /webhooks/{service}` | Slack, GitHub events |
| Health | `GET /health`, `GET /ready` | K8s liveness/readiness |

## Application Skeleton

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dapr.clients import DaprClient
import uuid

app = FastAPI(title="Digital FTE Service", version="1.0.0")

class TaskRequest(BaseModel):
    task: str
    context: dict | None = None
    require_approval: bool = False

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

@app.post("/tasks", response_model=TaskResponse)
async def submit_task(request: TaskRequest, bg: BackgroundTasks):
    task_id = str(uuid.uuid4())
    bg.add_task(start_workflow, task_id, request.task)
    return TaskResponse(task_id=task_id, status="accepted", message="Task submitted")
```

## A2A Agent Card

```python
@app.get("/.well-known/agent.json")
async def get_agent_card():
    return {
        "name": "Research Analyst FTE",
        "description": "Multi-step research and report generation",
        "url": "https://research-fte.svc.cluster.local/a2a",
        "version": "1.0.0",
        "capabilities": {
            "skills": ["research-planner", "source-finder", "report-writer"],
            "mcp_servers": ["web-search", "github"]
        },
        "authentication": {"type": "oauth2", "flows": ["client_credentials"]},
        "supportedModes": ["text", "artifacts", "streaming"]
    }
```

## Human-in-the-Loop Pattern

```python
@app.post("/workflows/{workflow_id}/approve")
async def approve_workflow(workflow_id: str, approval: dict):
    async with DaprClient() as client:
        await client.raise_workflow_event(
            instance_id=workflow_id,
            workflow_component="dapr",
            event_name="human_approval",
            event_data={"approved": approval.get("approved", False)}
        )
    return {"status": "recorded", "workflow_id": workflow_id}
```

## Key Rules

1. Always return 202 Accepted for async tasks — process in background
2. All task execution goes through Dapr Workflows for durability
3. A2A Agent Card MUST be at `/.well-known/agent.json`
4. Health checks MUST verify Dapr sidecar connectivity
5. Use Pydantic models for all request/response validation
6. CORS middleware for web client access

## Dependencies

```
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.0.0
dapr>=1.14.0
```
