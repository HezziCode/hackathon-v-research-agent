"""T037: Workflow activities — each calls the corresponding agent."""

from __future__ import annotations

import json
import logging
from typing import Any

from src.config import settings

logger = logging.getLogger(__name__)


async def _run_agent_step(agent, input_text: str) -> str:
    """Run a single OpenAI Agents SDK agent and return text output."""
    from agents import Runner

    result = await Runner.run(agent, input=input_text)
    return result.final_output if hasattr(result, "final_output") else str(result)


def _update_task_status(task_id: str, status: str, stage: str | None = None) -> None:
    """Update task in the in-memory store."""
    try:
        from src.api.main import get_task, save_task
        from src.models.task import PipelineStage, TaskStatus

        task = get_task(task_id)
        if task:
            task.advance_status(TaskStatus(status))
            if stage:
                task.current_stage = PipelineStage(stage)
            save_task(task)
    except Exception as e:
        logger.warning("Could not update task status: %s", e)


def _publish_event(topic: str, data: dict) -> None:
    """Publish event to Kafka via Dapr pub/sub (T039)."""
    try:
        from dapr.clients import DaprClient

        with DaprClient() as d:
            d.publish_event(
                pubsub_name="pubsub",
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json",
            )
        logger.info("Published event to %s", topic)
    except Exception as e:
        logger.warning("Could not publish event: %s", e)


# ---------------------------------------------------------------------------
# Activity: plan_research
# ---------------------------------------------------------------------------


def plan_research(ctx, input_data: dict) -> dict:
    """Research Planner activity — decomposes query into sub-questions."""
    import asyncio

    task_id = input_data["task_id"]
    query = input_data["query"]

    _update_task_status(task_id, "planning", "planner")
    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "planner", "status": "started"})

    from src.agents.simple_agents import research_planner

    result = asyncio.get_event_loop().run_until_complete(_run_agent_step(
        research_planner,
        f"Create a research plan for: {query}",
    ))

    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "planner", "status": "completed"})
    _publish_event("fte.audit.actions", {"task_id": task_id, "action": "plan_created", "agent": "research_planner"})

    return {"task_id": task_id, "plan": result, "query": query}


# ---------------------------------------------------------------------------
# Activity: find_sources
# ---------------------------------------------------------------------------


def find_sources(ctx, input_data: dict) -> dict:
    """Source Finder activity — discovers sources via web search."""
    import asyncio

    task_id = input_data["task_id"]

    _update_task_status(task_id, "sourcing", "source_finder")
    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "source_finder", "status": "started"})

    from src.agents.simple_agents import source_finder

    plan_text = input_data.get("plan", "")
    result = asyncio.get_event_loop().run_until_complete(_run_agent_step(
        source_finder,
        f"Find sources for this research plan:\n{plan_text}",
    ))

    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "source_finder", "status": "completed"})
    _publish_event("fte.audit.actions", {"task_id": task_id, "action": "sources_found", "agent": "source_finder"})

    return {"task_id": task_id, "sources": result, "plan": plan_text, "query": input_data.get("query", "")}


# ---------------------------------------------------------------------------
# Activity: analyze_content
# ---------------------------------------------------------------------------


def analyze_content(ctx, input_data: dict) -> dict:
    """Content Analyzer activity — cross-references sources."""
    import asyncio

    task_id = input_data["task_id"]

    _update_task_status(task_id, "analyzing", "content_analyzer")
    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "content_analyzer", "status": "started"})

    from src.agents.simple_agents import content_analyzer

    sources_text = input_data.get("sources", "")
    result = asyncio.get_event_loop().run_until_complete(_run_agent_step(
        content_analyzer,
        f"Analyze these sources:\n{sources_text}",
    ))

    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "content_analyzer", "status": "completed"})
    _publish_event("fte.audit.actions", {"task_id": task_id, "action": "analysis_complete", "agent": "content_analyzer"})

    return {
        "task_id": task_id,
        "analysis": result,
        "sources": sources_text,
        "query": input_data.get("query", ""),
    }


# ---------------------------------------------------------------------------
# Activity: verify_facts
# ---------------------------------------------------------------------------


def verify_facts(ctx, input_data: dict) -> dict:
    """Fact Checker activity — verifies claims via cross-source triangulation."""
    import asyncio

    task_id = input_data["task_id"]

    _update_task_status(task_id, "verifying", "fact_checker")
    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "fact_checker", "status": "started"})

    from src.agents.simple_agents import fact_checker

    analysis_text = input_data.get("analysis", "")
    result = asyncio.get_event_loop().run_until_complete(_run_agent_step(
        fact_checker,
        f"Verify the findings in this analysis:\n{analysis_text}",
    ))

    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "fact_checker", "status": "completed"})
    _publish_event("fte.audit.actions", {"task_id": task_id, "action": "facts_verified", "agent": "fact_checker"})

    return {
        "task_id": task_id,
        "verification": result,
        "analysis": analysis_text,
        "query": input_data.get("query", ""),
    }


# ---------------------------------------------------------------------------
# Activity: write_report
# ---------------------------------------------------------------------------


def write_report(ctx, input_data: dict) -> dict:
    """Report Writer activity — generates Markdown report + JSON metadata."""
    import asyncio

    task_id = input_data["task_id"]

    _update_task_status(task_id, "reporting", "report_writer")
    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "report_writer", "status": "started"})

    from src.agents.simple_agents import report_writer

    query = input_data.get("query", "")
    analysis = input_data.get("analysis", "")
    verification = input_data.get("verification", "")

    result = asyncio.get_event_loop().run_until_complete(_run_agent_step(
        report_writer,
        f"Write a research report based on:\nQuery: {query}\nAnalysis: {analysis}\nVerification: {verification}",
    ))

    # Save artifacts
    import os
    artifacts_dir = f"artifacts/{task_id}"
    os.makedirs(artifacts_dir, exist_ok=True)

    # Save markdown report
    md_path = f"{artifacts_dir}/research-report.md"
    with open(md_path, "w") as f:
        f.write(result)

    # Save sources.json and confidence-scores.json (attempt to parse from result)
    sources_path = f"{artifacts_dir}/sources.json"
    scores_path = f"{artifacts_dir}/confidence-scores.json"

    try:
        parsed = json.loads(result)
        with open(sources_path, "w") as f:
            json.dump(parsed.get("sources_json", {"sources": []}), f, indent=2)
        with open(scores_path, "w") as f:
            json.dump(parsed.get("confidence_scores_json", {}), f, indent=2)
        md_content = parsed.get("markdown_content", result)
        with open(md_path, "w") as f:
            f.write(md_content)
    except (json.JSONDecodeError, AttributeError):
        with open(sources_path, "w") as f:
            json.dump({"sources": [], "note": "Could not parse structured output"}, f, indent=2)
        with open(scores_path, "w") as f:
            json.dump({"note": "Could not parse structured output"}, f, indent=2)

    # Generate PDF (T052)
    pdf_path = f"{artifacts_dir}/research-report.pdf"
    try:
        from src.tools.pdf_export import markdown_to_pdf
        with open(md_path) as f:
            md_text = f.read()
        markdown_to_pdf(md_text, pdf_path)
    except Exception as e:
        logger.warning("PDF generation failed: %s", e)
        pdf_path = ""

    # Wire completion to task store (T040)
    try:
        from src.api.main import get_task, save_task
        from src.models.task import ArtifactRef, TaskStatus

        task = get_task(task_id)
        if task:
            task.advance_status(TaskStatus.COMPLETED)
            task.artifacts = [
                ArtifactRef(name="research-report.md", content_type="text/markdown", path=md_path, size_bytes=os.path.getsize(md_path)),
                ArtifactRef(name="sources.json", content_type="application/json", path=sources_path, size_bytes=os.path.getsize(sources_path)),
                ArtifactRef(name="confidence-scores.json", content_type="application/json", path=scores_path, size_bytes=os.path.getsize(scores_path)),
            ]
            if pdf_path and os.path.exists(pdf_path):
                task.artifacts.append(
                    ArtifactRef(name="research-report.pdf", content_type="application/pdf", path=pdf_path, size_bytes=os.path.getsize(pdf_path))
                )
            save_task(task)
    except Exception as e:
        logger.warning("Could not update task with artifacts: %s", e)

    _publish_event("fte.status.updates", {"task_id": task_id, "stage": "report_writer", "status": "completed"})
    _publish_event("fte.audit.actions", {"task_id": task_id, "action": "report_written", "agent": "report_writer"})

    return {"task_id": task_id, "report": result, "artifacts_dir": artifacts_dir}
