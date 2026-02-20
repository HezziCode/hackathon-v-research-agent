---
name: claude-agent-sdk
description: |
  Use when building agentic execution that requires Computer Use (GUI automation), bash execution,
  file operations, native MCP integration, or Agent Skills loading. Use when wrapping Claude SDK
  as execution engine inside OpenAI Agents SDK orchestration.
  NOT when only doing simple API calls or orchestration (use openai-agents-sdk instead).
---

# Claude Agent SDK — Agentic Execution Engine

## Overview

Claude Agent SDK provides the agentic execution engine (L5) for Digital FTEs. It handles tasks requiring Computer Use (GUI automation), bash/shell execution, file operations, native MCP server connections, and Agent Skills loading. Always runs inside an Agent Sandbox (gVisor) for security.

## When This Layer Is Needed

- GUI automation (Computer Use) — legacy systems without APIs
- Bash/shell command execution
- File read/write/edit operations
- Native MCP server integration
- Agent Skills loading (SKILL.md procedural knowledge)
- Any task where the LLM needs to interact with the environment

## Core Pattern: Agentic Loop

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {"type": "computer_20250124", "name": "computer",
     "display_width_px": 1920, "display_height_px": 1080, "display_number": 1},
    {"type": "bash_20250124", "name": "bash"},
    {"type": "text_editor_20250124", "name": "str_replace_editor"}
]

messages = [{"role": "user", "content": task}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=8096,
        system=system_prompt,
        tools=tools,
        messages=messages,
        betas=["computer-use-2025-01-24"]
    )

    if response.stop_reason == "end_turn":
        break  # Task complete

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})
```

## Wrapper Pattern for OpenAI Agents SDK

```python
from agents import HandoffAgent

class ClaudeAgentSDKWrapper(HandoffAgent):
    """Wraps Claude Agent SDK as OpenAI Agents SDK handoff target."""

    def __init__(self, name, skills=None, mcp_servers=None,
                 enable_computer_use=True, enable_bash=True):
        self.client = Anthropic()
        self.skills = skills or []
        self.mcp_servers = mcp_servers or []
        self.tools = self._build_tools(enable_computer_use, enable_bash)

    async def run(self, task: str, context: dict = None) -> dict:
        skills_prompt = self._load_skills()
        # Execute agentic loop (see Core Pattern above)
        # Return {"status": "completed", "output": result, "artifacts": [...]}
```

## Skills Loading

```python
def _load_skills(self) -> str:
    """Load SKILL.md files into system prompt."""
    content = []
    for skill_name in self.skills:
        skill_path = f"/skills/{skill_name}/SKILL.md"
        try:
            with open(skill_path, 'r') as f:
                content.append(f.read())
        except FileNotFoundError:
            pass
    return "\n\n".join(content)
```

## Key Rules

1. ALL Claude SDK execution MUST run inside Agent Sandbox (gVisor)
2. Never execute untrusted LLM-generated code on the host
3. Always wrap as HandoffAgent for OpenAI Agents SDK integration
4. Enable only the tools needed (don't enable Computer Use if not required)
5. Load Skills into system prompt, not user messages
6. Collect artifacts (screenshots, files) for audit trail

## Dependencies

```
anthropic>=0.45.0
```
