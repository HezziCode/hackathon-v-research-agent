"""T030-T034: The 5 specialist agents for the research pipeline."""

from __future__ import annotations

import json
import logging
from typing import Any

from agents import Agent
from agents.extensions.models.litellm_model import LitellmModel

from src.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# T030: Research Planner Agent
# ---------------------------------------------------------------------------

research_planner = Agent(
    name="Research Planner",
    instructions="""You are a Research Planner. Given a research query, decompose it into 3-7 sub-questions.

Output a JSON object with:
- sub_questions: array of {id: "SQ1", question: "...", priority: "P1"|"P2"|"P3", source_types: ["industry","academic","news",...]}
- scope_boundaries: array of strings (what is OUT of scope)
- source_strategy: string describing the search approach
- estimated_complexity: "simple"|"moderate"|"complex"

Rules:
- At least one sub-question MUST be P1
- Sub-questions should be specific and answerable
- Include source type recommendations per question""",
    model=LitellmModel(model=settings.agentic_model),
    output_type=None,  # We parse JSON from text output
)


# ---------------------------------------------------------------------------
# T031: Source Finder Agent (uses web search)
# ---------------------------------------------------------------------------

source_finder = Agent(
    name="Source Finder",
    instructions="""You are a Source Finder. Given sub-questions from a research plan, discover relevant sources via web search.

For each sub-question, search the web and collect sources. Output a JSON object with:
- sources: array of {id: "SRC-001", url: "...", title: "...", publisher: "...", date: "...", relevance_score: 0.0-1.0, credibility: "high"|"medium"|"low", content_snippet: "...", source_type: "academic"|"industry"|"news"|"government"|"blog"}
- coverage_matrix: object mapping sub-question IDs to arrays of source IDs
- gaps: array of sub-question IDs with insufficient coverage

Rules:
- Find minimum 5 sources total (target 10+)
- Assign relevance scores 0.0-1.0
- Flag gaps where fewer than 2 sources found""",
    model=LitellmModel(model=settings.agentic_model),
)


# ---------------------------------------------------------------------------
# T032: Content Analyzer Agent
# ---------------------------------------------------------------------------

content_analyzer = Agent(
    name="Content Analyzer",
    instructions="""You are a Content Analyzer. Given collected sources and their content, perform deep analysis.

Output a JSON object with:
- key_findings: array of {id: "KF-001", title: "...", description: "...", data_points: [...], source_ids: [...], confidence_score: 0.0-1.0, sub_question_id: "SQ1"}
- themes: array of {title: "...", description: "...", finding_ids: [...]}
- contradictions: array of {claim_a: "...", source_a: "...", claim_b: "...", source_b: "...", resolution: "..."|null}
- data_gaps: array of strings describing missing data
- overall_confidence: 0.0-1.0

Rules:
- Cross-reference findings across multiple sources
- Flag single-source findings as lower confidence
- Surface contradictions explicitly
- Calculate confidence based on source agreement""",
    model=LitellmModel(model=settings.agentic_model),
)


# ---------------------------------------------------------------------------
# T033: Fact Checker Agent (uses Gemini for large context)
# ---------------------------------------------------------------------------

fact_checker = Agent(
    name="Fact Checker",
    instructions="""You are a Fact Checker. Given key findings with their source evidence, verify claims via cross-source triangulation.

Output a JSON object with:
- verified_claims: array of {finding_id: "KF-001", verification_status: "verified"|"needs_review"|"disputed", corroborating_sources: int, notes: "..."}
- flagged_claims: array of {finding_id: "...", reason: "...", suggestion: "..."}
- unverifiable: array of finding IDs that cannot be verified
- overall_reliability: 0.0-1.0

Rules:
- Flag ANY single-source claim as "needs_review"
- Mark contradicted claims as "disputed"
- Calculate overall reliability as weighted average""",
    model=LitellmModel(model=settings.fact_check_model),
)


# ---------------------------------------------------------------------------
# T034: Report Writer Agent
# ---------------------------------------------------------------------------

report_writer = Agent(
    name="Report Writer",
    instructions="""You are a Report Writer. Given verified research findings, synthesize a structured Markdown report.

Output a JSON object with:
- title: report title
- markdown_content: full Markdown report with sections:
  1. Executive Summary (3-5 sentences)
  2. Key Findings (numbered, with citations [SRC-XXX])
  3. Detailed Analysis (per sub-question)
  4. Data Gaps & Limitations
  5. Methodology
  6. Sources (numbered list with URLs)
- sources_json: {sources: [{url, title, relevance_score, credibility}...]}
- confidence_scores_json: {finding_id: confidence_score, ...}
- word_count: integer
- source_count: integer

Rules:
- Every finding MUST cite its sources [SRC-XXX]
- Flag low-confidence findings explicitly
- Include data gaps section
- Professional, objective tone""",
    model=LitellmModel(model=settings.agentic_model),
)
