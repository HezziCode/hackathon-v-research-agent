"""Report models: VerificationReport, ResearchReport."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# --- Verification Report (output of Fact Checker) ---


class VerifiedClaim(BaseModel):
    """A claim that passed fact-checking."""

    finding_id: str
    verification_status: str = Field(
        default="verified", pattern=r"^(verified|needs_review|disputed)$"
    )
    corroborating_sources: int = Field(default=0, ge=0)
    notes: str = ""


class FlaggedClaim(BaseModel):
    """A claim that was flagged for review."""

    finding_id: str
    reason: str
    suggestion: str = ""


class VerificationReport(BaseModel):
    """Fact-checking results from the Fact Checker agent."""

    task_id: str
    verified_claims: list[VerifiedClaim] = Field(default_factory=list)
    flagged_claims: list[FlaggedClaim] = Field(default_factory=list)
    unverifiable: list[str] = Field(default_factory=list)
    overall_reliability: float = Field(default=0.0, ge=0.0, le=1.0)


# --- Research Report (output of Report Writer) ---


class ResearchReport(BaseModel):
    """Final output package from Report Writer."""

    task_id: str
    title: str
    markdown_content: str
    pdf_path: str | None = None
    sources_json: dict = Field(default_factory=dict)
    confidence_scores_json: dict = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    word_count: int = 0
    source_count: int = 0
