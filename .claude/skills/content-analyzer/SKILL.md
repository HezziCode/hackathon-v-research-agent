---
name: content-analyzer
description: |
  Use when a Digital FTE needs to perform deep analysis of collected research sources, extracting
  key findings, data points, arguments, and synthesizing insights across multiple sources.
  Uses Claude Agent SDK for agentic content processing (bash, file ops, MCP).
  NOT when discovering sources (use source-finder) or checking facts (use fact-checker).
---

# Content Analyzer — Deep Analysis Agent

## Overview

The Content Analyzer is a runtime skill for the Research Analyst Digital FTE. It takes curated sources (from Source Finder) and performs deep analysis: extracting key findings, data points, quotes, arguments, contradictions, and synthesizing cross-source insights.

## Workflow

```
Source Collection → Fetch Full Content → Extract Key Data → Cross-Reference → Identify Patterns → Synthesize → Output Analysis
```

## Input

Source collection JSON from Source Finder (sources array with URLs and metadata).

## Output Format

```json
{
  "analysis": {
    "key_findings": [
      {
        "id": "KF-001",
        "finding": "AI agents market projected at $XX billion by 2026",
        "confidence": 0.9,
        "sources": ["SRC-001", "SRC-003"],
        "data_points": [
          {"value": "$47.1B", "source": "SRC-001", "context": "Gartner estimate"},
          {"value": "$42.8B", "source": "SRC-003", "context": "McKinsey projection"}
        ]
      }
    ],
    "themes": [
      {"theme": "Rapid growth driven by enterprise adoption", "supporting_sources": 5},
      {"theme": "Regulatory uncertainty as key risk", "supporting_sources": 3}
    ],
    "contradictions": [
      {"topic": "Market size estimate", "positions": [
        {"claim": "$47.1B", "source": "SRC-001"},
        {"claim": "$42.8B", "source": "SRC-003"}
      ], "resolution": "Range is $42-47B, difference due to scope definition"}
    ],
    "data_gaps": ["No reliable data found for APAC regional breakdown"],
    "confidence_scores": {
      "SQ1": 0.9, "SQ2": 0.85, "SQ3": 0.7, "SQ4": 0.8, "SQ5": 0.4
    }
  }
}
```

## Analysis Methodology

1. **Extract**: Pull key data points, quotes, statistics from each source
2. **Cross-reference**: Compare claims across sources — identify agreement and contradiction
3. **Triangulate**: Weight findings by source credibility and recency
4. **Synthesize**: Identify overarching themes and patterns
5. **Quantify confidence**: Score each sub-question answer 0.0-1.0
6. **Flag gaps**: Note where evidence is weak or missing

## Confidence Scoring

| Score | Meaning | Source Requirement |
|-------|---------|-------------------|
| 0.9-1.0 | Very high — consensus across 3+ credible sources | 3+ analyst reports agree |
| 0.7-0.89 | High — strong evidence with minor variance | 2+ credible sources |
| 0.5-0.69 | Moderate — limited sources or some contradiction | 1-2 sources with caveats |
| 0.0-0.49 | Low — insufficient evidence | 0-1 weak sources |

## Key Rules

1. Every finding MUST cite specific sources by ID
2. Contradictions MUST be surfaced, not hidden
3. Confidence scores MUST be data-driven (not vibes)
4. Data gaps are as important as findings — always report them
5. Cross-reference minimum: compare each finding against 2+ sources
6. Output must be structured JSON — input to Fact Checker and Report Writer
