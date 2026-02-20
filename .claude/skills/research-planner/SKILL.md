---
name: research-planner
description: |
  Use when a Digital FTE needs to break down a research query into a structured research plan with
  sub-questions, strategy, scope boundaries, and source types. This is the first step in the
  research pipeline before source discovery.
  NOT when actually finding sources or analyzing content (use source-finder or content-analyzer).
---

# Research Planner — Research Strategy Agent

## Overview

The Research Planner is a runtime skill for the Research Analyst Digital FTE. It takes a user's research query and produces a structured research plan: sub-questions to investigate, recommended source types, scope boundaries, and a research strategy.

## Workflow

```
User Query → Parse Intent → Decompose into Sub-Questions → Define Scope → Select Source Strategy → Output Plan
```

## Input Format

```json
{
  "query": "What is the AI agents market size in 2026?",
  "context": {"depth": "comprehensive", "audience": "executive"},
  "constraints": {"max_sources": 20, "time_budget_minutes": 60}
}
```

## Output Format

```json
{
  "research_plan": {
    "title": "AI Agents Market Size Analysis 2026",
    "primary_question": "What is the AI agents market size in 2026?",
    "sub_questions": [
      {"id": "SQ1", "question": "Current market size estimates from analyst firms?", "priority": "P1", "source_types": ["analyst_reports", "market_research"]},
      {"id": "SQ2", "question": "Growth rate and CAGR projections?", "priority": "P1", "source_types": ["financial_reports", "analyst_reports"]},
      {"id": "SQ3", "question": "Key market segments and their sizes?", "priority": "P2", "source_types": ["industry_reports", "news"]},
      {"id": "SQ4", "question": "Major players and market share?", "priority": "P2", "source_types": ["company_reports", "news"]},
      {"id": "SQ5", "question": "Regional breakdown of market?", "priority": "P3", "source_types": ["analyst_reports"]}
    ],
    "scope": {
      "in_scope": ["Market sizing", "Growth projections", "Competitive landscape"],
      "out_of_scope": ["Technical architecture details", "Implementation guides"],
      "time_horizon": "2024-2027"
    },
    "strategy": "Start with P1 analyst reports, triangulate with P2 sources, fill gaps with P3"
  }
}
```

## Planning Heuristics

1. **Decomposition**: Break query into 3-7 sub-questions ordered by priority
2. **Source diversity**: Each sub-question should map to 2+ source types
3. **Scope bounding**: Explicitly state what is NOT being researched
4. **Prioritization**: P1 = must-have, P2 = important, P3 = nice-to-have
5. **Time allocation**: 60% on P1, 30% on P2, 10% on P3

## Key Rules

1. Always produce a structured JSON plan — no freeform text
2. Maximum 7 sub-questions (cognitive load limit)
3. Each sub-question MUST have assigned source types
4. Scope boundaries MUST include explicit out-of-scope items
5. Plan is input to Source Finder — format must be parseable
