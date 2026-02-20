"""Research pipeline models: ResearchPlan, SourceCollection, Analysis."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# --- Research Plan (output of Research Planner) ---


class SubQuestion(BaseModel):
    """A decomposed sub-question from the research plan."""

    id: str = Field(..., pattern=r"^SQ\d+$")
    question: str
    priority: str = Field(..., pattern=r"^P[123]$")
    source_types: list[str] = Field(default_factory=list)


class ResearchPlan(BaseModel):
    """Output of the Research Planner agent."""

    task_id: str
    sub_questions: list[SubQuestion] = Field(..., min_length=3, max_length=7)
    scope_boundaries: list[str] = Field(default_factory=list)
    source_strategy: str = ""
    estimated_complexity: str = Field(default="moderate", pattern=r"^(simple|moderate|complex)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("sub_questions")
    @classmethod
    def at_least_one_p1(cls, v: list[SubQuestion]) -> list[SubQuestion]:
        if not any(sq.priority == "P1" for sq in v):
            raise ValueError("At least one sub-question must be P1 priority")
        return v


# --- Source Collection (output of Source Finder) ---


class Source(BaseModel):
    """A discovered source."""

    id: str = Field(..., pattern=r"^SRC-\d+$")
    url: str
    title: str
    publisher: str = ""
    date: str | None = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    credibility: str = Field(default="medium", pattern=r"^(high|medium|low)$")
    content_snippet: str = Field(default="", max_length=500)
    source_type: str = "news"


class SourceCollection(BaseModel):
    """Curated list of sources from Source Finder."""

    task_id: str
    sources: list[Source] = Field(..., min_length=5)
    coverage_matrix: dict[str, list[str]] = Field(default_factory=dict)
    total_sources: int = 0
    average_relevance: float = Field(default=0.0, ge=0.0, le=1.0)
    gaps: list[str] = Field(default_factory=list)

    def model_post_init(self, __context: object) -> None:
        if self.total_sources == 0:
            self.total_sources = len(self.sources)
        if self.average_relevance == 0.0 and self.sources:
            self.average_relevance = sum(s.relevance_score for s in self.sources) / len(self.sources)


# --- Analysis (output of Content Analyzer) ---


class KeyFinding(BaseModel):
    """A major finding extracted from sources."""

    id: str = Field(..., pattern=r"^KF-\d+$")
    title: str
    description: str
    data_points: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    sub_question_id: str


class Theme(BaseModel):
    """An identified theme/pattern."""

    title: str
    description: str
    finding_ids: list[str] = Field(default_factory=list)


class Contradiction(BaseModel):
    """Conflicting data points between sources."""

    claim_a: str
    source_a: str
    claim_b: str
    source_b: str
    resolution: str | None = None


class Analysis(BaseModel):
    """Cross-referenced findings from Content Analyzer."""

    task_id: str
    key_findings: list[KeyFinding] = Field(default_factory=list)
    themes: list[Theme] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    data_gaps: list[str] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
