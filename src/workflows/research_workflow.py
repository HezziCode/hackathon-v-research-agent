"""T038: Dapr Workflow — sequential research pipeline with fan-out and approval gates."""

from __future__ import annotations

import logging
from datetime import timedelta

from dapr.ext.workflow import DaprWorkflowContext, RetryPolicy, when_any

from src.workflows.activities import (
    analyze_content,
    find_sources,
    plan_research,
    verify_facts,
    write_report,
)

logger = logging.getLogger(__name__)

# Retry policy for all activities (T062)
default_retry = RetryPolicy(
    first_retry_interval=timedelta(seconds=1),
    max_number_of_attempts=3,
    backoff_coefficient=2.0,
    max_retry_interval=timedelta(seconds=30),
)


def research_workflow(ctx: DaprWorkflowContext, input_data: dict):
    """Main research pipeline: Plan → Sources → Analyze → Verify → Report.

    Supports:
    - Human approval gates (wait_for_external_event)
    - Timeout handling (when_any with timer)
    - Fan-out source finding (when_all — future)
    - Crash recovery (each yield is a checkpoint)
    """
    task_id = input_data["task_id"]
    query = input_data["query"]
    require_approval = input_data.get("require_approval", False)
    budget_limit = input_data.get("budget_limit_usd", 1.0)

    # -----------------------------------------------------------------------
    # Stage 1: Research Planner
    # -----------------------------------------------------------------------
    plan_result = yield ctx.call_activity(
        plan_research,
        input={"task_id": task_id, "query": query},
        retry_policy=default_retry,
    )

    # -----------------------------------------------------------------------
    # Approval Gate: Plan approval (T044)
    # -----------------------------------------------------------------------
    if require_approval:
        event_task = ctx.wait_for_external_event("plan_approval")
        timeout_task = ctx.create_timer(timedelta(hours=24))
        winner = yield when_any([event_task, timeout_task])

        if winner == timeout_task:
            # T049: Timeout handling
            return {"task_id": task_id, "status": "timed_out", "reason": "Plan approval timed out after 24 hours"}

        approval = event_task.get_result()
        if not approval.get("approved", False):
            # T048: Rejection handling
            return {"task_id": task_id, "status": "rejected", "reason": approval.get("reason", "Plan rejected")}

    # -----------------------------------------------------------------------
    # Stage 2: Source Finder
    # -----------------------------------------------------------------------
    sources_result = yield ctx.call_activity(
        find_sources,
        input={
            "task_id": task_id,
            "plan": plan_result.get("plan", ""),
            "query": query,
        },
        retry_policy=default_retry,
    )

    # -----------------------------------------------------------------------
    # Stage 3: Content Analyzer
    # -----------------------------------------------------------------------
    analysis_result = yield ctx.call_activity(
        analyze_content,
        input={
            "task_id": task_id,
            "sources": sources_result.get("sources", ""),
            "query": query,
        },
        retry_policy=default_retry,
    )

    # -----------------------------------------------------------------------
    # Stage 4: Fact Checker
    # -----------------------------------------------------------------------
    verification_result = yield ctx.call_activity(
        verify_facts,
        input={
            "task_id": task_id,
            "analysis": analysis_result.get("analysis", ""),
            "query": query,
        },
        retry_policy=default_retry,
    )

    # -----------------------------------------------------------------------
    # Stage 5: Report Writer (includes PDF + artifact storage)
    # -----------------------------------------------------------------------
    report_result = yield ctx.call_activity(
        write_report,
        input={
            "task_id": task_id,
            "analysis": analysis_result.get("analysis", ""),
            "verification": verification_result.get("verification", ""),
            "query": query,
        },
        retry_policy=default_retry,
    )

    return {
        "task_id": task_id,
        "status": "completed",
        "artifacts_dir": report_result.get("artifacts_dir", ""),
    }
