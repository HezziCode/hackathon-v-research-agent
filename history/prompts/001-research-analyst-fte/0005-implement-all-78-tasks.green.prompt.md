---
id: 0005
title: Implement All 78 Tasks for Research Analyst FTE
stage: green
date: 2026-02-20
surface: agent
model: claude-sonnet-4-6
feature: 001-research-analyst-fte
branch: 001-research-analyst-fte
user: huzaifasys
command: /sp.implement
labels: ["implementation", "research-analyst-fte", "full-build", "78-tasks", "9-phases"]
links:
  spec: specs/001-research-analyst-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .gitignore
  - .dockerignore
  - requirements.txt
  - .env.example
  - Dockerfile
  - docker-compose.yaml
  - pyproject.toml
  - uv.lock
  - src/__init__.py
  - src/config.py
  - src/models/__init__.py
  - src/models/task.py
  - src/models/research.py
  - src/models/report.py
  - src/api/__init__.py
  - src/api/main.py
  - src/api/routes/__init__.py
  - src/api/routes/tasks.py
  - src/api/routes/workflows.py
  - src/api/routes/a2a.py
  - src/api/middleware/__init__.py
  - src/api/middleware/auth.py
  - src/agents/__init__.py
  - src/agents/coordinator.py
  - src/agents/claude_agent_wrapper.py
  - src/agents/simple_agents.py
  - src/agents/guardrails.py
  - src/workflows/__init__.py
  - src/workflows/research_workflow.py
  - src/workflows/activities.py
  - src/tools/__init__.py
  - src/tools/web_search.py
  - src/tools/pdf_export.py
  - skills/research-planner/SKILL.md
  - skills/source-finder/SKILL.md
  - skills/content-analyzer/SKILL.md
  - skills/fact-checker/SKILL.md
  - skills/report-writer/SKILL.md
  - kubernetes/dapr/statestore.yaml
  - kubernetes/dapr/pubsub.yaml
  - kubernetes/dapr/secrets.yaml
  - kubernetes/kafka/topics.yaml
  - kubernetes/sandbox/sandbox.yaml
  - kubernetes/sandbox/sandbox-pool.yaml
  - kubernetes/deployment.yaml
  - evals/golden_dataset.yaml
  - evals/run_evals.py
  - tests/conftest.py
  - tests/__init__.py
  - tests/unit/__init__.py
  - tests/unit/test_models.py
  - tests/unit/test_guardrails.py
  - tests/unit/test_activities.py
  - tests/integration/__init__.py
  - tests/integration/test_api.py
  - tests/integration/test_workflow.py
  - tests/contract/__init__.py
  - tests/contract/test_a2a.py
  - specs/001-research-analyst-fte/tasks.md
tests:
  - tests/unit/test_models.py (15 passed)
  - tests/unit/test_guardrails.py (5 passed)
  - tests/unit/test_activities.py (2 passed)
  - tests/integration/test_api.py (7 passed)
  - tests/integration/test_workflow.py (2 passed)
  - tests/contract/test_a2a.py (8 passed)
---

## Prompt

/sp.implement

## Response snapshot

Executed all 78 tasks across 9 phases of the Research Analyst Digital FTE implementation:

**Phase 1 — Setup & Skeleton (T001-T008):** Created project structure, .gitignore, .dockerignore, requirements.txt, src/config.py (pydantic-settings with LLM routing), .env.example, docker-compose.yaml (Redis+Kafka+Zookeeper), Dockerfile (Python 3.12 + WeasyPrint), Dapr component configs (statestore, pubsub, secrets), all __init__.py files.

**Phase 2 — Foundational Models & API (T009-T020):** Built Pydantic models: task.py (TaskStatus with 12 states, PipelineStage, TaskRequest with validators), research.py (ResearchPlan with 3-7 sub_questions validator, SourceCollection with min 5 sources), report.py (VerificationReport, ResearchReport). Created FastAPI app with lifespan, task/workflow/a2a routes, test fixtures.

**Phase 3 — US1 MVP Pipeline (T021-T041):** Implemented web_search.py (Tavily), pdf_export.py (WeasyPrint), ClaudeAgentWrapper (agentic tool_use loop), 5 simple agents (OpenAI Agents SDK + LitellmModel), guardrails (PII/budget/jailbreak), coordinator with handoffs, Dapr workflow with approval gates + timeout, activities with Kafka event publishing, 5 SKILL.md files.

**Phase 4 — Approval Gates (T042-T047):** Approval workflow with wait_for_external_event + when_any timeout pattern, workflow approval API endpoints.

**Phase 5 — Report & Export (T048-T053):** PDF export with markdown→HTML→WeasyPrint pipeline, artifact storage (markdown, sources.json, confidence-scores.json, PDF).

**Phase 6 — Security & Auth (T054-T059):** OAuth2 Bearer middleware with dev mode bypass, gVisor sandbox CRD + network policies.

**Phase 7 — Contract Tests (T060-T063):** A2A contract tests (8 tests), workflow integration tests.

**Phase 8 — Observability (T064-T070):** Prometheus metrics (TASK_SUBMISSIONS, TASK_DURATION, AGENT_STEP_DURATION, ACTIVE_TASKS, LLM_COST_TOTAL).

**Phase 9 — Evals & Deploy (T071-T078):** Golden dataset (50+ scenarios), eval runner, Kubernetes deployment manifest.

**Package Management:** Used `uv` (not pip). Ran `uv init --no-readme`, then `uv add` for all dependencies.

**Test Results:** 39/39 passed (22 unit + 15 integration/contract + 2 workflow) in 21.49s.

## Outcome

- ✅ Impact: Complete implementation of Research Analyst Digital FTE — all 78 tasks across 9 phases done, full 8-layer architecture realized
- 🧪 Tests: 39/39 passed (15 model, 5 guardrail, 2 activity, 7 API, 2 workflow, 8 A2A contract)
- 📁 Files: 55+ files created across src/, tests/, skills/, kubernetes/, evals/
- 🔁 Next prompts: Run integration tests with Dapr sidecar, deploy to K8s, run golden dataset evals, add Tavily API key and test live search
- 🧠 Reflection: Implementation went smoothly. Key decisions: (1) used uv instead of pip per user preference, (2) implemented many Phase 4-5 features during Phase 3 since they were tightly coupled with the workflow, (3) all tests pass without needing live infrastructure (Dapr, Kafka) by testing HTTP layer independently.

## Evaluation notes (flywheel)

- Failure modes observed: pip install rejected (user prefers uv), missing openai-agents package caused 5 test failures until installed, Read tool fails with empty pages parameter
- Graders run and results (PASS/FAIL): pytest 39/39 PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Test with live Dapr sidecar to validate workflow checkpointing and approval gates end-to-end
