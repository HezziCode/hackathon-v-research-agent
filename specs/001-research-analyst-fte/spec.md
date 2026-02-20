# Feature Specification: Research Analyst Digital FTE

**Feature Branch**: `001-research-analyst-fte`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "Research Analyst Digital FTE — A Custom Agent that performs autonomous multi-step web research on any topic with 5 sub-agents, hybrid orchestration, and full 8-layer architecture."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit Research Query (Priority: P1)

A user submits a research query (e.g., "What is the AI agents market size in 2026?") via the FastAPI `/tasks` endpoint. The system accepts the task, returns a task ID, and begins autonomous multi-step research through the 5-agent pipeline.

**Why this priority**: This is the core value proposition — without task submission and the research pipeline, the Digital FTE cannot function. Everything else builds on this.

**Independent Test**: Can be fully tested by sending a POST to `/tasks` with a research query, then polling `/tasks/{id}/status` until completion. Delivers a structured research report as output.

**Acceptance Scenarios**:

1. **Given** the Digital FTE is running, **When** a user submits a research query via `POST /tasks`, **Then** the system returns a task ID with status "accepted" within 2 seconds
2. **Given** a task is accepted, **When** the research pipeline executes, **Then** the 5 agents execute in order: Planner → Source Finder → Content Analyzer → Fact Checker → Report Writer
3. **Given** the pipeline completes, **When** the user queries `GET /tasks/{id}/status`, **Then** status is "completed" and artifacts are available at `/tasks/{id}/artifacts`
4. **Given** the pipeline completes, **When** artifacts are retrieved, **Then** output includes `research-report.md`, `sources.json`, and `confidence-scores.json`

---

### User Story 2 - Human Approval Gates (Priority: P1)

A user submits a research query with `require_approval: true`. The system pauses at key decision points (research direction, source selection, final report) and waits for human approval before proceeding.

**Why this priority**: Human-in-the-loop is a core Agent Factory requirement (Principle VII). Without it, the Digital FTE cannot be trusted for production use.

**Independent Test**: Submit a task with approval required, verify system pauses and sends notification, then approve via `/workflows/{id}/approve` and confirm pipeline resumes.

**Acceptance Scenarios**:

1. **Given** a task is submitted with `require_approval: true`, **When** the Research Planner completes, **Then** the workflow pauses and status shows "awaiting_approval" with the research plan
2. **Given** the workflow is paused for approval, **When** a manager sends `POST /workflows/{id}/approve` with `approved: true`, **Then** the workflow resumes from the next stage
3. **Given** the workflow is paused for approval, **When** a manager sends approval with `approved: false`, **Then** the workflow terminates with status "rejected" and the rejection reason is recorded

---

### User Story 3 - PDF Report Export (Priority: P2)

After the research pipeline completes, the system generates a PDF version of the Markdown research report with proper formatting, citations, and metadata.

**Why this priority**: PDF is the standard deliverable format for business stakeholders. Important but the Markdown report alone (from P1) provides value.

**Independent Test**: Complete a research task, then verify `research-report.pdf` exists in artifacts with correct formatting and all citations preserved.

**Acceptance Scenarios**:

1. **Given** a research report is generated in Markdown, **When** the Report Writer completes, **Then** a PDF version is generated alongside the Markdown
2. **Given** a PDF is generated, **When** the PDF is opened, **Then** all citations, headings, data points, and confidence scores from the Markdown are correctly rendered

---

### User Story 4 - A2A Discovery and Inter-FTE Collaboration (Priority: P2)

Other Digital FTEs can discover the Research Analyst FTE via the A2A Agent Card at `/.well-known/agent.json` and send research tasks via the `/a2a` endpoint using the A2A protocol.

**Why this priority**: A2A enables the "Agentic Web" vision. Important for the full Agent Factory demonstration but the FTE delivers value standalone (via direct task submission).

**Independent Test**: Query `GET /.well-known/agent.json` and verify the Agent Card is returned with correct capabilities. Send a task via `POST /a2a` and verify it is processed.

**Acceptance Scenarios**:

1. **Given** the Digital FTE is running, **When** another agent queries `GET /.well-known/agent.json`, **Then** a valid Agent Card is returned with skills, capabilities, and supported modes
2. **Given** another FTE sends a task via `POST /a2a` with method `tasks/send`, **Then** the task is accepted and processed through the same pipeline as direct submissions
3. **Given** a task was sent via A2A, **When** the requesting FTE queries status via `tasks/status`, **Then** the current status and any available artifacts are returned

---

### User Story 5 - Crash Recovery and Durable Execution (Priority: P2)

The research pipeline survives crashes and infrastructure failures. If the system restarts during execution, Dapr Workflows resumes from the last checkpoint without data loss or duplicate work.

**Why this priority**: Durability is Principle VIII — essential for a 168 hr/week Digital FTE but can be verified after the core pipeline works.

**Independent Test**: Start a research task, simulate a crash mid-execution (restart the worker), verify the workflow resumes from the last completed activity.

**Acceptance Scenarios**:

1. **Given** a workflow is executing at step 3 (Content Analysis), **When** the worker process crashes, **Then** upon restart the workflow resumes from step 3 (not step 1)
2. **Given** a workflow has checkpointed results from steps 1-2, **When** the system restarts, **Then** steps 1-2 results are available from the state store and not re-executed

---

### User Story 6 - Observability Dashboard (Priority: P3)

Operations team can monitor the Digital FTE's performance via Prometheus metrics, OpenTelemetry traces, and LLM cost tracking.

**Why this priority**: Essential for production but not needed for the core research capability demonstration.

**Independent Test**: Submit a research task, then verify metrics are exposed at `/metrics` endpoint and traces are captured in the tracing system.

**Acceptance Scenarios**:

1. **Given** a research task is executing, **When** Prometheus scrapes `/metrics`, **Then** task count, latency, error rate, and agent-level metrics are available
2. **Given** a research task completes, **When** traces are queried, **Then** a full distributed trace shows timing for each of the 5 agent steps

---

### Edge Cases

- What happens when web search returns zero results for a sub-question? The Source Finder flags the gap in the coverage matrix and the Content Analyzer reports it as a data gap with low confidence score.
- What happens when the LLM API is rate-limited or unavailable? The workflow retries with exponential backoff (via Dapr) up to 3 times, then fails the activity and the workflow status shows the specific failure reason.
- What happens when the research query is ambiguous or too broad? The Research Planner decomposes it into sub-questions with explicit scope boundaries and flags ambiguity in the plan for human review.
- What happens when budget limits are exceeded mid-research? The BudgetGuardrail (OpenAI Agents SDK) halts execution, saves partial results, and returns status "budget_exceeded" with results collected so far.
- What happens when two sources contradict each other? The Content Analyzer surfaces the contradiction explicitly and the Fact Checker flags it as "needs_review" with both positions documented.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept research queries via `POST /tasks` and return a task ID with status "accepted"
- **FR-002**: System MUST orchestrate 5 sub-agents in sequence: Research Planner → Source Finder → Content Analyzer → Fact Checker → Report Writer
- **FR-003**: Research Planner MUST decompose queries into 3-7 sub-questions with priorities (P1/P2/P3) and source type recommendations
- **FR-004**: Source Finder MUST discover sources via web search MCP and return a curated collection with relevance scores and a coverage matrix
- **FR-005**: Content Analyzer MUST extract key findings, cross-reference across sources, identify contradictions, and produce confidence scores (0.0-1.0)
- **FR-006**: Fact Checker MUST verify claims using cross-source triangulation and flag single-source claims as "needs_review"
- **FR-007**: Report Writer MUST generate a structured Markdown report with executive summary, key findings with citations, data gaps section, and methodology
- **FR-008**: Report Writer MUST generate `sources.json` and `confidence-scores.json` metadata alongside the report
- **FR-009**: Report Writer MUST export the report to PDF format preserving all formatting and citations
- **FR-010**: System MUST support human-in-the-loop approval gates at configurable workflow stages via Dapr Workflow external events
- **FR-011**: Coordinator (OpenAI Agents SDK) MUST apply guardrails: PII detection/masking, budget limits, and jailbreak detection
- **FR-012**: System MUST expose an A2A Agent Card at `GET /.well-known/agent.json` with capabilities and supported skills
- **FR-013**: System MUST accept tasks from other FTEs via `POST /a2a` using JSON-RPC 2.0 protocol
- **FR-014**: All workflow execution MUST be durable via Dapr Workflows with automatic checkpointing to survive crashes
- **FR-015**: System MUST publish status events to Kafka topics: `fte.status.updates` for progress and `fte.audit.actions` for immutable audit trail
- **FR-016**: System MUST expose Prometheus metrics and OpenTelemetry traces for monitoring
- **FR-017**: System MUST provide task status via `GET /tasks/{id}/status` and artifacts via `GET /tasks/{id}/artifacts`
- **FR-018**: System MUST route to optimal LLM per task via LiteLLM: Claude for agentic execution, Gemini for large-context fact-checking, cheapest model for simple sub-tasks

### Key Entities

- **Research Task**: Represents a user-submitted research query with ID, status, configuration (approval required, budget), and lifecycle timestamps
- **Research Plan**: Output of the Research Planner — sub-questions, priorities, scope boundaries, and source strategy
- **Source Collection**: Curated list of sources with URLs, metadata, relevance scores, credibility ratings, and coverage matrix
- **Analysis**: Cross-referenced findings with key data points, themes, contradictions, confidence scores, and data gaps
- **Verification Report**: Fact-checking results — verified claims, flagged claims, unverifiable items, and overall reliability score
- **Research Report**: Final output package — Markdown report, PDF export, sources.json, and confidence-scores.json

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can submit a research query and receive a complete research report within 15 minutes for standard topics
- **SC-002**: Research reports contain a minimum of 10 cited sources with relevance scores
- **SC-003**: 95% of key findings in the report have confidence scores above 0.7
- **SC-004**: Human approval gates pause the workflow within 5 seconds of reaching the approval point
- **SC-005**: Crash recovery resumes workflows from the last checkpoint within 30 seconds of restart
- **SC-006**: The A2A Agent Card correctly describes all capabilities and other FTEs can successfully submit tasks
- **SC-007**: All 5 sub-agents are visible in distributed traces with timing breakdown
- **SC-008**: Agent Evals pass 95%+ of the Golden Dataset (50+ research scenarios) before deployment
- **SC-009**: The system operates on $0 infrastructure licensing — only LLM API token costs

## Assumptions

- Web search MCP server is available and configured (e.g., Brave Search, Tavily, or similar)
- LLM API keys (Anthropic, OpenAI/LiteLLM, Google) are provided via environment variables or Dapr Secrets
- Redis is available as state store for Dapr Workflows
- Kafka cluster is available for event pub/sub
- Kubernetes cluster with gVisor runtime is available for sandbox deployment
- PDF generation tool (pandoc or weasyprint) is available in the container image
