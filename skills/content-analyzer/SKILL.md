# Content Analyzer Skill

Perform deep cross-source analysis of collected research sources.

## Input
- Source collection with content

## Output (JSON)
- key_findings: [{id, title, description, data_points, source_ids, confidence_score}]
- themes: [{title, description, finding_ids}]
- contradictions: [{claim_a, source_a, claim_b, source_b}]
- data_gaps: [strings]
- overall_confidence: 0.0-1.0

## Rules
- Cross-reference across multiple sources
- Flag single-source findings as lower confidence
- Surface contradictions explicitly
