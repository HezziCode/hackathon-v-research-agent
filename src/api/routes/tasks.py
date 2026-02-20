"""Task management endpoints: submit, status, artifacts."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from prometheus_client import Counter, Gauge, Histogram, generate_latest

from src.models.task import (
    ArtifactRef,
    TaskAccepted,
    TaskRequest,
    TaskStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tasks"])

# ---------------------------------------------------------------------------
# T067: Prometheus Metrics
# ---------------------------------------------------------------------------

TASK_SUBMISSIONS = Counter("task_submissions_total", "Total research tasks submitted")
TASK_DURATION = Histogram("task_duration_seconds", "Research task end-to-end duration")
AGENT_STEP_DURATION = Histogram(
    "agent_step_duration_seconds",
    "Duration of individual agent steps",
    ["agent"],
)
ACTIVE_TASKS = Gauge("active_tasks", "Currently running research tasks")
LLM_COST_TOTAL = Counter("llm_cost_usd_total", "Total LLM cost in USD")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


# ---------------------------------------------------------------------------
# POST /tasks  (T024 — wired in Phase 3)
# ---------------------------------------------------------------------------


@router.post("/tasks", response_model=TaskAccepted, status_code=202)
async def submit_task(request: TaskRequest):
    """Accept a research query and start the pipeline."""
    from src.api.main import save_task
    from src.models.task import ResearchTask

    task = ResearchTask(
        query=request.query,
        require_approval=request.require_approval,
        budget_limit_usd=request.budget_limit_usd,
        priority=request.priority,
        metadata=request.metadata,
    )
    save_task(task)
    TASK_SUBMISSIONS.inc()
    ACTIVE_TASKS.inc()

    # Start Dapr workflow
    workflow_id: str | None = None
    try:
        from dapr.ext.workflow import DaprWorkflowClient

        wf_client = DaprWorkflowClient()
        instance_id = wf_client.schedule_new_workflow(
            workflow="research_workflow",
            input={
                "task_id": task.id,
                "query": task.query,
                "require_approval": task.require_approval,
                "budget_limit_usd": task.budget_limit_usd,
            },
            instance_id=task.id,
        )
        workflow_id = instance_id
        task.workflow_instance_id = workflow_id
        save_task(task)
        logger.info("Workflow started: %s", workflow_id)
    except Exception as e:
        logger.warning("Could not start Dapr workflow: %s", e)

    return TaskAccepted(
        task_id=task.id,
        status="accepted",
        workflow_instance_id=workflow_id,
        created_at=task.created_at,
    )


# ---------------------------------------------------------------------------
# GET /tasks/{id}/status  (T025)
# ---------------------------------------------------------------------------


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Return current task status."""
    from src.api.main import get_task

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_status_response()


# ---------------------------------------------------------------------------
# GET /tasks/{id}/artifacts  (T026)
# ---------------------------------------------------------------------------


@router.get("/tasks/{task_id}/artifacts")
async def get_task_artifacts(task_id: str):
    """List available artifacts for a completed task."""
    from src.api.main import get_task

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "artifacts": [a.model_dump() for a in task.artifacts],
    }


# ---------------------------------------------------------------------------
# GET /tasks/{id}/artifacts/{name}  (T027)
# ---------------------------------------------------------------------------


@router.get("/tasks/{task_id}/artifacts/{artifact_name}")
async def download_artifact(task_id: str, artifact_name: str):
    """Download a specific artifact file."""
    from src.api.main import get_task

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    artifact: ArtifactRef | None = None
    for a in task.artifacts:
        if a.name == artifact_name:
            artifact = a
            break

    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = Path(artifact.path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact file missing")

    return FileResponse(
        path=str(file_path),
        media_type=artifact.content_type,
        filename=artifact.name,
    )


# ---------------------------------------------------------------------------
# GET /metrics  (T069)
# ---------------------------------------------------------------------------


@router.get("/metrics")
async def get_metrics():
    """Expose Prometheus metrics in text exposition format."""
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
