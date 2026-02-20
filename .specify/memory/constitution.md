<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0 (MINOR — added Digital FTE economics, provider-agnostic routing, spec blueprint)
Added principles:
  - IX. Digital FTE Economics
  - X. Provider-Agnostic Model Routing
Amended sections:
  - II. Spec-Driven Development — added the 6-section blueprint requirement
  - IV. Open Standards — strengthened three-protocol stack language
  - Technology Stack — added LiteLLM for provider-agnostic routing
  - Development Workflow — added Agent Evals detail
Previous version (1.0.0) added:
  - I. Agent Factory Architecture (Hybrid Multi-SDK)
  - II. Spec-Driven Development
  - III. Security-First (Sandbox-First)
  - IV. Open Standards & Zero-Cost Licensing
  - V. Observability & Agent Evals
  - VI. Smallest Viable Diff
  - VII. Human-in-the-Loop Guardrails
  - VIII. Event-Driven & Crash-Proof
  - Technology Stack (8-layer architecture)
  - Development Workflow (SDD manufacturing process)
  - Governance
Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ no changes needed
  - .specify/templates/spec-template.md — ✅ no changes needed
  - .specify/templates/tasks-template.md — ✅ no changes needed
Follow-up TODOs: none
-->

# Agent Factory Hackathon Constitution

## Core Principles

### I. Agent Factory Architecture (Hybrid Multi-SDK)

Every Digital FTE MUST be built using the hybrid orchestration
pattern: OpenAI Agents SDK for orchestration (handoffs,
guardrails, sessions, tracing) and Claude Agent SDK for agentic
execution (Computer Use, bash, files, MCP, Skills). FastAPI
serves as the HTTP interface layer. Dapr provides durable
workflow execution. No single-SDK monoliths allowed.

**Rationale**: Separating orchestration from execution enables
provider-agnostic model routing, production-grade guardrails,
and access to Claude-specific agentic capabilities (Computer
Use, native MCP, Agent Skills) that no single SDK provides
alone.

### II. Spec-Driven Development

The Spec is the Source Code. Every Custom Agent / Digital FTE
MUST begin with a written specification (Markdown) covering
the **6-section blueprint**: (1) Identity — persona, role,
tone; (2) Context — MCP servers & data, knowledge base Skills;
(3) Logic — deterministic guardrails, mandatory steps,
never-list, external scripts for deterministic computation;
(4) Success Triggers — keywords, file types, event patterns;
(5) Output Standard — templates, schemas, reporting channels;
(6) Error Protocol — fallbacks, escalation, degradation. The
General Agent (Claude Code) manufactures the Custom Agent from
this spec. No code without a spec; no deployment without a
passing eval.

**Rationale**: Specs are the manufacturing blueprint. Without
them, agents become unpredictable black boxes. SDD ensures
reproducibility, auditability, and enables non-engineers to
define agent behavior.

### III. Security-First (Sandbox-First Principle)

All LLM-generated code execution MUST run inside an Agent
Sandbox (gVisor/Kata Containers) with network policies,
resource limits, and seccomp profiles. Assume all LLM-generated
code is potentially hostile. Never execute untrusted code on
the host. Never hardcode secrets or tokens; use Dapr Secrets
Management backed by Vault or equivalent. OWASP Agentic AI
threats MUST be mitigated at Layer 0.

**Rationale**: Digital FTEs combine LLM code generation, bash
execution, Computer Use, and enterprise integrations — the
blast radius of a compromised agent extends to Kafka, databases,
and APIs. Sandbox-first is non-negotiable.

### IV. Open Standards & Zero-Cost Licensing

The architecture MUST be built entirely on open standards and
zero-cost open-source infrastructure. The three-protocol stack
is mandatory: Agent Skills (domain knowledge), MCP (tool/data
integration), A2A (inter-agent collaboration). Infrastructure
licensing cost MUST be $0 — only pay-per-token for LLM API
calls. Prefer Dapr Workflows over paid alternatives (Temporal
Cloud). Prefer Apache Kafka (via Dapr Pub/Sub) for eventing.

**Rationale**: Zero-cost infrastructure makes Digital FTEs
economically viable at $0.25-0.50/task. Vendor lock-in
contradicts the provider-agnostic thesis.

### V. Observability & Agent Evals

Every Digital FTE MUST have: (1) a Golden Dataset of 50+
real-world scenarios for accuracy testing before deployment,
(2) OpenTelemetry distributed tracing for agent execution,
(3) Prometheus metrics for API layer, (4) Logfire/AgentOps
for LLM cost and performance tracking. Agent Evals MUST use
semantic similarity scoring (exact match + semantic match),
not just pass/fail. Regression testing MUST run on every
SKILL.md update.

**Rationale**: You cannot "hire" a Digital FTE without knowing
its accuracy rate. Evals are the interview; observability is
the performance review.

### VI. Smallest Viable Diff

Every change MUST be the smallest viable diff that achieves
the goal. No unrelated refactoring. No speculative features.
No over-engineering. YAGNI applies. Code is glue — Agent
Skills and MCP do the heavy lifting. Start simple, measure,
then optimize.

**Rationale**: In the Agent Factory model, complexity is the
enemy of reliability. Custom Agents ("Assembly Line") succeed
through simplicity and consistency, not clever abstractions.

### VII. Human-in-the-Loop Guardrails

Every Digital FTE MUST implement deterministic guardrails via
OpenAI Agents SDK: PII detection/masking, budget limits,
jailbreak detection, and domain-specific never-lists. High-
value actions (e.g., approvals above threshold) MUST require
human approval via Dapr Workflow external events. The agent
MUST NOT make autonomous decisions that exceed its delegated
authority.

**Rationale**: 99%+ consistency requires guardrails, not hope.
The "Assembly Line" analogy demands strict process control.
Human-in-the-loop gates are safety valves, not bottlenecks.

### VIII. Event-Driven & Crash-Proof

All Digital FTE task execution MUST be durable via Dapr
Workflows with automatic checkpointing. Crashes MUST trigger
replay from the last checkpointed state. All triggers,
status updates, and audit events MUST flow through Kafka
topics. Audit trails MUST have 7-year retention for
compliance. No fire-and-forget patterns for production tasks.

**Rationale**: A Digital FTE works 168 hours/week. Crashes
are inevitable. Durability is what separates a production
agent from a demo.

### IX. Digital FTE Economics

Every Digital FTE MUST be designed to deliver measurable
economic value: 168 hours/week availability (vs human 40),
cost per task of $0.25-0.50 (vs human $3-6), instant
scaling via duplication, and instant ramp-up via SKILL.md.
The 85-90% cost reduction threshold is the business case.
Infrastructure licensing MUST remain $0 — only LLM API
token costs are acceptable recurring expenses.

**Rationale**: The Digital FTE is priced as headcount, not
software. CEOs approve projects at 85%+ cost reduction
without further debate. Economics drive adoption.

### X. Provider-Agnostic Model Routing

Custom Agents MUST NOT be locked to a single LLM provider.
Use LiteLLM for provider-agnostic model routing across
Claude, GPT, Gemini, and 100+ models. The coordinator
(OpenAI Agents SDK) routes to the optimal model per task:
Claude for agentic execution, Gemini for large-context
analysis, cheapest model for simple Q&A. Model selection
is a runtime decision, not a build-time dependency.

**Rationale**: Provider lock-in contradicts the open-standards
thesis. Model capabilities and pricing change rapidly;
routing flexibility ensures optimal cost-performance ratio.

## Technology Stack

The 8-layer architecture for Custom Agents (Digital FTEs):

| Layer | Technology | Role |
|-------|-----------|------|
| L0 | Agent Sandbox (gVisor) | Secure execution |
| L1 | Apache Kafka | Event backbone |
| L2 | Dapr + Workflows | Infrastructure + durability |
| L3 | FastAPI | HTTP interface + A2A |
| L4 | OpenAI Agents SDK | High-level orchestration |
| L5 | Claude Agent SDK | Agentic execution engine |
| L6 | Runtime Skills + MCP | Domain knowledge + tools |
| L7 | A2A Protocol | Multi-FTE collaboration |

**Two levels of Agent Skills**:
- **Development Skills**: Used by General Agent (Claude Code)
  to BUILD the Digital FTE (e.g., fastapi-service,
  dapr-workflow, openai-agents-sdk, claude-agent-sdk)
- **Runtime Skills**: Used by the Digital FTE to EXECUTE
  business tasks in production (e.g., invoice-validation,
  research-analyst, vendor-matching)

**Project structure** follows:
```
digital-fte/
  src/api/          # FastAPI (L3)
  src/agents/       # Coordinator + Claude wrapper (L4-L5)
  src/workflows/    # Dapr Workflows (L2)
  src/tools/        # MCP clients, Computer Use helpers
  skills/           # Runtime Agent Skills (L6)
  kubernetes/       # Sandbox, Kafka, Dapr configs (L0-L2)
  evals/            # Golden Dataset + accuracy scoring
  tests/            # Unit, integration, contract tests
```

## Development Workflow

The Spec-Driven Manufacturing Process:

1. **Specify**: Human writes spec (Identity, Context, Logic,
   Triggers, Output, Errors) in `specs/<feature>/spec.md`
2. **Plan**: General Agent analyzes spec, loads Development
   Skills, plans architecture in `specs/<feature>/plan.md`
3. **Tasks**: Break plan into dependency-ordered, testable
   tasks in `specs/<feature>/tasks.md`
4. **Implement**: General Agent generates code using
   Development Skills (fastapi-service, dapr-workflow,
   openai-agents-sdk, claude-agent-sdk)
5. **Eval**: Run Golden Dataset (50+ scenarios), verify 95%+
   accuracy before deployment
6. **Deploy**: Containerize, deploy to Kubernetes with Agent
   Sandbox, set up monitoring

**Decision matrix** for execution engine selection:
- GUI automation / RPA: Claude Agent SDK (Computer Use)
- Multi-day research: Claude Agent SDK (bash + MCP)
- Simple Q&A: LiteLLM API call (cheapest model)
- Large document analysis: Gemini API (2M context)
- All cases: OpenAI Agents SDK handles orchestration

## Governance

- This constitution supersedes all other development practices
  for this hackathon project.
- Amendments require: (1) documented rationale, (2) team
  approval, (3) version bump per semver rules below.
- All PRs MUST verify compliance with these principles.
- Complexity beyond the 8-layer architecture MUST be justified
  in a Complexity Tracking table.
- Architectural decisions that meet significance criteria
  (long-term impact + multiple alternatives + cross-cutting
  scope) MUST be documented as ADRs.
- Versioning policy: MAJOR for principle removals/redefinitions,
  MINOR for new principles/sections, PATCH for clarifications.

**Version**: 1.1.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19
