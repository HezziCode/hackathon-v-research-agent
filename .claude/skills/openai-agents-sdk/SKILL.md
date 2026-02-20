---
name: openai-agents-sdk
description: |
  Use when building Custom Agent orchestration with multi-agent handoffs, guardrails (PII, budget, jailbreak),
  sessions, or tracing. Use when creating coordinator agents that delegate to specialist agents.
  NOT when doing direct Claude API calls or single-agent tasks (use claude-agent-sdk instead).
---

# OpenAI Agents SDK — Orchestration Layer

## Overview

OpenAI Agents SDK provides the orchestration layer (L4) for Digital FTEs. It coordinates multi-agent workflows with handoffs, guardrails, sessions, and tracing. It is provider-agnostic via LiteLLM (supports 100+ LLMs).

## When This Layer Is Needed

- Multi-agent coordination with handoffs
- Input/output guardrails (PII masking, budget limits, jailbreak detection)
- Session management (conversation history across runs)
- Production tracing (Logfire, AgentOps, Braintrust)
- Any Custom Agent that needs to route tasks to different execution engines

## Core Pattern: Coordinator with Handoffs

```python
from agents import Agent, Runner, Guardrail
from agents.extensions.litellm import LiteLLMModel

# Specialist agents
researcher = Agent(
    name="Research Specialist",
    model=LiteLLMModel("anthropic/claude-sonnet-4-5"),
    instructions="You research topics thoroughly."
)

analyst = Agent(
    name="Document Analyst",
    model=LiteLLMModel("google/gemini-2.5-flash"),  # 2M context
    instructions="Analyze large documents efficiently."
)

# Coordinator with handoffs
coordinator = Agent(
    name="Coordinator",
    model=LiteLLMModel("anthropic/claude-sonnet-4-5"),
    instructions="""
    Route tasks to specialists:
    - Research tasks → Research Specialist
    - Large document analysis → Document Analyst
    """,
    handoffs=[researcher, analyst],
    guardrails=[PIIGuardrail(), BudgetGuardrail(max_tokens=1_000_000)]
)

# Run
result = await Runner.run(coordinator, "Analyze this 200-page report")
```

## Guardrail Pattern

```python
from agents import Guardrail

class PIIGuardrail(Guardrail):
    """Detect and mask PII before processing."""
    async def check(self, input: str) -> tuple[bool, str]:
        has_pii = self._detect_pii(input)
        if has_pii:
            return True, self._mask_pii(input)
        return True, input

class BudgetGuardrail(Guardrail):
    """Enforce token budget limits."""
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    async def check(self, input: str) -> tuple[bool, str]:
        estimated = len(input) // 4
        if self.used_tokens + estimated > self.max_tokens:
            return False, "Budget exceeded"
        return True, input
```

## Claude Agent SDK Wrapper Integration

When a task needs agentic capabilities (Computer Use, bash, MCP, Skills), wrap Claude Agent SDK as a HandoffAgent:

```python
from agents import HandoffAgent
from .claude_agent_wrapper import ClaudeAgentSDKWrapper

# Claude SDK wrapper as handoff target
claude_executor = ClaudeAgentSDKWrapper(
    name="Agentic Executor",
    skills=["research-analyst"],
    mcp_servers=["web-search", "github"],
    enable_computer_use=False,
    enable_bash=True
)

coordinator = Agent(
    name="Coordinator",
    handoffs=[claude_executor, simple_agent],
    guardrails=[PIIGuardrail()]
)
```

## Key Rules

1. OpenAI Agents SDK ALWAYS handles orchestration — never bypass it
2. Use LiteLLM for model routing — never hardcode a single provider
3. Every coordinator MUST have at least one guardrail
4. Handoffs are the delegation mechanism — use them for all specialist routing
5. Tracing MUST be enabled in production (Logfire or AgentOps)

## Dependencies

```
openai-agents[litellm]>=0.1.0
litellm>=1.0.0
```

## References

- See `references/handoff-patterns.md` for advanced handoff configurations
- See `references/guardrail-catalog.md` for pre-built guardrail implementations
