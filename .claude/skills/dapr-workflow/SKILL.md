---
name: dapr-workflow
description: |
  Use when implementing durable, crash-proof workflow execution for Digital FTEs using Dapr Workflows.
  Use when tasks need checkpointing, human-in-the-loop gates, fan-out/fan-in, timers, or compensation.
  NOT when building simple request-response APIs (use fastapi-service instead).
---

# Dapr Workflow — Durable Execution Engine

## Overview

Dapr Workflows provides the durable execution layer (L2) for Digital FTEs. It runs inside the Dapr sidecar and uses Dapr Actors for state management. Workflows survive crashes by replaying from the last checkpointed state. Zero additional infrastructure cost.

## How Durability Works

1. Workflow starts → Actor created with unique ID
2. Before each activity → Reminder set (durable timer)
3. Activity executes → Result checkpointed to state store
4. If crash → Reminder triggers actor reactivation
5. Actor resumes → Replays from last checkpoint
6. Workflow continues from exact point of failure

## Workflow Patterns

| Pattern | Use Case | Implementation |
|---------|----------|---------------|
| Task Chaining | Sequential steps | `await ctx.call_activity()` in sequence |
| Fan-Out/Fan-In | Parallel analysis | `ctx.when_all([activities...])` |
| Human-in-Loop | Approval gates | `ctx.wait_for_external_event()` |
| Compensation | Rollback on failure | `try/except` with cleanup activities |
| Timers | Scheduled check-ins | `ctx.create_timer(duration)` |
| Sub-Workflows | Delegate to specialists | `ctx.call_child_workflow()` |

## Core Pattern: Digital FTE Workflow

```python
import dapr.ext.workflow as wf
from datetime import timedelta

class DigitalFTEWorkflow(wf.Workflow):
    def __init__(self):
        super().__init__()

    def run(self, ctx: wf.WorkflowContext, input: dict):
        task = input["task"]

        # Step 1: Plan (checkpointed)
        plan = yield ctx.call_activity(plan_research, input=task)

        # Step 2: Human approval gate
        if input.get("require_approval"):
            yield ctx.call_activity(notify_for_approval, input=plan)
            approval = yield ctx.wait_for_external_event("human_approval")
            if not approval.get("approved"):
                return {"status": "rejected", "reason": approval.get("comments")}

        # Step 3: Fan-out parallel research
        source_tasks = [
            ctx.call_activity(find_sources, input=q)
            for q in plan["sub_questions"]
        ]
        sources = yield ctx.when_all(source_tasks)

        # Step 4: Analyze (checkpointed)
        analysis = yield ctx.call_activity(analyze_content, input=sources)

        # Step 5: Fact-check
        verified = yield ctx.call_activity(fact_check, input=analysis)

        # Step 6: Generate report
        report = yield ctx.call_activity(write_report, input=verified)

        return {"status": "completed", "report": report}
```

## Activity Definition

```python
@wf.activity
def plan_research(ctx, task: str) -> dict:
    """Break research query into sub-questions."""
    # Call coordinator agent
    result = coordinator.run(task)
    return result

@wf.activity
def notify_for_approval(ctx, plan: dict):
    """Send approval request via Slack/email."""
    # Publish to Kafka topic for notification
    pass
```

## Dapr Component Configuration

```yaml
# dapr/components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
```

## Key Rules

1. Every long-running FTE task MUST use Dapr Workflows
2. State store (Redis/PostgreSQL) MUST be configured for checkpointing
3. Human-in-the-loop gates use `wait_for_external_event`
4. Fan-out/fan-in for parallel sub-tasks (e.g., researching multiple sources)
5. Never fire-and-forget in production — always durable
6. Workflow IDs = task IDs for traceability

## Dependencies

```
dapr>=1.14.0
dapr-ext-workflow>=0.5.0
```
