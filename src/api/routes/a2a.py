"""A2A Protocol endpoints: Agent Card + JSON-RPC 2.0."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["A2A"])

# ---------------------------------------------------------------------------
# Agent Card  (T057)
# ---------------------------------------------------------------------------

AGENT_CARD = {
    "name": "Research Analyst FTE",
    "description": "Autonomous multi-step web research agent that produces structured reports with citations and confidence scores.",
    "url": f"http://localhost:{settings.app_port}",
    "version": settings.app_version,
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": True,
    },
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text", "file"],
    "skills": [
        {
            "id": "web-research",
            "name": "Web Research",
            "description": "Multi-step research on any topic with 5-agent pipeline: Planner → Source Finder → Analyzer → Fact Checker → Report Writer",
            "tags": ["research", "analysis", "report", "fact-check"],
            "inputModes": ["text"],
            "outputModes": ["text", "file"],
        }
    ],
    "provider": {
        "organization": "Agent Factory",
        "url": "https://agentfactory.dev",
    },
}


@router.get("/.well-known/agent.json")
async def get_agent_card():
    """A2A Agent Card discovery endpoint."""
    return AGENT_CARD


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 endpoint  (T058)
# ---------------------------------------------------------------------------


@router.post("/a2a")
async def a2a_endpoint(request: Request):
    """A2A JSON-RPC 2.0 endpoint for inter-agent communication."""
    body = await request.json()

    jsonrpc = body.get("jsonrpc", "")
    method = body.get("method", "")
    req_id = body.get("id", "")
    params = body.get("params", {})

    if jsonrpc != "2.0":
        return JSONResponse(
            {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Invalid JSON-RPC version"}},
            status_code=400,
        )

    if method == "tasks/send":
        return await _handle_tasks_send(req_id, params)
    elif method == "tasks/get":
        return await _handle_tasks_get(req_id, params)
    elif method == "tasks/cancel":
        return await _handle_tasks_cancel(req_id, params)
    else:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}},
            status_code=400,
        )


async def _handle_tasks_send(req_id: str, params: dict) -> JSONResponse:
    """Handle tasks/send — create a research task from A2A message."""
    from src.api.main import save_task
    from src.models.task import ResearchTask

    message = params.get("message", {})
    parts = message.get("parts", [])
    query = ""
    for part in parts:
        if part.get("type") == "text":
            query = part.get("text", "")
            break

    if len(query) < 10:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Query too short (min 10 chars)"}},
            status_code=400,
        )

    task = ResearchTask(query=query)
    save_task(task)

    # Start workflow
    try:
        from dapr.ext.workflow import DaprWorkflowClient

        wf_client = DaprWorkflowClient()
        wf_client.schedule_new_workflow(
            workflow="research_workflow",
            input={"task_id": task.id, "query": task.query, "require_approval": False, "budget_limit_usd": 1.0},
            instance_id=task.id,
        )
        task.workflow_instance_id = task.id
        save_task(task)
    except Exception as e:
        logger.warning("A2A workflow start failed: %s", e)

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "id": task.id,
            "status": {"state": "submitted"},
            "artifacts": [],
        },
    })


async def _handle_tasks_get(req_id: str, params: dict) -> JSONResponse:
    """Handle tasks/get — return task status."""
    from src.api.main import get_task

    task_id = params.get("id", "")
    task = get_task(task_id)
    if not task:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Task not found"}},
            status_code=404,
        )

    artifacts = []
    for a in task.artifacts:
        artifacts.append({"name": a.name, "parts": [{"type": "file", "file": {"name": a.name, "mimeType": a.content_type}}]})

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "id": task.id,
            "status": {"state": task.status.value},
            "artifacts": artifacts,
        },
    })


async def _handle_tasks_cancel(req_id: str, params: dict) -> JSONResponse:
    """Handle tasks/cancel — terminate workflow."""
    from src.api.main import get_task

    task_id = params.get("id", "")
    task = get_task(task_id)
    if not task:
        return JSONResponse(
            {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Task not found"}},
            status_code=404,
        )

    try:
        from dapr.clients import DaprClient

        with DaprClient() as d:
            d.terminate_workflow(instance_id=task_id, workflow_component="dapr")
        task.advance_status(task.status.FAILED)
        task.error_message = "Cancelled via A2A"
        from src.api.main import save_task
        save_task(task)
    except Exception as e:
        logger.warning("A2A cancel failed: %s", e)

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {"id": task_id, "status": {"state": "canceled"}},
    })
