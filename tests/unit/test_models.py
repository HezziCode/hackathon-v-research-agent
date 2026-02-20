"""T021: Unit tests for all Pydantic models."""

import pytest

from src.models.task import (
    ArtifactRef,
    PipelineStage,
    ResearchTask,
    TaskRequest,
    TaskStatus,
)
from src.models.research import (
    Analysis,
    KeyFinding,
    ResearchPlan,
    Source,
    SourceCollection,
    SubQuestion,
)
from src.models.report import ResearchReport, VerificationReport, VerifiedClaim


class TestTaskRequest:
    def test_valid_request(self):
        req = TaskRequest(query="What is the AI agents market size in 2026?")
        assert req.query == "What is the AI agents market size in 2026?"
        assert req.require_approval is False
        assert req.budget_limit_usd == 1.0
        assert req.priority == "P2"

    def test_query_too_short(self):
        with pytest.raises(Exception):
            TaskRequest(query="short")

    def test_budget_limits(self):
        with pytest.raises(Exception):
            TaskRequest(query="Valid query for testing purposes", budget_limit_usd=0.001)
        with pytest.raises(Exception):
            TaskRequest(query="Valid query for testing purposes", budget_limit_usd=200.0)

    def test_priority_validation(self):
        req = TaskRequest(query="Valid query for testing purposes", priority="P1")
        assert req.priority == "P1"


class TestResearchTask:
    def test_default_creation(self):
        task = ResearchTask(query="What is the current state of AI agents?")
        assert task.status == TaskStatus.ACCEPTED
        assert task.id is not None
        assert task.budget_limit_usd == 1.0

    def test_advance_status(self):
        task = ResearchTask(query="What is the current state of AI agents?")
        task.advance_status(TaskStatus.PLANNING)
        assert task.status == TaskStatus.PLANNING

    def test_completed_sets_timestamp(self):
        task = ResearchTask(query="What is the current state of AI agents?")
        task.advance_status(TaskStatus.COMPLETED)
        assert task.completed_at is not None

    def test_status_response(self):
        task = ResearchTask(query="What is the current state of AI agents?")
        task.current_stage = PipelineStage.CONTENT_ANALYZER
        resp = task.to_status_response()
        assert resp.progress_pct == 60


class TestResearchPlan:
    def test_valid_plan(self):
        plan = ResearchPlan(
            task_id="test-123",
            sub_questions=[
                SubQuestion(id="SQ1", question="Market size?", priority="P1", source_types=["industry"]),
                SubQuestion(id="SQ2", question="Key players?", priority="P2", source_types=["news"]),
                SubQuestion(id="SQ3", question="Trends?", priority="P2", source_types=["academic"]),
            ],
            source_strategy="web search + academic databases",
        )
        assert len(plan.sub_questions) == 3

    def test_no_p1_fails(self):
        with pytest.raises(Exception):
            ResearchPlan(
                task_id="test-123",
                sub_questions=[
                    SubQuestion(id="SQ1", question="Q1?", priority="P2", source_types=[]),
                    SubQuestion(id="SQ2", question="Q2?", priority="P3", source_types=[]),
                    SubQuestion(id="SQ3", question="Q3?", priority="P2", source_types=[]),
                ],
            )

    def test_too_few_questions_fails(self):
        with pytest.raises(Exception):
            ResearchPlan(
                task_id="test-123",
                sub_questions=[
                    SubQuestion(id="SQ1", question="Q1?", priority="P1", source_types=[]),
                ],
            )


class TestSourceCollection:
    def test_valid_collection(self):
        sources = [
            Source(id=f"SRC-{i:03d}", url=f"https://example.com/{i}", title=f"Source {i}", relevance_score=0.8)
            for i in range(5)
        ]
        coll = SourceCollection(task_id="test-123", sources=sources)
        assert coll.total_sources == 5
        assert coll.average_relevance == 0.8

    def test_too_few_sources_fails(self):
        with pytest.raises(Exception):
            SourceCollection(
                task_id="test-123",
                sources=[Source(id="SRC-001", url="https://example.com", title="Only one", relevance_score=0.5)],
            )


class TestVerificationReport:
    def test_valid_report(self):
        report = VerificationReport(
            task_id="test-123",
            verified_claims=[VerifiedClaim(finding_id="KF-001", corroborating_sources=3)],
            overall_reliability=0.85,
        )
        assert report.overall_reliability == 0.85


class TestResearchReport:
    def test_valid_report(self):
        report = ResearchReport(
            task_id="test-123",
            title="AI Agents Market Analysis",
            markdown_content="# Report\n\nContent here.",
            sources_json={"sources": []},
            confidence_scores_json={"scores": {}},
            word_count=150,
            source_count=10,
        )
        assert report.word_count == 150
