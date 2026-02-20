---
name: nextjs-frontend
description: |
  Use when building the Next.js frontend application for a Digital FTE dashboard.
  Use when creating React components, pages, layouts, API route handlers, or client-side data fetching
  that connects to the FastAPI backend.
  NOT when building backend APIs (use fastapi-service), agent logic (use openai-agents-sdk),
  or infrastructure (use kubernetes-deploy).
---

# Next.js Frontend — Digital FTE Dashboard

## Overview

Next.js serves as the frontend layer for Digital FTE dashboards. It provides a modern React-based UI
for task submission, real-time status tracking, report viewing, and PDF downloads — connecting to the
FastAPI backend via REST API.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Next.js 15 (App Router) | Framework |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS 4 | Styling |
| shadcn/ui | Component library |
| Lucide React | Icons |

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Home / dashboard
│   │   ├── research/
│   │   │   ├── page.tsx        # New research form
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Research detail + report
│   │   └── history/
│   │       └── page.tsx        # Past research list
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   ├── research-form.tsx   # Query submission form
│   │   ├── status-tracker.tsx  # Pipeline progress
│   │   ├── report-viewer.tsx   # Markdown report renderer
│   │   └── nav.tsx             # Navigation
│   ├── lib/
│   │   ├── api.ts              # FastAPI client functions
│   │   └── types.ts            # TypeScript interfaces
│   └── hooks/
│       └── use-polling.ts      # Status polling hook
├── public/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

## API Client Pattern

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitResearch(query: string, budgetUsd: number = 1.0) {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, budget_limit_usd: budgetUsd }),
  });
  return res.json(); // { task_id, status, created_at }
}

export async function getTaskStatus(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/status`);
  return res.json(); // { task_id, status, current_stage, progress_pct }
}

export async function getTaskArtifacts(taskId: string) {
  const res = await fetch(`${API_BASE}/tasks/${taskId}/artifacts`);
  return res.json(); // { artifacts: [{name, content_type, size_bytes}] }
}

export async function downloadArtifact(taskId: string, name: string) {
  return `${API_BASE}/tasks/${taskId}/artifacts/${name}`;
}
```

## Component Patterns

### Research Form
```tsx
// components/research-form.tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitResearch } from "@/lib/api";

export function ResearchForm() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    const result = await submitResearch(query);
    router.push(`/research/${result.task_id}`);
  }

  return (
    <form onSubmit={handleSubmit}>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)}
        placeholder="What would you like to research?"
        minLength={10} maxLength={5000} required />
      <button type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Start Research"}
      </button>
    </form>
  );
}
```

### Status Polling Hook
```typescript
// hooks/use-polling.ts
"use client";
import { useState, useEffect } from "react";
import { getTaskStatus } from "@/lib/api";

export function useTaskPolling(taskId: string, intervalMs = 3000) {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    const poll = async () => {
      const data = await getTaskStatus(taskId);
      setStatus(data);
      if (["completed", "failed", "timed_out"].includes(data.status)) return;
      setTimeout(poll, intervalMs);
    };
    poll();
  }, [taskId, intervalMs]);

  return status;
}
```

### Pipeline Stages Visual
```
Planning → Searching → Analyzing → Fact-Checking → Writing → Complete
   ●──────────●──────────●──────────●──────────●──────────●
```

Map `current_stage` from API to visual progress:
- `planning` → 20%
- `searching` → 40%
- `analyzing` → 60%
- `verifying` → 80%
- `writing` → 95%
- `completed` → 100%

## CORS Configuration

Backend must allow frontend origin. In `src/config.py`:
```python
CORS_ORIGINS=["http://localhost:3000"]  # Next.js dev server
```

## Setup Commands

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
cd frontend
npx shadcn@latest init
npx shadcn@latest add button card input textarea badge progress
npm install lucide-react react-markdown
```

## Key Conventions

1. **App Router only** — no Pages Router
2. **Server Components default** — add `"use client"` only when needed (forms, hooks, state)
3. **Tailwind for styling** — no CSS modules or styled-components
4. **shadcn/ui** — use existing components, customize via Tailwind
5. **Environment variables** — `NEXT_PUBLIC_API_URL` for backend URL
6. **Error handling** — try/catch in API calls, show toast on failure
7. **Loading states** — skeleton/spinner while data loads
