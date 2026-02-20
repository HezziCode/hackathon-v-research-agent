---
id: 001
title: Update CLAUDE.md and Constitution for Agent Factory
stage: general
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: huzaifasys
command: /resume
labels: ["claude-md", "constitution", "agent-factory", "hackathon-docs"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
  - .specify/memory/constitution.md
tests:
  - (none)
---

## Prompt

according to this hackathone docs requirment > The Agent Factory Architecture ... Update main claude file and if constitution also update if need

(User provided the full Agent Factory Architecture hackathon document — a comprehensive architecture spec covering: General Agents vs Custom Agents, Digital FTEs, 8-layer architecture (L0-L7), hybrid orchestration pattern (OpenAI Agents SDK + Claude Agent SDK), Agent Skills (Development + Runtime), MCP, A2A Protocol, Dapr Workflows, FastAPI, Agent Sandbox, Kafka, Agent Evals, Spec-Driven Development, project structure, and complete code examples.)

## Response snapshot

Updated both `CLAUDE.md` and `.specify/memory/constitution.md` to align with the Agent Factory hackathon architecture document:

**CLAUDE.md changes:**
- Added "Agent Factory Context" section with General Agent vs Custom Agent table
- Added Hybrid Orchestration Pattern (OpenAI Agents SDK + Claude Agent SDK + FastAPI + Dapr)
- Added 8-Layer Architecture table (L0-L7)
- Added Two levels of Agent Skills (Development vs Runtime)
- Added Three-Protocol Agentic Stack (Skills + MCP + A2A)
- Added Decision Matrix for execution engine selection
- Added $0 infrastructure licensing cost note
- Updated Task Context to reflect General Agent (BUILDER) role
- Added Agent Evals as deployment gate in success criteria
- Replaced Basic Project Structure with full Digital FTE project structure
- Added Digital FTE Spec Blueprint (6-section requirement)
- Added Agent Evals section with Golden Dataset requirements

**Constitution changes (1.0.0 → 1.1.0):**
- Added Principle IX: Digital FTE Economics (168hrs/week, $0.25-0.50/task, $0 infra)
- Added Principle X: Provider-Agnostic Model Routing (LiteLLM, runtime model selection)
- Amended Principle II: Added 6-section blueprint requirement for specs
- Updated Sync Impact Report header

## Outcome

- ✅ Impact: CLAUDE.md and constitution now fully aligned with Agent Factory hackathon architecture requirements
- 🧪 Tests: N/A (documentation update)
- 📁 Files: CLAUDE.md, .specify/memory/constitution.md
- 🔁 Next prompts: Begin feature spec for a specific Digital FTE, or run `/sp.specify` for a new feature
- 🧠 Reflection: The existing constitution was well-structured; only 2 new principles and minor amendments were needed. CLAUDE.md needed more substantial updates to encode the Agent Factory context and architecture tables.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify CLAUDE.md renders correctly in Claude Code context loading
