"""T029: Claude Agent SDK wrapper with agentic loop (tool_use pattern)."""

from __future__ import annotations

import logging
from typing import Any, Callable

import anthropic

from src.config import settings

logger = logging.getLogger(__name__)


class ClaudeAgentWrapper:
    """Wraps Anthropic SDK with agentic loop: tool_use → execute → feed back → repeat."""

    def __init__(
        self,
        system_prompt: str,
        tools: list[dict] | None = None,
        tool_executor: Callable | None = None,
        model: str | None = None,
        max_turns: int = 10,
    ):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key or None)
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_executor = tool_executor
        self.model = model or "claude-sonnet-4-5-20250929"
        self.max_turns = max_turns

    async def run(self, user_input: str, context: dict | None = None) -> dict[str, Any]:
        """Execute the agentic loop until end_turn or max_turns."""
        messages = [{"role": "user", "content": user_input}]
        turns = 0

        while turns < self.max_turns:
            turns += 1
            kwargs: dict[str, Any] = {
                "model": self.model,
                "max_tokens": 4096,
                "system": self.system_prompt,
                "messages": messages,
            }
            if self.tools:
                kwargs["tools"] = self.tools

            response = await self.client.messages.create(**kwargs)
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                text_parts = [b.text for b in response.content if hasattr(b, "text")]
                return {"output": "".join(text_parts), "turns": turns}

            if response.stop_reason == "tool_use" and self.tool_executor:
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        logger.info("Tool call: %s", block.name)
                        result = await self.tool_executor(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                # No more tool calls, extract text
                text_parts = [b.text for b in response.content if hasattr(b, "text")]
                return {"output": "".join(text_parts), "turns": turns}

        logger.warning("Max turns (%d) reached", self.max_turns)
        text_parts = [b.text for b in messages[-1]["content"] if hasattr(b, "text")]
        return {"output": "".join(text_parts), "turns": turns}
