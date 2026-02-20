"""Human approval workflow endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Workflows"])


class ApprovalRequest(BaseModel):
    approved: bool
    reason: str = ""
    modifications: dict | None = None


class ApprovalResponse(BaseModel):
    workflow_id: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# POST /workflows/{id}/approve  (T045 — implemented in Phase 4)
# ---------------------------------------------------------------------------


@router.post("/workflows/{workflow_id}/approve", response_model=ApprovalResponse)
async def approve_workflow(workflow_id: str, request: ApprovalRequest):
    """Approve or reject a workflow stage."""
    try:
        from dapr.clients import DaprClient

        with DaprClient() as d:
            d.raise_workflow_event(
                instance_id=workflow_id,
                workflow_component="dapr",
                event_name="plan_approval",
                event_data={"approved": request.approved, "reason": request.reason},
            )
        status = "resumed" if request.approved else "rejected"
        return ApprovalResponse(
            workflow_id=workflow_id,
            status=status,
            message=f"Workflow {status} successfully",
        )
    except Exception as e:
        logger.error("Approval failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# GET /workflows/{id}/status  (T046)
# ---------------------------------------------------------------------------


@router.get("/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Return detailed workflow status."""
    try:
        from dapr.ext.workflow import DaprWorkflowClient

        wf_client = DaprWorkflowClient()
        state = wf_client.get_workflow_state(instance_id=workflow_id)
        return {
            "workflow_id": workflow_id,
            "runtime_status": state.runtime_status.name if state else "UNKNOWN",
            "created_at": str(state.created_at) if state else None,
            "last_updated_at": str(state.last_updated_at) if state else None,
        }
    except Exception as e:
        logger.error("Workflow status failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
