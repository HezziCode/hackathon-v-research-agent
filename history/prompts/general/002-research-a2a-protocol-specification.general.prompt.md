---
id: 002
title: Research A2A Protocol Specification
stage: general
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: research
labels: ["a2a", "protocol", "agent-to-agent", "json-rpc", "research"]
links:
  spec: https://github.com/a2aproject/A2A
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/002-research-a2a-protocol-specification.general.prompt.md
tests:
  - none
---

## Prompt

Research the A2A (Agent-to-Agent) Protocol. I need to know:
1. The Agent Card JSON schema (/.well-known/agent.json)
2. The JSON-RPC 2.0 message format for tasks/send and tasks/status
3. Supported communication modes (text, artifacts, streaming)
4. Authentication patterns (OAuth2)
5. Long-running task support
6. Any Python reference implementations

Search the web and check the A2A project at https://github.com/a2aproject/A2A. Return a concise summary with schemas and patterns.

## Response snapshot

Provided comprehensive summary of A2A protocol covering: Agent Card JSON schema with all fields (name, description, url, version, capabilities, authentication, skills, provider); JSON-RPC 2.0 methods (tasks/send, tasks/get, tasks/cancel, tasks/sendSubscribe, tasks/pushNotification/set, tasks/resubscribe); Part types (text, file, data); Artifact model; Task states (submitted, working, input-required, completed, failed, canceled); OAuth 2.0 authentication patterns; Long-running task support via polling, push notifications, and SSE streaming; Python SDK structure with A2AClient, A2AServer, A2AHandler classes and Pydantic type models. Note: external tools were restricted so response was based on training knowledge up to Jan 2025.

## Outcome

- Impact: Research deliverable providing protocol reference for A2A implementation
- Tests: none
- Files: 1 PHR created
- Next prompts: Implement A2A agent, create Agent Card, build A2A server
- Reflection: External tool access (WebFetch, WebSearch, Bash, GitHub MCP) was denied; relied on training knowledge which covers the initial spec but may miss recent updates

## Evaluation notes (flywheel)

- Failure modes observed: All external network tools denied (WebFetch, WebSearch, Bash, GitHub MCP, Context7)
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Re-run with external tool permissions enabled to verify spec against latest repo
