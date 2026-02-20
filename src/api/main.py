"""FastAPI application with Dapr Workflow runtime lifecycle."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import a2a, tasks, workflows
from src.config import settings
from src.models.task import ResearchTask

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory task store (T019)
# ---------------------------------------------------------------------------

task_store: dict[str, ResearchTask] = {}


def get_task(task_id: str) -> ResearchTask | None:
    return task_store.get(task_id)


def save_task(task: ResearchTask) -> None:
    task_store[task.id] = task


def list_tasks() -> list[ResearchTask]:
    return list(task_store.values())


# ---------------------------------------------------------------------------
# Dapr Workflow runtime lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop Dapr WorkflowRuntime with the FastAPI server."""
    logger.info("Starting Research Analyst FTE...")

    # Import here to avoid issues when Dapr sidecar is not running (e.g. tests)
    try:
        from dapr.ext.workflow import WorkflowRuntime

        from src.workflows.activities import (
            analyze_content,
            find_sources,
            plan_research,
            verify_facts,
            write_report,
        )
        from src.workflows.research_workflow import research_workflow

        wfr = WorkflowRuntime()
        wfr.register_workflow(research_workflow)
        wfr.register_activity(plan_research)
        wfr.register_activity(find_sources)
        wfr.register_activity(analyze_content)
        wfr.register_activity(verify_facts)
        wfr.register_activity(write_report)
        wfr.start()
        logger.info("Dapr WorkflowRuntime started")
        yield
        wfr.shutdown()
        logger.info("Dapr WorkflowRuntime stopped")
    except Exception as e:
        logger.warning("Dapr WorkflowRuntime not available: %s — running without workflows", e)
        yield


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Research Analyst Digital FTE — autonomous multi-step web research agent",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(workflows.router)
app.include_router(a2a.router)
