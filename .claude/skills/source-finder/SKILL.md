---
name: source-finder
description: |
  Use when a Digital FTE needs to discover and collect relevant sources for research sub-questions
  via web search MCP servers. Takes a research plan and returns a curated list of sources with
  metadata and relevance scores.
  NOT when planning research (use research-planner) or analyzing content (use content-analyzer).
---

# Source Finder — Source Discovery Agent

## Overview

The Source Finder is a runtime skill for the Research Analyst Digital FTE. It takes a research plan (from Research Planner) and discovers relevant sources using web search MCP, evaluates source quality, and returns a curated source collection.

## Workflow

```
Research Plan → Iterate Sub-Questions → Search (Web MCP) → Evaluate Quality → Deduplicate → Score Relevance → Output Sources
```

## Input

Research plan JSON from Research Planner (sub_questions with source_types).

## Output Format

```json
{
  "sources": [
    {
      "id": "SRC-001",
      "url": "https://example.com/report",
      "title": "AI Agents Market Report 2026",
      "source_type": "analyst_report",
      "publisher": "Gartner",
      "date": "2026-01-15",
      "relevance_score": 0.95,
      "answers_questions": ["SQ1", "SQ2"],
      "snippet": "The AI agents market is projected to reach...",
      "credibility": "high"
    }
  ],
  "coverage_matrix": {
    "SQ1": ["SRC-001", "SRC-003", "SRC-007"],
    "SQ2": ["SRC-001", "SRC-004"],
    "SQ3": ["SRC-002", "SRC-005"]
  },
  "gaps": ["SQ5 has only 1 source — consider expanding search"]
}
```

## Source Quality Criteria

| Signal | High Quality | Low Quality |
|--------|-------------|-------------|
| Publisher | Known analyst firm, academic institution | Unknown blog, content farm |
| Date | Within 12 months | Older than 24 months |
| Citations | Cites primary data | No references |
| Specificity | Contains specific data/numbers | Vague generalizations |

## Search Strategy

1. For each sub-question, generate 2-3 search queries
2. Use web search MCP to execute queries
3. Collect top 5 results per query
4. Deduplicate by URL and content similarity
5. Score relevance (0.0-1.0) against sub-question
6. Filter: keep sources with relevance >= 0.6
7. Build coverage matrix — ensure each sub-question has 2+ sources
8. Identify gaps and suggest additional searches

## Key Rules

1. Minimum 2 sources per P1 sub-question
2. Deduplicate before returning (same content, different URLs)
3. Always include credibility assessment
4. Coverage matrix MUST be complete — flag gaps
5. Maximum 20 sources total (prevents analysis overload)
6. Preserve original snippets for fact-checking later
