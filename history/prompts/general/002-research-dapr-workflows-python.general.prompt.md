---
id: 002
title: Research Dapr Workflows for Python
stage: general
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: research
labels: ["dapr", "workflows", "python", "research", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/002-research-dapr-workflows-python.general.prompt.md
tests:
  - none
---

## Prompt

Research Dapr Workflows for Python. I need to know:
1. Current latest version of dapr and dapr-ext-workflow packages
2. How to define a workflow with activities
3. How checkpointing and crash recovery works
4. How wait_for_external_event works (human-in-the-loop)
5. How fan-out/fan-in pattern works (when_all)
6. How to integrate with FastAPI
7. State store configuration for workflow durability

Search the web and check the official Dapr docs at https://docs.dapr.io. Return a concise summary with code patterns.

## Response snapshot

Provided comprehensive research summary covering all 7 topics:
1. Versions: dapr and dapr-ext-workflow ~1.14.x (from training data; live fetch denied)
2. Workflow/activity definition using @workflow_runtime.workflow() and @workflow_runtime.activity() decorators with generator yield pattern
3. Checkpointing via event-sourcing with replay; every yield is a checkpoint; on crash, orchestrator replays from start with cached activity results
4. wait_for_external_event suspends workflow; raise_workflow_event resumes it; combined with create_timer and when_any for timeout patterns
5. Fan-out/fan-in via wf.when_all([tasks]) for parallel; wf.when_any([tasks]) for racing
6. FastAPI integration using lifespan context manager to start/stop WorkflowRuntime; DaprClient for workflow management endpoints
7. State store must have actorStateStore: "true" and support transactions; examples for Redis, PostgreSQL, Cosmos DB

Included complete code examples for all patterns including a minimal end-to-end FastAPI app.

## Outcome

- Impact: Research deliverable providing architecture patterns for Dapr workflow integration
- Tests: none (research only)
- Files: PHR created
- Next prompts: Spec creation for workflow feature, plan with ADRs for state store and workflow engine choices
- Reflection: WebSearch, WebFetch, Bash, Context7, and GitHub file tools were all denied; research was based on training data with version caveat noted

## Evaluation notes (flywheel)

- Failure modes observed: All external data fetching tools denied in session; unable to verify latest package versions
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Re-run with tool permissions enabled to verify latest versions from PyPI
