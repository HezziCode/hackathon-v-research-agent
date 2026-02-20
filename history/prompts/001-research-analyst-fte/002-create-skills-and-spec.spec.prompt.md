---
id: 002
title: Create Agent Skills and Research Analyst FTE Spec
stage: spec
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-research-analyst-fte
branch: 001-research-analyst-fte
user: huzaifasys
command: /sp.specify
labels: ["skills", "spec", "research-analyst", "agent-factory", "development-skills", "runtime-skills"]
links:
  spec: specs/001-research-analyst-fte/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/openai-agents-sdk/SKILL.md
  - .claude/skills/claude-agent-sdk/SKILL.md
  - .claude/skills/fastapi-service/SKILL.md
  - .claude/skills/dapr-workflow/SKILL.md
  - .claude/skills/kafka-setup/SKILL.md
  - .claude/skills/kubernetes-deploy/SKILL.md
  - .claude/skills/a2a-protocol/SKILL.md
  - .claude/skills/research-planner/SKILL.md
  - .claude/skills/source-finder/SKILL.md
  - .claude/skills/content-analyzer/SKILL.md
  - .claude/skills/fact-checker/SKILL.md
  - .claude/skills/report-writer/SKILL.md
  - specs/001-research-analyst-fte/spec.md
  - specs/001-research-analyst-fte/checklists/requirements.md
tests:
  - All 12 skills pass verify.py validation
---

## Prompt

User asked to create skills according to the sample in .claude/skills/creating-skills before starting feature work, then run /sp.specify for the Research Analyst Digital FTE. User chose: General Web Research scope, Markdown + PDF + JSON output, 5 sub-agents (Planner, Source Finder, Content Analyzer, Fact Checker, Report Writer).

## Response snapshot

Created 12 Agent Skills (7 Development + 5 Runtime) following the creating-skills format, then created feature branch 001-research-analyst-fte with full spec.md.

**Development Skills (7)**: openai-agents-sdk, claude-agent-sdk, fastapi-service, dapr-workflow, kafka-setup, kubernetes-deploy, a2a-protocol — each with SKILL.md + scripts/verify.py

**Runtime Skills (5)**: research-planner, source-finder, content-analyzer, fact-checker, report-writer — each with SKILL.md + scripts/verify.py

**Spec**: 6 user stories (P1-P3), 18 functional requirements, 9 measurable success criteria, 5 edge cases, 6 key entities. Checklist passes all items.

## Outcome

- Impact: Full skill foundation + feature spec created for Research Analyst Digital FTE
- Tests: All 12 skills verified via verify.py (pass)
- Files: 12 SKILL.md files, 12 verify.py files, spec.md, requirements checklist
- Next prompts: Run `/sp.plan` to create the architecture plan, or `/sp.clarify` to refine spec
- Reflection: Creating skills first was the right call — they encode the Agent Factory domain knowledge that will guide implementation. The spec has no NEEDS CLARIFICATION markers, all requirements are testable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): verify.py on all 12 skills — PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.plan to validate spec translates cleanly to architecture
