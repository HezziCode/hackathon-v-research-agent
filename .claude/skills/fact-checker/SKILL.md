---
name: fact-checker
description: |
  Use when a Digital FTE needs to verify claims, cross-check data points, and validate findings
  from the Content Analyzer. Uses large-context models (Gemini) for comprehensive cross-verification.
  NOT when discovering sources (use source-finder) or writing reports (use report-writer).
---

# Fact Checker — Verification Agent

## Overview

The Fact Checker is a runtime skill for the Research Analyst Digital FTE. It takes analysis output (from Content Analyzer) and verifies claims, cross-checks data points, validates source reliability, and flags unverifiable assertions. Uses Gemini (2M context) for large-document cross-referencing.

## Workflow

```
Analysis Output → Extract Verifiable Claims → Cross-Check Sources → Verify Data Points → Flag Issues → Output Verification Report
```

## Input

Analysis JSON from Content Analyzer (key_findings, data_points, contradictions).

## Output Format

```json
{
  "verification": {
    "verified_claims": [
      {
        "claim_id": "KF-001",
        "claim": "AI agents market projected at $42-47B by 2026",
        "status": "verified",
        "verification_method": "cross-source triangulation",
        "confidence_adjustment": 0.0,
        "notes": "3 independent analyst firms agree within 10% range"
      }
    ],
    "flagged_claims": [
      {
        "claim_id": "KF-005",
        "claim": "Market growing at 45% CAGR",
        "status": "needs_review",
        "issue": "Only one source for this specific CAGR figure",
        "recommendation": "Verify with additional analyst reports or present as single-source estimate"
      }
    ],
    "unverifiable": [
      {
        "claim_id": "KF-008",
        "claim": "APAC region accounts for 30% of market",
        "status": "unverifiable",
        "reason": "No independent sources found to confirm or deny"
      }
    ],
    "overall_reliability": 0.85,
    "human_review_needed": ["KF-005", "KF-008"]
  }
}
```

## Verification Methods

| Method | When to Use | Confidence Boost |
|--------|------------|-----------------|
| Cross-source triangulation | 3+ sources cite same data | +0.1 |
| Primary source trace | Can trace to original study | +0.15 |
| Recency check | Data from last 6 months | +0.05 |
| Publisher reputation | Known analyst firm or institution | +0.1 |
| Internal consistency | Numbers add up, no contradictions | +0.05 |

## Verification Process

1. Extract all verifiable claims (numbers, dates, named entities)
2. For each claim, check if 2+ independent sources agree
3. Trace claims to primary sources where possible
4. Check for stale data (older than 12 months on fast-moving topics)
5. Verify internal consistency (do percentages add to 100%? do trends align?)
6. Flag claims with single source, stale data, or logical inconsistency
7. Recommend human review for flagged and unverifiable claims

## Key Rules

1. Every data point MUST be verified against at least one other source
2. Single-source claims MUST be flagged as "needs_review"
3. Never silently drop unverifiable claims — always report them
4. Confidence adjustments are additive based on verification method
5. Human review recommendations are mandatory for flagged items
6. Overall reliability = average confidence across all verified claims
