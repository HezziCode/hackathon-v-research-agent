# Tasks: Research Analyst Digital FTE

**Input**: Design documents from `specs/001-research-analyst-fte/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included as the spec references pytest + pytest-asyncio and Golden Dataset evals. TDD approach follows the Agent Factory pattern.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in all descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency management, and infrastructure configuration

- [x] T001 Create project directory structure per plan.md layout (src/api/, src/agents/, src/workflows/, src/tools/, src/models/, skills/, kubernetes/, evals/, tests/)
- [x] T002 Create requirements.txt with all dependencies: fastapi, uvicorn, openai-agents[litellm]>=0.7.0, anthropic, dapr, dapr-ext-workflow, dapr-ext-fastapi, pydantic>=2.0, httpx, weasyprint, markdown, prometheus-client, pytest, pytest-asyncio in requirements.txt
- [x] T003 [P] Create src/config.py with Settings class using pydantic-settings for env vars (ANTHROPIC_API_KEY, TAVILY_API_KEY, GEMINI_API_KEY, REDIS_HOST, KAFKA_BROKER, etc.)
- [x] T004 [P] Create .env.example with all required environment variables documented in .env.example
- [x] T005 [P] Create docker-compose.yaml with Redis (port 6379), Kafka + Zookeeper (port 9092), and Dapr sidecar configuration in docker-compose.yaml
- [x] T006 [P] Create Dapr component configs: kubernetes/dapr/statestore.yaml (Redis with actorStateStore: true), kubernetes/dapr/pubsub.yaml (Kafka), kubernetes/dapr/secrets.yaml in kubernetes/dapr/
- [x] T007 [P] Create Dockerfile with Python 3.12, WeasyPrint system deps (libpango, libcairo, libgdk-pixbuf), and uvicorn entrypoint in Dockerfile
- [x] T008 Create all __init__.py files for src/api/, src/api/routes/, src/api/middleware/, src/agents/, src/workflows/, src/tools/, src/models/

**Checkpoint**: Project skeleton ready, infrastructure can be started with `docker-compose up -d`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, FastAPI app shell, and workflow runtime — MUST complete before any user story

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 [P] Create Pydantic enums (TaskStatus, PipelineStage) and base models (ArtifactRef) in src/models/task.py per data-model.md
- [x] T010 [P] Create ResearchTask model with all fields, validators (query 10-5000 chars, budget 0.01-100.0), and status transition logic in src/models/task.py
- [x] T011 [P] Create TaskRequest and TaskAccepted response models matching openapi.yaml TaskRequest/TaskAccepted schemas in src/models/task.py
- [x] T012 [P] Create ResearchPlan and SubQuestion models with validators (3-7 sub_questions, at least one P1) in src/models/research.py
- [x] T013 [P] Create SourceCollection, Source models with validators (min 5 sources, relevance 0.0-1.0) in src/models/research.py
- [x] T014 [P] Create Analysis, KeyFinding, Theme, Contradiction models in src/models/research.py
- [x] T015 [P] Create VerificationReport, VerifiedClaim, FlaggedClaim models in src/models/report.py
- [x] T016 [P] Create ResearchReport model with all output fields in src/models/report.py
- [x] T017 Create FastAPI app with lifespan (WorkflowRuntime start/shutdown), CORS, and router includes in src/api/main.py
- [x] T018 [P] Create health check endpoint returning {status: "healthy"} at GET /health in src/api/routes/tasks.py
- [x] T019 Create in-memory task store (dict-based) for task state management with get/set/list operations in src/api/main.py
- [x] T020 Create tests/conftest.py with FastAPI TestClient fixture, mock Dapr client, and shared test utilities in tests/conftest.py

**Checkpoint**: Foundation ready — FastAPI runs, models validate, workflow runtime initializes

---

## Phase 3: User Story 1 — Submit Research Query (Priority: P1) MVP

**Goal**: User submits a research query via POST /tasks, the 5-agent pipeline executes autonomously, and produces a Markdown report + JSON metadata

**Independent Test**: `curl -X POST http://localhost:8000/tasks -d '{"query":"AI agents market 2026"}' && curl http://localhost:8000/tasks/{id}/status` → returns completed with artifacts

### Tests for User Story 1

- [x] T021 [P] [US1] Unit tests for all Pydantic models (TaskRequest validation, status transitions, ResearchPlan constraints) in tests/unit/test_models.py
- [x] T022 [P] [US1] Unit tests for workflow activities (mock LLM responses, verify activity inputs/outputs) in tests/unit/test_activities.py
- [x] T023 [P] [US1] Integration test: POST /tasks returns 202 with task_id, GET /tasks/{id}/status returns valid status in tests/integration/test_api.py

### Implementation for User Story 1

- [x] T024 [US1] Implement POST /tasks endpoint: validate TaskRequest, create ResearchTask, start Dapr workflow, return TaskAccepted in src/api/routes/tasks.py
- [x] T025 [US1] Implement GET /tasks/{id}/status endpoint returning TaskStatusResponse per openapi.yaml in src/api/routes/tasks.py
- [x] T026 [US1] Implement GET /tasks/{id}/artifacts endpoint listing available artifacts in src/api/routes/tasks.py
- [x] T027 [US1] Implement GET /tasks/{id}/artifacts/{name} endpoint for file download in src/api/routes/tasks.py
- [x] T028 [US1] Implement web search tool using Tavily API (httpx client, search query, return structured results) in src/tools/web_search.py
- [x] T029 [US1] Implement ClaudeAgentWrapper with agentic loop (tool_use stop_reason, tool dispatch, max_turns) per research.md R-2 pattern in src/agents/claude_agent_wrapper.py
- [x] T030 [US1] Implement Research Planner agent: reads skills/research-planner/SKILL.md instructions, outputs ResearchPlan with sub-questions in src/agents/simple_agents.py
- [x] T031 [US1] Implement Source Finder agent: uses ClaudeAgentWrapper + web_search tool, outputs SourceCollection with coverage matrix in src/agents/simple_agents.py
- [x] T032 [US1] Implement Content Analyzer agent: uses ClaudeAgentWrapper, cross-references sources, outputs Analysis with confidence scores in src/agents/simple_agents.py
- [x] T033 [US1] Implement Fact Checker agent: uses LitellmModel(model="gemini/gemini-2.0-flash") for large context, outputs VerificationReport in src/agents/simple_agents.py
- [x] T034 [US1] Implement Report Writer agent: generates Markdown report, sources.json, confidence-scores.json per skills/report-writer/SKILL.md format in src/agents/simple_agents.py
- [x] T035 [US1] Implement OpenAI Agents SDK coordinator with handoffs to all 5 agents, LiteLLM model routing per DD-2 in src/agents/coordinator.py
- [x] T036 [US1] Implement guardrails: PII detection InputGuardrail, budget tracking InputGuardrail, jailbreak detection InputGuardrail in src/agents/guardrails.py
- [x] T037 [US1] Implement workflow activities: plan_research, find_sources, analyze_content, verify_facts, write_report — each calls the corresponding agent in src/workflows/activities.py
- [x] T038 [US1] Implement research_workflow: sequential pipeline (Plan → Sources → Analyze → Verify → Report) with fan-out in Source Finder via when_all in src/workflows/research_workflow.py
- [x] T039 [US1] Implement Kafka event publishing: publish status updates to fte.status.updates topic via Dapr pub/sub in src/workflows/activities.py
- [x] T040 [US1] Wire workflow completion to task store: update task status and artifact references when workflow completes in src/api/main.py
- [x] T041 [US1] Create Kafka topic definitions for fte.status.updates and fte.audit.actions in kubernetes/kafka/topics.yaml

**Checkpoint**: Core pipeline works end-to-end — submit query, get Markdown report + sources.json + confidence-scores.json

---

## Phase 4: User Story 2 — Human Approval Gates (Priority: P1)

**Goal**: Tasks with `require_approval: true` pause at workflow stages for human review via POST /workflows/{id}/approve

**Independent Test**: Submit task with `require_approval: true`, verify status shows "awaiting_approval", approve via API, verify pipeline resumes

### Tests for User Story 2

- [x] T042 [P] [US2] Unit test for approval gate logic: workflow pauses on wait_for_external_event, resumes on raise_event in tests/unit/test_activities.py
- [x] T043 [P] [US2] Integration test: submit with require_approval=true, check awaiting_approval status, POST approve, check resumed in tests/integration/test_workflow.py

### Implementation for User Story 2

- [x] T044 [US2] Add approval gates to research_workflow: wait_for_external_event("plan_approval") after Planner stage with timeout via when_any in src/workflows/research_workflow.py
- [x] T045 [US2] Implement POST /workflows/{id}/approve endpoint: raise_workflow_event with approval data, handle approved=true/false in src/api/routes/workflows.py
- [x] T046 [US2] Implement GET /workflows/{id}/status endpoint returning workflow stage details, approval_pending data in src/api/routes/workflows.py
- [x] T047 [US2] Update task status to "awaiting_approval" when workflow pauses, include pending plan data in status response in src/workflows/activities.py
- [x] T048 [US2] Handle rejection: terminate workflow with "rejected" status and record rejection reason in src/workflows/research_workflow.py
- [x] T049 [US2] Handle timeout: auto-reject after configurable timeout (default 24h), update status to "timed_out" in src/workflows/research_workflow.py

**Checkpoint**: Approval flow works — tasks pause, managers approve/reject, pipeline resumes or terminates

---

## Phase 5: User Story 3 — PDF Report Export (Priority: P2)

**Goal**: Research reports automatically export to PDF alongside Markdown, available as a downloadable artifact

**Independent Test**: Complete a research task, verify research-report.pdf in artifacts list, download and verify formatting

### Tests for User Story 3

- [x] T050 [P] [US3] Unit test for PDF export: markdown input → PDF output with correct formatting in tests/unit/test_activities.py

### Implementation for User Story 3

- [x] T051 [US3] Implement markdown_to_pdf function: markdown → HTML (via markdown lib) → PDF (via WeasyPrint) with report CSS styling in src/tools/pdf_export.py
- [x] T052 [US3] Add PDF export step to Report Writer agent: call pdf_export after markdown generation, output pdf_path in src/agents/simple_agents.py
- [x] T053 [US3] Add research-report.pdf to artifact list in workflow completion handler in src/workflows/activities.py

**Checkpoint**: PDF reports generated automatically alongside Markdown, downloadable via artifacts API

---

## Phase 6: User Story 4 — A2A Discovery and Inter-FTE Collaboration (Priority: P2)

**Goal**: Other FTEs discover this agent via Agent Card at /.well-known/agent.json and submit tasks via JSON-RPC 2.0 at /a2a

**Independent Test**: `curl http://localhost:8000/.well-known/agent.json` returns valid Agent Card; POST /a2a with tasks/send method processes research task

### Tests for User Story 4

- [x] T054 [P] [US4] Contract test: GET /.well-known/agent.json returns valid AgentCard with required fields in tests/contract/test_a2a.py
- [x] T055 [P] [US4] Contract test: POST /a2a with tasks/send returns valid JSON-RPC response, tasks/get returns status in tests/contract/test_a2a.py

### Implementation for User Story 4

- [x] T056 [P] [US4] Create A2A Pydantic models: AgentCard, Skill, AgentCapabilities, JsonRpcRequest, JsonRpcResponse, TaskSendParams, Message, TextPart, FilePart, DataPart, Artifact per research.md R-4 in src/models/task.py
- [x] T057 [US4] Implement GET /.well-known/agent.json endpoint returning static AgentCard with research skill in src/api/routes/a2a.py
- [x] T058 [US4] Implement POST /a2a endpoint: parse JSON-RPC 2.0 request, dispatch tasks/send to create ResearchTask, tasks/get to return status in src/api/routes/a2a.py
- [x] T059 [US4] Implement tasks/cancel handler: terminate running workflow via DaprClient in src/api/routes/a2a.py
- [x] T060 [US4] Map A2A Message parts to internal TaskRequest format and internal results back to A2A Artifact format in src/api/routes/a2a.py

**Checkpoint**: A2A protocol works — other agents discover capabilities and submit/query research tasks

---

## Phase 7: User Story 5 — Crash Recovery and Durable Execution (Priority: P2)

**Goal**: Workflow survives process crashes and resumes from last checkpoint without re-executing completed stages

**Independent Test**: Start research task, kill worker process mid-pipeline, restart, verify workflow resumes from last completed activity

### Tests for User Story 5

- [x] T061 [P] [US5] Integration test: start workflow, verify checkpoint exists in Redis state store, simulate restart, verify no duplicate activity execution in tests/integration/test_workflow.py

### Implementation for User Story 5

- [x] T062 [US5] Add RetryPolicy to all workflow activities: first_retry_interval=1s, max_attempts=3, backoff_coefficient=2, max_interval=30s in src/workflows/research_workflow.py
- [x] T063 [US5] Ensure all activity functions are idempotent: check for existing results before re-executing in src/workflows/activities.py
- [x] T064 [US5] Add workflow state recovery on FastAPI startup: query Dapr for running workflow instances and re-register status callbacks in src/api/main.py
- [x] T065 [US5] Verify statestore.yaml has actorStateStore: "true" and transactional support; document crash recovery behavior in kubernetes/dapr/statestore.yaml

**Checkpoint**: Crash recovery verified — workflow resumes from last checkpoint after restart

---

## Phase 8: User Story 6 — Observability Dashboard (Priority: P3)

**Goal**: Prometheus metrics and OpenTelemetry traces expose agent-level performance data for monitoring

**Independent Test**: Submit research task, scrape GET /metrics, verify task_count/latency/error_rate metrics present; verify traces show 5-agent timing

### Tests for User Story 6

- [x] T066 [P] [US6] Integration test: submit task, GET /metrics, verify prometheus_client counters and histograms present in tests/integration/test_api.py

### Implementation for User Story 6

- [x] T067 [P] [US6] Create Prometheus metrics: task_submissions_total counter, task_duration_seconds histogram, agent_step_duration_seconds histogram (per agent), active_tasks gauge in src/api/main.py
- [x] T068 [P] [US6] Implement custom TracingProcessor for OpenAI Agents SDK: forward spans to OpenTelemetry collector in src/agents/coordinator.py
- [x] T069 [US6] Implement GET /metrics endpoint exposing Prometheus metrics in text exposition format in src/api/routes/tasks.py
- [x] T070 [US6] Instrument workflow activities with timing: record agent_step_duration_seconds for each of the 5 pipeline stages in src/workflows/activities.py
- [x] T071 [US6] Add LLM cost tracking: accumulate token usage per task from LiteLLM responses, expose as metric in src/agents/coordinator.py

**Checkpoint**: Metrics and traces available — Prometheus can scrape /metrics, traces show full pipeline timing

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, security hardening, deployment configs

- [x] T072 [P] Implement OAuth2 authentication middleware (Bearer token validation) in src/api/middleware/auth.py
- [x] T073 [P] Create Agent Sandbox CRD and pre-warmed pool configs in kubernetes/sandbox/sandbox.yaml and kubernetes/sandbox/sandbox-pool.yaml
- [x] T074 [P] Create Kubernetes Deployment + Service manifest with Dapr annotations, resource limits, health probes in kubernetes/deployment.yaml
- [x] T075 [P] Create Golden Dataset with 50+ research scenarios covering edge cases in evals/golden_dataset.yaml
- [x] T076 [P] Create eval runner that executes Golden Dataset against live system and reports pass/fail rate in evals/run_evals.py
- [x] T077 Validate quickstart.md end-to-end: follow all steps on fresh environment, verify task submission through report delivery
- [x] T078 Run all tests (unit, integration, contract) and fix any failures

**Checkpoint**: Production-ready — all tests pass, evals at 95%+, deployment configs complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — core MVP, implement first
- **US2 (Phase 4)**: Depends on Phase 2 + T038 (workflow exists) — adds approval to existing workflow
- **US3 (Phase 5)**: Depends on Phase 2 + T034 (Report Writer exists) — adds PDF to existing report step
- **US4 (Phase 6)**: Depends on Phase 2 + T024 (task submission exists) — wraps existing API in A2A protocol
- **US5 (Phase 7)**: Depends on Phase 2 + T038 (workflow exists) — adds retry/recovery to existing workflow
- **US6 (Phase 8)**: Depends on Phase 2 + T035 (coordinator exists) — adds instrumentation to existing agents
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only — no dependency on other stories. THIS IS THE MVP.
- **US2 (P1)**: Requires US1's workflow (T038) to exist. Can add approval gates incrementally.
- **US3 (P2)**: Requires US1's Report Writer (T034). Can add PDF export incrementally.
- **US4 (P2)**: Requires US1's task submission (T024). Wraps existing API with A2A layer.
- **US5 (P2)**: Requires US1's workflow (T038). Adds retry policies and recovery logic.
- **US6 (P3)**: Requires US1's coordinator (T035). Adds metrics/tracing instrumentation.

### Within Each User Story

- Tests written first (FAIL before implementation)
- Models before agents
- Agents before workflow activities
- Workflow before API endpoints
- Core before integration

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006, T007 all parallelizable (different files)
**Phase 2**: T009-T016 all parallelizable (different model files); T017 sequential (depends on models)
**Phase 3**: T021-T023 tests parallel; T028-T034 agents parallel (different files); T035-T038 sequential (coordinator → guardrails → activities → workflow)
**Phase 4-8**: Tests within each phase are parallel; after US1 completes, US3/US4/US5/US6 can all proceed in parallel

---

## Parallel Example: User Story 1

```
Phase 2 complete
        │
        ▼
┌───────────────────────────────┐
│  T021, T022, T023 (tests)     │  ← All parallel (different test files)
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────┐
│  T024-T027 (API endpoints)  │  T028 (web search) │  ← Parallel groups
│  T029 (claude wrapper)      │  T030 (planner)    │
│  T031 (source finder)       │  T032 (analyzer)   │
│  T033 (fact checker)        │  T034 (report)     │
└───────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│  T035 (coordinator)           │  ← Sequential: depends on all agents
│  T036 (guardrails)            │
│  T037 (activities)            │  ← Sequential: depends on coordinator
│  T038 (workflow)              │  ← Sequential: depends on activities
└───────────────────────────────┘
        │
        ▼
┌───────────────────────────────┐
│  T039 (Kafka events)          │  ← Sequential: depends on workflow
│  T040 (wire completion)       │
│  T041 (Kafka topics)          │
└───────────────────────────────┘
        │
        ▼
  US1 COMPLETE ✓ (MVP)
```

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**Phases 1 + 2 + 3 (User Story 1)** = Tasks T001-T041 (41 tasks)

This delivers the core value: submit a research query and receive a complete report with sources and confidence scores. Everything else is incremental.

### Incremental Delivery Order

1. **MVP**: US1 (submit query → get report) — 41 tasks
2. **Trust Layer**: US2 (human approval gates) — 8 tasks
3. **Polish Output**: US3 (PDF export) — 4 tasks
4. **Interop**: US4 (A2A protocol) — 7 tasks
5. **Resilience**: US5 (crash recovery) — 5 tasks
6. **Operations**: US6 (observability) — 6 tasks
7. **Production**: Polish phase — 7 tasks

### Task Summary

| Phase | User Story | Priority | Tasks | Cumulative |
|-------|-----------|----------|-------|------------|
| 1 | Setup | — | 8 | 8 |
| 2 | Foundational | — | 12 | 20 |
| 3 | US1: Submit Research Query | P1 | 21 | 41 |
| 4 | US2: Human Approval Gates | P1 | 8 | 49 |
| 5 | US3: PDF Report Export | P2 | 4 | 53 |
| 6 | US4: A2A Discovery | P2 | 7 | 60 |
| 7 | US5: Crash Recovery | P2 | 5 | 65 |
| 8 | US6: Observability | P3 | 6 | 71 |
| 9 | Polish | — | 7 | 78 |
| **Total** | | | **78** | |
