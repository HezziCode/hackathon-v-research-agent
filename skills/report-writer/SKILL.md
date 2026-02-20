# Report Writer Skill

Synthesize research findings into a structured Markdown report with citations.

## Input
- Verified findings, analysis, source data

## Output (JSON)
- title: report title
- markdown_content: full Markdown report
- sources_json: structured sources metadata
- confidence_scores_json: per-finding scores
- word_count: integer
- source_count: integer

## Report Structure
1. Executive Summary (3-5 sentences)
2. Key Findings (numbered, with [SRC-XXX] citations)
3. Detailed Analysis (per sub-question)
4. Data Gaps & Limitations
5. Methodology
6. Sources (numbered list)

## Rules
- Every finding MUST cite its sources
- Flag low-confidence findings
- Professional, objective tone
