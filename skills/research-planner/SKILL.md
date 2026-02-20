# Research Planner Skill

Decompose a research query into 3-7 actionable sub-questions with priorities and source strategy.

## Input
- Research query (natural language)

## Output (JSON)
- sub_questions: [{id, question, priority, source_types}]
- scope_boundaries: [strings]
- source_strategy: string
- estimated_complexity: simple|moderate|complex

## Rules
- At least one P1 sub-question
- Sub-questions must be specific and answerable
- Include source type recommendations
