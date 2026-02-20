---
name: research-dashboard
description: |
  Use when building the Research Analyst FTE dashboard UI — the specific pages, components,
  and interactions for submitting research queries, tracking pipeline progress, viewing reports,
  and downloading artifacts.
  NOT when setting up the Next.js project itself (use nextjs-frontend) or building backend (use fastapi-service).
---

# Research Dashboard — FTE-Specific UI

## Overview

The Research Dashboard is the user-facing interface for the Research Analyst Digital FTE.
It translates the 5-agent research pipeline into an intuitive visual experience.

## Pages

### 1. Dashboard Home (`/`)
- Hero section: "AI Research Analyst — Your 24/7 Research Partner"
- Quick research input (text area + submit)
- Active research tasks (cards with live progress)
- Recent completed research (list with dates)
- Stats: total researches, avg completion time, sources analyzed

### 2. New Research (`/research`)
- Full research form:
  - Query (textarea, 10-5000 chars)
  - Priority (low/medium/high/critical)
  - Budget limit (slider, $0.10 - $10.00)
  - Require approval toggle
- Query suggestions / example topics
- Submit → redirect to `/research/[id]`

### 3. Research Detail (`/research/[id]`)
- **Pipeline Tracker** — 5 stages with live status:
  ```
  [✓] Planning  →  [●] Searching  →  [ ] Analyzing  →  [ ] Verifying  →  [ ] Writing
  ```
- **Live Progress** — progress bar with percentage
- **Stage Details** — expandable panels showing:
  - Planning: sub-questions generated
  - Searching: sources found count
  - Analyzing: key findings preview
  - Verifying: confidence score
  - Writing: report preview
- **Approval Gate** — if approval required, show approve/reject buttons
- **Artifacts** — when complete:
  - View full report (rendered markdown)
  - Download PDF
  - View sources JSON
  - View confidence scores

### 4. History (`/history`)
- Paginated list of all research tasks
- Filter by status (active/completed/failed)
- Search by query text
- Sort by date, status, priority

## Key Components

### PipelineTracker
```tsx
interface PipelineStage {
  name: string;
  status: "pending" | "active" | "completed" | "failed";
  icon: LucideIcon;
}

const STAGES: PipelineStage[] = [
  { name: "Planning", icon: Brain },
  { name: "Searching", icon: Search },
  { name: "Analyzing", icon: FileText },
  { name: "Fact-Checking", icon: ShieldCheck },
  { name: "Writing", icon: PenTool },
];
```

### ReportViewer
- Render markdown report with `react-markdown`
- Syntax highlighting for code blocks
- Clickable citation links
- Table of contents sidebar
- Print-friendly layout

### ApprovalGate
- Shows when `approval_pending: true`
- Research plan summary
- Estimated cost
- Approve / Reject buttons
- Calls `POST /workflows/{id}/approve`

## Design System

### Colors (Dark Theme Primary)
```
Background:    hsl(222, 47%, 11%)   — slate-900
Card:          hsl(217, 33%, 17%)   — slate-800
Primary:       hsl(217, 91%, 60%)   — blue-500
Success:       hsl(142, 71%, 45%)   — green-500
Warning:       hsl(38, 92%, 50%)    — amber-500
Error:         hsl(0, 84%, 60%)     — red-500
Text:          hsl(210, 40%, 98%)   — slate-50
Muted:         hsl(215, 20%, 65%)   — slate-400
```

### Layout
- Sidebar navigation (collapsible)
- Main content area with max-width
- Responsive: sidebar → bottom nav on mobile
- Sticky header with search + user menu

## API Integration Map

| UI Action | API Call | Response |
|-----------|----------|----------|
| Submit research | `POST /tasks` | `{ task_id, status }` |
| Poll status | `GET /tasks/{id}/status` | `{ status, stage, progress_pct }` |
| Get artifacts | `GET /tasks/{id}/artifacts` | `{ artifacts: [...] }` |
| Download PDF | `GET /tasks/{id}/artifacts/report.pdf` | Binary file |
| Approve plan | `POST /workflows/{id}/approve` | `{ status }` |
| Get history | `GET /tasks/{id}/status` (per task) | Status per task |
| Agent info | `GET /.well-known/agent.json` | Agent Card |

## Status-to-UI Mapping

```typescript
const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  accepted: { label: "Queued", color: "slate", icon: "Clock" },
  planning: { label: "Planning Research", color: "blue", icon: "Brain" },
  searching: { label: "Finding Sources", color: "purple", icon: "Search" },
  analyzing: { label: "Analyzing Content", color: "amber", icon: "FileText" },
  verifying: { label: "Fact-Checking", color: "orange", icon: "ShieldCheck" },
  writing: { label: "Writing Report", color: "cyan", icon: "PenTool" },
  approval_pending: { label: "Awaiting Approval", color: "yellow", icon: "AlertCircle" },
  completed: { label: "Research Complete", color: "green", icon: "CheckCircle" },
  failed: { label: "Failed", color: "red", icon: "XCircle" },
  timed_out: { label: "Timed Out", color: "red", icon: "Timer" },
};
```

## UX Requirements

1. **Real-time feel** — poll every 3s during active research, stop on completion
2. **Optimistic UI** — show "Submitting..." immediately on form submit
3. **Error recovery** — retry button on failed requests, toast notifications
4. **Empty states** — friendly messages when no research history
5. **Loading skeletons** — shimmer effect while data loads
6. **Responsive** — works on mobile (min 375px width)
7. **Accessible** — proper ARIA labels, keyboard navigation, color contrast
