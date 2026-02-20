# Fact Checker Skill

Verify research claims via cross-source triangulation.

## Input
- Key findings with source evidence

## Output (JSON)
- verified_claims: [{finding_id, verification_status, corroborating_sources}]
- flagged_claims: [{finding_id, reason, suggestion}]
- unverifiable: [finding_ids]
- overall_reliability: 0.0-1.0

## Rules
- Flag ANY single-source claim as "needs_review"
- Mark contradicted claims as "disputed"
- Calculate weighted average reliability
