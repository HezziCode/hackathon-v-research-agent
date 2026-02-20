"""Task models: ResearchTask, TaskRequest, TaskAccepted, TaskStatus, ArtifactRef."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Lifecycle states for a research task."""

    ACCEPTED = "accepted"
    PLANNING = "planning"
    SOURCING = "sourcing"
    ANALYZING = "analyzing"
    VERIFYING = "verifying"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    REJECTED = "rejected"
    BUDGET_EXCEEDED = "budget_exceeded"
    TIMED_OUT = "timed_out"


class PipelineStage(str, Enum):
    """The 5-agent pipeline stages."""

    PLANNER = "planner"
    SOURCE_FINDER = "source_finder"
    CONTENT_ANALYZER = "content_analyzer"
    FACT_CHECKER = "fact_checker"
    REPORT_WRITER = "report_writer"


class ArtifactRef(BaseModel):
    """Reference to a generated output file."""

    name: str
    content_type: str
    size_bytes: int = 0
    path: str


class TaskRequest(BaseModel):
    """Incoming task submission from user or A2A."""

    query: str = Field(..., min_length=10, max_length=5000)
    require_approval: bool = False
    budget_limit_usd: float = Field(default=1.0, ge=0.01, le=100.0)
    priority: str = Field(default="P2", pattern=r"^P[123]$")
    metadata: dict = Field(default_factory=dict)


class TaskAccepted(BaseModel):
    """Response after task is accepted."""

    task_id: str
    status: str = "accepted"
    workflow_instance_id: str | None = None
    created_at: datetime


class TaskStatusResponse(BaseModel):
    """Status polling response."""

    task_id: str
    status: TaskStatus
    current_stage: PipelineStage | None = None
    progress_pct: int = Field(default=0, ge=0, le=100)
    approval_pending: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


# Forward progress mapping for progress_pct calculation
STAGE_PROGRESS: dict[PipelineStage, int] = {
    PipelineStage.PLANNER: 20,
    PipelineStage.SOURCE_FINDER: 40,
    PipelineStage.CONTENT_ANALYZER: 60,
    PipelineStage.FACT_CHECKER: 80,
    PipelineStage.REPORT_WRITER: 95,
}


class ResearchTask(BaseModel):
    """Full task entity with all lifecycle fields."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str = Field(..., min_length=10, max_length=5000)
    status: TaskStatus = TaskStatus.ACCEPTED
    require_approval: bool = False
    budget_limit_usd: float = Field(default=1.0, ge=0.01, le=100.0)
    priority: str = Field(default="P2", pattern=r"^P[123]$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    workflow_instance_id: str | None = None
    current_stage: PipelineStage | None = None
    error_message: str | None = None
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query must not be blank")
        return v.strip()

    def advance_status(self, new_status: TaskStatus) -> None:
        """Update status with timestamp."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.utcnow()

    def to_status_response(self) -> TaskStatusResponse:
        """Convert to API response."""
        progress = 0
        if self.status == TaskStatus.COMPLETED:
            progress = 100
        elif self.current_stage:
            progress = STAGE_PROGRESS.get(self.current_stage, 0)

        return TaskStatusResponse(
            task_id=self.id,
            status=self.status,
            current_stage=self.current_stage,
            progress_pct=progress,
            error_message=self.error_message,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
