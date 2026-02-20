# Source Finder Skill

Discover and collect relevant sources for research sub-questions via web search.

## Input
- Research plan with sub-questions

## Output (JSON)
- sources: [{id, url, title, publisher, relevance_score, credibility, source_type}]
- coverage_matrix: {sub_question_id: [source_ids]}
- gaps: [sub_question_ids with insufficient coverage]

## Rules
- Minimum 5 sources (target 10+)
- Assign relevance scores 0.0-1.0
- Flag gaps where < 2 sources found
