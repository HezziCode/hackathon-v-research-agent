"""T035: OpenAI Agents SDK coordinator with handoffs and guardrails."""

from __future__ import annotations

import json
import logging
from typing import Any

from agents import Agent, InputGuardrail, Runner
from agents.extensions.models.litellm_model import LitellmModel

from src.agents.guardrails import budget_check, jailbreak_check, pii_check
from src.agents.simple_agents import (
    content_analyzer,
    fact_checker,
    report_writer,
    research_planner,
    source_finder,
)
from src.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Coordinator Agent (L4 — Orchestration)
# ---------------------------------------------------------------------------

coordinator = Agent(
    name="Research Coordinator",
    instructions="""You are the Research Coordinator. You orchestrate a 5-agent research pipeline.

When given a research query, execute the pipeline in order:
1. Hand off to Research Planner to decompose the query
2. Hand off to Source Finder to discover sources
3. Hand off to Content Analyzer to analyze findings
4. Hand off to Fact Checker to verify claims
5. Hand off to Report Writer to produce the final report

Pass the output of each step as input to the next step.
Always execute all 5 steps in order.""",
    model=LitellmModel(model=settings.agentic_model),
    handoffs=[research_planner, source_finder, content_analyzer, fact_checker, report_writer],
    input_guardrails=[
        InputGuardrail(guardrail_function=pii_check),
        InputGuardrail(guardrail_function=budget_check),
        InputGuardrail(guardrail_function=jailbreak_check),
    ],
)


async def run_research_pipeline(query: str, context: dict | None = None) -> dict[str, Any]:
    """Execute the full 5-agent research pipeline via the coordinator.

    For the workflow integration, we run each agent sequentially
    rather than relying on the coordinator's handoff mechanism,
    giving us more control over intermediate state.
    """
    logger.info("Starting research pipeline for: %s", query[:100])
    results: dict[str, Any] = {}

    # Step 1: Research Planner
    logger.info("Step 1/5: Research Planner")
    plan_result = await Runner.run(research_planner, input=f"Create a research plan for: {query}")
    plan_text = plan_result.final_output if hasattr(plan_result, "final_output") else str(plan_result)
    results["plan"] = plan_text
    logger.info("Plan complete")

    # Step 2: Source Finder
    logger.info("Step 2/5: Source Finder")
    source_result = await Runner.run(
        source_finder,
        input=f"Find sources for this research plan:\n{plan_text}",
    )
    source_text = source_result.final_output if hasattr(source_result, "final_output") else str(source_result)
    results["sources"] = source_text
    logger.info("Sources found")

    # Step 3: Content Analyzer
    logger.info("Step 3/5: Content Analyzer")
    analysis_result = await Runner.run(
        content_analyzer,
        input=f"Analyze these sources:\n{source_text}",
    )
    analysis_text = analysis_result.final_output if hasattr(analysis_result, "final_output") else str(analysis_result)
    results["analysis"] = analysis_text
    logger.info("Analysis complete")

    # Step 4: Fact Checker
    logger.info("Step 4/5: Fact Checker")
    verify_result = await Runner.run(
        fact_checker,
        input=f"Verify the findings in this analysis:\n{analysis_text}",
    )
    verify_text = verify_result.final_output if hasattr(verify_result, "final_output") else str(verify_result)
    results["verification"] = verify_text
    logger.info("Verification complete")

    # Step 5: Report Writer
    logger.info("Step 5/5: Report Writer")
    report_result = await Runner.run(
        report_writer,
        input=f"Write a research report based on:\nQuery: {query}\nAnalysis: {analysis_text}\nVerification: {verify_text}",
    )
    report_text = report_result.final_output if hasattr(report_result, "final_output") else str(report_result)
    results["report"] = report_text
    logger.info("Report complete")

    return results
