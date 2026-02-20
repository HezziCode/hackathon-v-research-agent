# Phase 0 Research: Research Analyst Digital FTE

**Feature**: 001-research-analyst-fte | **Date**: 2026-02-19 | **Status**: Complete

## R-1: OpenAI Agents SDK (Orchestration Layer — L4)

**Decision**: Use `openai-agents` v0.7.0 with LiteLLM extension for multi-provider orchestration.

**Rationale**: The SDK provides native primitives for Agent, Handoff, InputGuardrail/OutputGuardrail, Runner, function_tool, and tracing — exactly matching our coordinator needs. LiteLLM integration (`LitellmModel`) enables routing to Claude, Gemini, and other providers without changing the orchestration code.

**Alternatives considered**:
- LangGraph: More complex graph-based approach; overkill for a linear pipeline with handoffs
- CrewAI: Higher-level abstraction but less control over guardrails and tracing
- Custom orchestration: No built-in handoff/guardrail/tracing framework

**Key findings**:
- **Package**: `pip install "openai-agents[litellm]"` (v0.7.0)
- **Agent definition**: `Agent(name, instructions, model, tools, handoffs, input_guardrails, output_guardrails, output_type)`
- **Handoffs**: `Agent.handoffs=[other_agent]` or `handoff(agent, tool_name_override, tool_description_override)`
- **Guardrails**: `InputGuardrail(guardrail_function=async_fn)` → returns `GuardrailFunctionOutput(tripwire_triggered=bool)`
- **LiteLLM routing**: `model=LitellmModel(model="anthropic/claude-sonnet-4-5-20250929")` or `model="litellm/anthropic/claude-sonnet-4-5-20250929"`
- **Structured output**: `output_type=PydanticModel` for typed agent responses
- **Context sharing**: `Agent[AppContext]` with `RunContextWrapper[AppContext]` for shared state across agents
- **Tracing**: Built-in with `trace()` context manager, custom `TracingProcessor` for external observability
- **Runner**: `await Runner.run(agent, input, context, run_config)` — async execution

**Code pattern — Coordinator with handoffs + guardrails**:
```python
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput, handoff
from agents.extensions.models.litellm_model import LitellmModel

coordinator = Agent(
    name="Research Coordinator",
    instructions="Route research tasks to specialist agents.",
    model=LitellmModel(model="anthropic/claude-sonnet-4-5-20250929"),
    handoffs=[planner_agent, source_finder_agent, analyzer_agent, fact_checker_agent, report_writer_agent],
    input_guardrails=[InputGuardrail(guardrail_function=pii_check), InputGuardrail(guardrail_function=budget_check)],
)
result = await Runner.run(coordinator, input=task_input, context=app_context)
```

---

## R-2: Claude Agent SDK (Agentic Execution — L5)

**Decision**: Use `anthropic` Python SDK with agentic loop pattern (tool_use stop_reason) for sub-agents that need bash, file ops, or MCP.

**Rationale**: Claude's agentic loop provides superior tool use capabilities (bash execution, file operations, MCP tool integration) needed by Source Finder and Content Analyzer. The pattern is simple — loop on `stop_reason == "tool_use"`, execute tools, feed results back.

**Alternatives considered**:
- Using OpenAI SDK for everything: No native bash/file/MCP tool types
- Direct API calls without wrapper: No reusable pattern; error handling repeated everywhere

**Key findings**:
- **Package**: `pip install anthropic`
- **Agentic loop**: Check `response.stop_reason == "tool_use"` → execute tools → feed `tool_result` back → repeat until `end_turn`
- **Tool definition**: JSON schema with `name`, `description`, `input_schema`
- **Tool result format**: `{"type": "tool_result", "tool_use_id": block.id, "content": result_str}`
- **Async client**: `AsyncAnthropic()` for non-blocking execution
- **Streaming**: `client.messages.stream(...)` context manager with `stream.text_stream`
- **Error handling**: `RateLimitError`, `APIStatusError`, `APIConnectionError`

**Code pattern — ClaudeAgentWrapper (HandoffAgent)**:
```python
class ClaudeAgentWrapper:
    def __init__(self, system_prompt: str, tools: list, tool_executor: Callable, model: str = "claude-sonnet-4-5-20250929"):
        self.client = anthropic.AsyncAnthropic()
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_executor = tool_executor
        self.model = model

    async def run(self, user_input: str, context: dict | None = None) -> dict:
        messages = [{"role": "user", "content": user_input}]
        while True:
            response = await self.client.messages.create(
                model=self.model, max_tokens=4096,
                system=self.system_prompt, tools=self.tools, messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason == "end_turn":
                return {"output": "".join(b.text for b in response.content if hasattr(b, "text"))}
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await self.tool_executor(block.name, block.input)
                        tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
                messages.append({"role": "user", "content": tool_results})
```

---

## R-3: Dapr Workflows (Durable Execution — L2)

**Decision**: Use `dapr-ext-workflow` with Python generator-based workflows, Redis actor state store, and FastAPI lifespan integration.

**Rationale**: Dapr Workflows provide $0 licensing, crash-proof checkpointing via event-sourcing, and native patterns for fan-out/fan-in (`when_all`), human-in-the-loop (`wait_for_external_event`), and timeouts (`create_timer`). Each `yield` is an automatic checkpoint.

**Alternatives considered**:
- Temporal Cloud: $25/month+ licensing, violates Principle IV ($0 infra)
- Celery: No durable checkpointing, no replay-on-crash, no fan-out/fan-in primitives
- Plain asyncio: No crash recovery, no checkpointing

**Key findings**:
- **Packages**: `pip install dapr dapr-ext-workflow dapr-ext-fastapi`
- **Imports**: `from dapr.ext.workflow import WorkflowRuntime, DaprWorkflowContext, WorkflowActivityContext, RetryPolicy, DaprWorkflowClient, when_any, when_all`
- **Workflow**: Generator function decorated `@wfr.workflow(name='...')`, uses `yield ctx.call_activity(...)` for checkpoints
- **Activity**: Function decorated `@wfr.activity(name='...')` — all I/O and side effects live here
- **Crash recovery**: Orchestrator replays from start; completed activities return cached results (no re-execution)
- **Fan-out/Fan-in**: `yield wf.when_all([ctx.call_activity(fn, input=item) for item in items])`
- **Human-in-the-loop**: `yield ctx.wait_for_external_event("event_name")` + `DaprClient.raise_workflow_event()`
- **Timeout pattern**: `winner = yield when_any([event_task, ctx.create_timer(timedelta(hours=1))])`
- **Retry policy**: `RetryPolicy(first_retry_interval, max_number_of_attempts, backoff_coefficient, max_retry_interval)`
- **State store**: Must have `actorStateStore: "true"` and support transactions (Redis for dev)
- **FastAPI integration**: Use `lifespan` context manager to start/stop `WorkflowRuntime()`

**Code pattern — Research workflow with approval gate**:
```python
@wfr.workflow(name='research_workflow')
def research_workflow(ctx: DaprWorkflowContext, task_input: dict):
    # Stage 1: Plan
    plan = yield ctx.call_activity(plan_research, input=task_input)

    # Approval gate (if required)
    if task_input.get("require_approval"):
        event = ctx.wait_for_external_event("plan_approval")
        timeout = ctx.create_timer(timedelta(hours=24))
        winner = yield when_any([event, timeout])
        if winner == timeout:
            return {"status": "timed_out"}
        if not event.result.get("approved"):
            return {"status": "rejected"}

    # Stage 2: Fan-out source finding
    sub_questions = plan["sub_questions"]
    source_tasks = [ctx.call_activity(find_sources, input={"query": sq}) for sq in sub_questions]
    sources = yield when_all(source_tasks)

    # Stage 3-5: Sequential
    analysis = yield ctx.call_activity(analyze_content, input={"sources": sources})
    verification = yield ctx.call_activity(verify_facts, input={"analysis": analysis})
    report = yield ctx.call_activity(write_report, input={"verification": verification})
    return report
```

---

## R-4: A2A Protocol (Inter-FTE Collaboration — L7)

**Decision**: Implement A2A Agent Card at `/.well-known/agent.json` and JSON-RPC 2.0 endpoints for `tasks/send` and `tasks/get`.

**Rationale**: A2A is the standard for agent-to-agent communication in the Agent Factory architecture. It provides discovery via Agent Cards, standardized task submission/status via JSON-RPC 2.0, and streaming via SSE.

**Alternatives considered**:
- Custom REST API: No standardized discovery, no interoperability with other FTEs
- gRPC: More complex setup, not HTTP-native, harder to debug

**Key findings**:
- **Agent Card** at `GET /.well-known/agent.json`: `AgentCard(name, description, url, version, capabilities, skills, authentication, provider)`
- **Task lifecycle states**: `submitted → working → completed | failed | canceled | input-required`
- **JSON-RPC methods**: `tasks/send`, `tasks/get`, `tasks/cancel`, `tasks/sendSubscribe` (SSE), `tasks/pushNotification/set`
- **Message format**: `Message(role="user"|"agent", parts=[TextPart|FilePart|DataPart])`
- **Artifacts**: Named output deliverables with parts array
- **Authentication**: OAuth 2.0 Bearer tokens (or API key for dev)
- **Streaming**: SSE via `tasks/sendSubscribe` with `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`

**Code pattern — Agent Card**:
```python
AGENT_CARD = {
    "name": "Research Analyst FTE",
    "description": "Autonomous multi-step web research agent",
    "url": "https://research-analyst.example.com",
    "version": "1.0.0",
    "capabilities": {"streaming": True, "pushNotifications": False, "stateTransitionHistory": True},
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text", "file"],
    "skills": [
        {"id": "web-research", "name": "Web Research", "description": "Multi-step research on any topic",
         "tags": ["research", "analysis", "report"], "inputModes": ["text"], "outputModes": ["text", "file"]}
    ],
    "provider": {"organization": "Agent Factory", "url": "https://agentfactory.dev"}
}
```

---

## R-5: Web Search via MCP

**Decision**: Use Tavily Search MCP server for web search capability.

**Rationale**: Tavily provides a purpose-built search API for AI agents with relevance scoring, content extraction, and structured results. Available as an MCP server, making it swappable with Brave Search or other MCP-compatible providers.

**Alternatives considered**:
- Brave Search API: Good alternative, slightly less AI-optimized results
- Google Custom Search: Requires billing setup, not MCP-native
- SerpAPI: Paid service, higher per-query cost

**Key findings**:
- **MCP tool**: `tavily_search` with `query`, `max_results`, `search_depth` parameters
- **Environment**: `TAVILY_API_KEY` env var (free tier: 1000 queries/month)
- **Fallback**: Can swap to Brave Search MCP without code changes (MCP abstraction)

---

## R-6: PDF Generation

**Decision**: Use WeasyPrint for Markdown → HTML → PDF conversion.

**Rationale**: Pure Python, runs in gVisor sandbox without external binary dependencies. Markdown is converted to HTML via `markdown` library, then WeasyPrint renders HTML+CSS to PDF.

**Alternatives considered**:
- Pandoc + LaTeX: Requires large LaTeX installation (~1GB), bloats container image
- wkhtmltopdf: Requires headless browser, potential security concerns in sandbox
- fpdf2: Lower quality output, limited CSS support

**Key findings**:
- **Packages**: `pip install weasyprint markdown`
- **Pipeline**: `markdown.markdown(md_text) → html_string → weasyprint.HTML(string=html).write_pdf(path)`
- **Container note**: WeasyPrint needs `libpango`, `libcairo`, `libgdk-pixbuf` — add to Dockerfile

---

## Research Summary

| Topic | Decision | Key Package | Version |
|-------|----------|-------------|---------|
| Orchestration (L4) | OpenAI Agents SDK + LiteLLM | `openai-agents[litellm]` | v0.7.0 |
| Agentic Execution (L5) | Anthropic SDK agentic loop | `anthropic` | latest |
| Durable Workflows (L2) | Dapr Workflows | `dapr-ext-workflow` | latest |
| Event Backbone (L1) | Kafka via Dapr Pub/Sub | `dapr` | latest |
| HTTP Interface (L3) | FastAPI + Dapr FastAPI ext | `fastapi`, `dapr-ext-fastapi` | latest |
| Inter-FTE (L7) | A2A Protocol JSON-RPC 2.0 | Custom implementation | 1.0 |
| Web Search | Tavily MCP | MCP server | latest |
| PDF Export | WeasyPrint | `weasyprint` | latest |

All NEEDS CLARIFICATION items: **RESOLVED** (none remain).
