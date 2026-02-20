# Implementation Plan: Research Analyst Digital FTE

**Branch**: `001-research-analyst-fte` | **Date**: 2026-02-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-research-analyst-fte/spec.md`

## Summary

Build a Research Analyst Digital FTE — a Custom Agent that autonomously performs multi-step web research using the Agent Factory 8-layer architecture. Uses 5 sub-agents (Research Planner → Source Finder → Content Analyzer → Fact Checker → Report Writer) orchestrated via OpenAI Agents SDK with Claude Agent SDK as the agentic execution engine. FastAPI provides the HTTP/A2A interface, Dapr Workflows ensures crash-proof durable execution, and Kafka handles the event backbone. Output: Markdown report + PDF + JSON metadata.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (with LiteLLM), Anthropic SDK (Claude Agent SDK), Dapr SDK + dapr-ext-workflow, Apache Kafka (via Dapr Pub/Sub), httpx, pydantic, weasyprint (PDF)
**Storage**: Redis (Dapr state store for workflow checkpoints), Kafka (event pub/sub)
**Testing**: pytest + pytest-asyncio, httpx (TestClient), Golden Dataset YAML (Agent Evals)
**Target Platform**: Linux server (Kubernetes with gVisor Agent Sandbox)
**Project Type**: Single service (Digital FTE microservice)
**Performance Goals**: Research report delivered within 15 minutes for standard topics, task acceptance < 2 seconds, approval gate response < 5 seconds
**Constraints**: $0 infrastructure licensing, LLM-only costs, all open-source stack
**Scale/Scope**: Single Digital FTE instance, handling 1 research task at a time (queue via Kafka for concurrency)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Hybrid Multi-SDK Architecture | PASS | OpenAI Agents SDK (L4) for orchestration + Claude Agent SDK (L5) for agentic execution. No single-SDK monolith. |
| II. Spec-Driven Development | PASS | Full spec with 6-section blueprint (Identity, Context, Logic, Triggers, Output, Errors) in spec.md. |
| III. Security-First (Sandbox-First) | PASS | Agent Sandbox (gVisor) at L0. Secrets via Dapr Secrets Management. Network policies restrict egress. |
| IV. Open Standards & Zero-Cost Licensing | PASS | Agent Skills + MCP + A2A protocol stack. Dapr Workflows (not Temporal Cloud). Kafka via Dapr Pub/Sub. $0 infra. |
| V. Observability & Agent Evals | PASS | Golden Dataset (50+ scenarios), Prometheus metrics, OpenTelemetry traces, Logfire for LLM tracking. |
| VI. Smallest Viable Diff | PASS | Single Digital FTE, minimal scope. No speculative features. |
| VII. Human-in-the-Loop Guardrails | PASS | OpenAI SDK guardrails (PII, budget, jailbreak). Dapr Workflow external events for approval gates. |
| VIII. Event-Driven & Crash-Proof | PASS | Dapr Workflows with checkpointing. Kafka for all events. 7-year audit retention. |
| IX. Digital FTE Economics | PASS | 168 hrs/week availability, $0 infra, LLM-only costs (~$0.25-0.50/task target). |
| X. Provider-Agnostic Model Routing | PASS | LiteLLM for routing: Claude (agentic), Gemini (large-context fact-check), cheapest model (simple tasks). |

**Gate Result**: ALL PASS — proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-research-analyst-fte/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI)
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
src/
├── api/                          # FastAPI layer (L3)
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, CORS, lifespan
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── a2a.py                # A2A protocol endpoints
│   │   ├── tasks.py              # Task submission + status + artifacts
│   │   ├── webhooks.py           # Slack/external webhooks
│   │   └── workflows.py          # Human approval endpoints
│   └── middleware/
│       ├── __init__.py
│       └── auth.py               # OAuth2 authentication
│
├── agents/                        # Agent definitions (L4-L5)
│   ├── __init__.py
│   ├── coordinator.py            # OpenAI Agents SDK coordinator with handoffs
│   ├── claude_agent_wrapper.py   # Claude Agent SDK wrapper (HandoffAgent)
│   ├── guardrails.py             # PII, budget, jailbreak guardrails
│   └── simple_agents.py          # LiteLLM-based lightweight agents
│
├── workflows/                     # Dapr Workflows (L2)
│   ├── __init__.py
│   ├── research_workflow.py      # Main durable research pipeline
│   └── activities.py             # Workflow activities (plan, search, analyze, verify, report)
│
├── tools/                         # Tool implementations
│   ├── __init__.py
│   ├── web_search.py             # Web search MCP client
│   └── pdf_export.py             # Markdown → PDF conversion
│
├── models/                        # Pydantic models
│   ├── __init__.py
│   ├── task.py                   # TaskRequest, TaskResponse, TaskStatus
│   ├── research.py               # ResearchPlan, SourceCollection, Analysis
│   └── report.py                 # VerificationReport, ResearchReport
│
└── config.py                      # Settings, env vars, Dapr config

skills/                            # Runtime Agent Skills (L6)
├── research-planner/SKILL.md
├── source-finder/SKILL.md
├── content-analyzer/SKILL.md
├── fact-checker/SKILL.md
└── report-writer/SKILL.md

kubernetes/                        # Infrastructure configs (L0-L2)
├── sandbox/
│   ├── sandbox.yaml              # Agent Sandbox CRD
│   └── sandbox-pool.yaml         # Pre-warmed pool
├── kafka/
│   └── topics.yaml               # Kafka topic definitions
├── dapr/
│   ├── pubsub.yaml               # Kafka pub/sub component
│   ├── statestore.yaml           # Redis state store
│   └── secrets.yaml              # Secrets component
└── deployment.yaml                # K8s deployment + service

evals/                             # Agent Evals / Golden Dataset
├── golden_dataset.yaml            # 50+ research scenarios
└── run_evals.py                   # Eval runner script

tests/
├── conftest.py
├── unit/
│   ├── test_models.py
│   ├── test_guardrails.py
│   └── test_activities.py
├── integration/
│   ├── test_api.py
│   ├── test_workflow.py
│   └── test_agents.py
└── contract/
    └── test_a2a.py

Dockerfile
requirements.txt
docker-compose.yaml                # Local dev (FastAPI + Redis + Kafka + Dapr)
```

**Structure Decision**: Single-service microservice architecture following the Agent Factory standard project layout. All 8 layers represented: L0 (kubernetes/sandbox), L1 (kubernetes/kafka), L2 (src/workflows + kubernetes/dapr), L3 (src/api), L4 (src/agents/coordinator.py), L5 (src/agents/claude_agent_wrapper.py), L6 (skills/), L7 (src/api/routes/a2a.py).

## Complexity Tracking

No constitution violations to justify. Architecture follows the standard 8-layer pattern exactly.

## Design Decisions

### DD-1: Hybrid Orchestration — OpenAI Agents SDK + Claude Agent SDK

**Decision**: Use OpenAI Agents SDK as the orchestration layer with Claude Agent SDK wrapped as HandoffAgent for agentic execution.

**Rationale**: The coordinator routes tasks to 5 specialist agents. OpenAI SDK provides native handoff support, guardrails, sessions, and tracing. Claude SDK provides agentic capabilities (bash, file ops, MCP) needed by Source Finder and Content Analyzer. This separation means orchestration concerns (routing, safety) are cleanly separated from execution concerns (tool use, data processing).

**Alternatives rejected**:
- Single Claude SDK for everything: No guardrails framework, no handoff management, no provider-agnostic routing
- Single OpenAI SDK for everything: No bash/file/MCP capabilities, can't load Agent Skills natively

### DD-2: LiteLLM for Model Routing

**Decision**: Route models per-agent: Claude Sonnet for agentic agents (Planner, Source Finder, Content Analyzer, Report Writer), Gemini Flash for Fact Checker (2M context for cross-referencing), cheapest available model for simple sub-tasks.

**Rationale**: Each research step has different requirements. Fact Checker benefits from Gemini's 2M token context window for cross-referencing many sources simultaneously. Agentic tasks need Claude's superior tool use. Simple formatting tasks don't need expensive models.

### DD-3: Dapr Workflows for Durability (not Temporal)

**Decision**: Use Dapr Workflows with Redis state store for crash-proof execution.

**Rationale**: $0 licensing cost (vs Temporal Cloud), already integrated with Dapr sidecar, provides the same checkpointing and replay guarantees. Activities checkpoint after each pipeline stage, so a crash mid-research only replays from the last completed stage.

### DD-4: Research Pipeline as Sequential Workflow with Fan-Out

**Decision**: Main pipeline is sequential (Plan → Sources → Analyze → Verify → Report) with fan-out inside Source Finder (parallel search per sub-question).

**Rationale**: Each stage depends on the previous stage's output. However, Source Finder can search for multiple sub-questions in parallel (fan-out/fan-in pattern), significantly reducing total research time. Human approval gates are implemented as `wait_for_external_event` between stages.

### DD-5: Web Search via MCP

**Decision**: Use a web search MCP server (Tavily, Brave Search, or similar) for source discovery.

**Rationale**: MCP provides standardized tool integration. The Source Finder agent calls the web search MCP tool rather than implementing search directly. This is swappable — any MCP-compatible search provider works.

### DD-6: PDF Export via WeasyPrint

**Decision**: Use WeasyPrint for Markdown → PDF conversion inside the container.

**Rationale**: Pure Python solution that runs in gVisor sandbox without external dependencies. Pandoc requires LaTeX which bloats the container image. WeasyPrint produces professional PDFs from HTML/CSS, and markdown-to-HTML conversion is trivial.

## Post-Design Constitution Re-Check

*GATE: Re-evaluated after Phase 1 design completion.*

| Principle | Status | Post-Design Evidence |
|-----------|--------|----------------------|
| I. Hybrid Multi-SDK Architecture | PASS | Confirmed: OpenAI Agents SDK v0.7.0 (L4) with `LitellmModel` for orchestration + Anthropic SDK agentic loop (L5) for execution. Code patterns validated via Context7. |
| II. Spec-Driven Development | PASS | Confirmed: spec.md → plan.md → research.md → data-model.md → contracts/openapi.yaml → quickstart.md. Full SDD pipeline. |
| III. Security-First (Sandbox-First) | PASS | Confirmed: gVisor sandbox at L0, Dapr Secrets Management, no hardcoded keys, .env pattern in quickstart. |
| IV. Open Standards & Zero-Cost Licensing | PASS | Confirmed: All packages are open-source (openai-agents, anthropic, dapr, fastapi, weasyprint). $0 infra. A2A + MCP + Agent Skills. |
| V. Observability & Agent Evals | PASS | Confirmed: OpenAI SDK tracing with custom `TracingProcessor`, Prometheus metrics at `/metrics`, Golden Dataset in evals/. |
| VI. Smallest Viable Diff | PASS | Confirmed: Single service, 7 entities in data model, 8 API endpoints. No speculative features. |
| VII. Human-in-the-Loop Guardrails | PASS | Confirmed: `InputGuardrail` for PII/budget/jailbreak (OpenAI SDK), `wait_for_external_event` + `when_any` timeout pattern for approvals (Dapr). |
| VIII. Event-Driven & Crash-Proof | PASS | Confirmed: Dapr Workflows with generator-based `yield` checkpoints, Redis actor state store (`actorStateStore: "true"`), Kafka pub/sub for events. |
| IX. Digital FTE Economics | PASS | Confirmed: Docker Compose for dev ($0), Kubernetes for prod ($0 licensing). LLM costs estimated $0.25-0.50/task via LiteLLM routing. |
| X. Provider-Agnostic Model Routing | PASS | Confirmed: `LitellmModel(model="anthropic/...")`, `LitellmModel(model="gemini/...")`, string shorthand `"litellm/anthropic/..."` all validated. |

**Post-Design Gate Result**: ALL PASS — proceed to Phase 2 (task generation via `/sp.tasks`).

## Phase Completion Summary

### Phase 0: Research — COMPLETE
- **Output**: [research.md](research.md)
- **Findings**: 6 research topics resolved (OpenAI Agents SDK, Claude Agent SDK, Dapr Workflows, A2A Protocol, Web Search MCP, PDF Generation)
- **NEEDS CLARIFICATION**: 0 remaining (all resolved)
- **Key version pins**: openai-agents v0.7.0, dapr-ext-workflow latest, anthropic latest

### Phase 1: Design & Contracts — COMPLETE
- **Data Model**: [data-model.md](data-model.md) — 7 entities (ResearchTask, ResearchPlan, SourceCollection, Analysis, VerificationReport, ResearchReport, ArtifactRef)
- **API Contract**: [contracts/openapi.yaml](contracts/openapi.yaml) — 8 endpoints (tasks CRUD, workflow approval, A2A, health, metrics)
- **Quickstart**: [quickstart.md](quickstart.md) — Prerequisites, install, run, test commands
- **Agent Context**: Updated CLAUDE.md with Python 3.12, FastAPI, OpenAI Agents SDK, Anthropic SDK, Dapr, Kafka, Redis

### Phase 2: Task Generation — PENDING
- Run `/sp.tasks` to generate tasks.md from plan + data-model + contracts
