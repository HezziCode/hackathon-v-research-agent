# Data Model: Research Analyst Digital FTE

**Feature**: 001-research-analyst-fte | **Date**: 2026-02-19 | **Spec**: [spec.md](spec.md)

## Entity Definitions

### 1. ResearchTask

The top-level entity representing a user-submitted research request.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` (UUID4) | Yes | Unique task identifier |
| `query` | `str` | Yes | The research question/topic |
| `status` | `TaskStatus` enum | Yes | Current lifecycle state |
| `require_approval` | `bool` | No | Whether human approval gates are enabled (default: `false`) |
| `budget_limit_usd` | `float` | No | Maximum LLM cost for this task (default: `1.0`) |
| `priority` | `str` enum | No | P1/P2/P3 priority (default: `P2`) |
| `created_at` | `datetime` | Yes | Task creation timestamp |
| `updated_at` | `datetime` | Yes | Last status change timestamp |
| `completed_at` | `datetime | None` | No | Completion timestamp |
| `workflow_instance_id` | `str | None` | No | Dapr workflow instance ID |
| `current_stage` | `PipelineStage` enum | No | Current pipeline stage |
| `error_message` | `str | None` | No | Error details if failed |
| `artifacts` | `list[ArtifactRef]` | No | References to output artifacts |
| `metadata` | `dict` | No | Arbitrary key-value metadata |

**Status transitions**:
```
accepted → planning → sourcing → analyzing → verifying → reporting → completed
    ↓          ↓          ↓           ↓          ↓           ↓
    └──────────┴──────────┴───────────┴──────────┴───────────┴──→ failed
    ↓          ↓          ↓           ↓          ↓           ↓
    └──────────┴──────────┴───────────┴──────────┴───────────┴──→ awaiting_approval
                                                                        ↓
                                                                   rejected
```

**Validation rules**:
- `query` must be 10-5000 characters
- `budget_limit_usd` must be 0.01-100.0
- `status` can only transition forward (or to `failed`/`awaiting_approval`)

---

### 2. ResearchPlan

Output of the Research Planner agent — sub-questions with priorities and strategy.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Reference to parent ResearchTask |
| `sub_questions` | `list[SubQuestion]` | Yes | 3-7 decomposed sub-questions |
| `scope_boundaries` | `list[str]` | Yes | What is explicitly out of scope |
| `source_strategy` | `str` | Yes | Recommended approach for source discovery |
| `estimated_complexity` | `str` enum | Yes | `simple` / `moderate` / `complex` |
| `created_at` | `datetime` | Yes | When the plan was generated |

**SubQuestion**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | e.g., `SQ1`, `SQ2` |
| `question` | `str` | Yes | The specific sub-question text |
| `priority` | `str` enum | Yes | `P1` / `P2` / `P3` |
| `source_types` | `list[str]` | Yes | Recommended source types (e.g., `academic`, `industry`, `news`) |

**Validation rules**:
- Must have 3-7 `sub_questions`
- At least one sub-question must be `P1`

---

### 3. SourceCollection

Curated list of sources discovered by Source Finder.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Reference to parent ResearchTask |
| `sources` | `list[Source]` | Yes | Discovered sources |
| `coverage_matrix` | `dict[str, list[str]]` | Yes | Maps sub-question IDs to source IDs |
| `total_sources` | `int` | Yes | Count of sources |
| `average_relevance` | `float` | Yes | Mean relevance score 0.0-1.0 |
| `gaps` | `list[str]` | No | Sub-questions with insufficient coverage |

**Source**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | e.g., `SRC-001` |
| `url` | `str` | Yes | Source URL |
| `title` | `str` | Yes | Page/document title |
| `publisher` | `str` | No | Publisher name |
| `date` | `str | None` | No | Publication date |
| `relevance_score` | `float` | Yes | 0.0-1.0 relevance to query |
| `credibility` | `str` enum | Yes | `high` / `medium` / `low` |
| `content_snippet` | `str` | No | Key excerpt (max 500 chars) |
| `source_type` | `str` | Yes | `academic`, `industry`, `news`, `government`, `blog` |

**Validation rules**:
- Minimum 5 sources (target 10+)
- `relevance_score` must be 0.0-1.0
- `coverage_matrix` must reference valid sub-question and source IDs

---

### 4. Analysis

Cross-referenced findings from Content Analyzer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Reference to parent ResearchTask |
| `key_findings` | `list[KeyFinding]` | Yes | Major findings extracted |
| `themes` | `list[Theme]` | Yes | Identified themes/patterns |
| `contradictions` | `list[Contradiction]` | No | Conflicting data points |
| `data_gaps` | `list[str]` | No | Areas lacking sufficient data |
| `overall_confidence` | `float` | Yes | Aggregate confidence 0.0-1.0 |

**KeyFinding**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | e.g., `KF-001` |
| `title` | `str` | Yes | Brief finding title |
| `description` | `str` | Yes | Detailed finding text |
| `data_points` | `list[str]` | Yes | Specific numbers/facts |
| `source_ids` | `list[str]` | Yes | Sources supporting this finding |
| `confidence_score` | `float` | Yes | 0.0-1.0 confidence |
| `sub_question_id` | `str` | Yes | Which sub-question this answers |

**Theme**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | `str` | Yes | Theme name |
| `description` | `str` | Yes | Theme analysis |
| `finding_ids` | `list[str]` | Yes | Related findings |

**Contradiction**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim_a` | `str` | Yes | First claim |
| `source_a` | `str` | Yes | Source ID for claim A |
| `claim_b` | `str` | Yes | Contradicting claim |
| `source_b` | `str` | Yes | Source ID for claim B |
| `resolution` | `str | None` | No | How the contradiction was resolved |

---

### 5. VerificationReport

Fact-checking results from the Fact Checker agent.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Reference to parent ResearchTask |
| `verified_claims` | `list[VerifiedClaim]` | Yes | Claims that passed verification |
| `flagged_claims` | `list[FlaggedClaim]` | No | Claims needing review |
| `unverifiable` | `list[str]` | No | Claims that couldn't be verified |
| `overall_reliability` | `float` | Yes | 0.0-1.0 overall reliability score |

**VerifiedClaim**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `finding_id` | `str` | Yes | Reference to KeyFinding |
| `verification_status` | `str` enum | Yes | `verified` / `needs_review` / `disputed` |
| `corroborating_sources` | `int` | Yes | Number of independent sources confirming |
| `notes` | `str` | No | Verification notes |

**FlaggedClaim**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `finding_id` | `str` | Yes | Reference to KeyFinding |
| `reason` | `str` | Yes | Why it was flagged |
| `suggestion` | `str` | No | Suggested resolution |

---

### 6. ResearchReport

Final output package from Report Writer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Reference to parent ResearchTask |
| `title` | `str` | Yes | Report title |
| `markdown_content` | `str` | Yes | Full Markdown report |
| `pdf_path` | `str | None` | No | Path to generated PDF |
| `sources_json` | `dict` | Yes | Structured sources metadata |
| `confidence_scores_json` | `dict` | Yes | Per-finding confidence scores |
| `generated_at` | `datetime` | Yes | Report generation timestamp |
| `word_count` | `int` | Yes | Report word count |
| `source_count` | `int` | Yes | Number of cited sources |

---

### 7. ArtifactRef

Reference to a generated output file.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `str` | Yes | Artifact name (e.g., `research-report.md`) |
| `content_type` | `str` | Yes | MIME type |
| `size_bytes` | `int` | Yes | File size |
| `path` | `str` | Yes | Storage path |

---

## Enums

### TaskStatus
```
accepted | planning | sourcing | analyzing | verifying | reporting |
completed | failed | awaiting_approval | rejected | budget_exceeded
```

### PipelineStage
```
planner | source_finder | content_analyzer | fact_checker | report_writer
```

## Entity Relationships

```
ResearchTask (1) ──→ (1) ResearchPlan
ResearchTask (1) ──→ (1) SourceCollection
ResearchTask (1) ──→ (1) Analysis
ResearchTask (1) ──→ (1) VerificationReport
ResearchTask (1) ──→ (1) ResearchReport
ResearchTask (1) ──→ (N) ArtifactRef

ResearchPlan.sub_questions ←──→ SourceCollection.coverage_matrix
SourceCollection.sources ←──→ Analysis.key_findings.source_ids
Analysis.key_findings ←──→ VerificationReport.verified_claims
Analysis + VerificationReport ──→ ResearchReport
```
