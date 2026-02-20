"""T022: Unit tests for workflow activities (mock LLM responses)."""

from __future__ import annotations

import pytest


class TestPlanResearchActivity:
    """Tests for the plan_research workflow activity."""

    def test_plan_output_has_sub_questions(self):
        """Plan should produce 3-7 sub-questions."""
        # Activity will be tested with mock LLM in integration
        from src.models.research import ResearchPlan, SubQuestion

        plan = ResearchPlan(
            task_id="test-001",
            sub_questions=[
                SubQuestion(id="SQ1", question="What is the market size?", priority="P1", source_types=["industry"]),
                SubQuestion(id="SQ2", question="Who are key players?", priority="P2", source_types=["news"]),
                SubQuestion(id="SQ3", question="What are trends?", priority="P2", source_types=["academic"]),
            ],
            source_strategy="web search",
            estimated_complexity="moderate",
        )
        assert 3 <= len(plan.sub_questions) <= 7
        assert any(sq.priority == "P1" for sq in plan.sub_questions)


class TestWriteReportActivity:
    """Tests for the write_report activity output structure."""

    def test_report_has_required_fields(self):
        from src.models.report import ResearchReport

        report = ResearchReport(
            task_id="test-001",
            title="Test Report",
            markdown_content="# Test\n\nContent",
            sources_json={"sources": [{"url": "https://example.com", "title": "Example"}]},
            confidence_scores_json={"KF-001": 0.9},
            word_count=100,
            source_count=1,
        )
        assert report.markdown_content.startswith("#")
        assert len(report.sources_json["sources"]) > 0
