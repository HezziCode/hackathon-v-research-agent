"""T036: Input guardrails — PII detection, budget tracking, jailbreak detection."""

from __future__ import annotations

import logging
import re

from agents import GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PII Detection Guardrail
# ---------------------------------------------------------------------------

PII_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN"),
    (r"\b\d{16}\b", "credit card"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "phone number"),
]


async def pii_check(ctx: RunContextWrapper, agent, input_text: str) -> GuardrailFunctionOutput:
    """Detect PII in the input and block if found."""
    text = input_text if isinstance(input_text, str) else str(input_text)
    detected = []
    for pattern, pii_type in PII_PATTERNS:
        if re.search(pattern, text):
            detected.append(pii_type)

    if detected:
        logger.warning("PII detected: %s", detected)
        return GuardrailFunctionOutput(
            output_info={"detected_pii": detected},
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(output_info={}, tripwire_triggered=False)


# ---------------------------------------------------------------------------
# Budget Tracking Guardrail
# ---------------------------------------------------------------------------


async def budget_check(ctx: RunContextWrapper, agent, input_text: str) -> GuardrailFunctionOutput:
    """Check if budget limit would be exceeded."""
    # Budget tracking is approximate — based on context metadata
    context = ctx.context if hasattr(ctx, "context") and ctx.context else {}
    budget_limit = context.get("budget_limit_usd", 1.0) if isinstance(context, dict) else 1.0
    spent = context.get("total_spent_usd", 0.0) if isinstance(context, dict) else 0.0

    if spent >= budget_limit:
        logger.warning("Budget exceeded: $%.2f / $%.2f", spent, budget_limit)
        return GuardrailFunctionOutput(
            output_info={"spent": spent, "limit": budget_limit},
            tripwire_triggered=True,
        )
    return GuardrailFunctionOutput(output_info={}, tripwire_triggered=False)


# ---------------------------------------------------------------------------
# Jailbreak Detection Guardrail
# ---------------------------------------------------------------------------

JAILBREAK_PATTERNS = [
    r"ignore (?:previous|all|your) instructions",
    r"you are now",
    r"pretend (?:you are|to be)",
    r"bypass (?:your|the) (?:rules|guidelines|restrictions)",
    r"act as (?:a|an) (?:different|new)",
    r"disregard (?:your|all) (?:rules|safety)",
]


async def jailbreak_check(ctx: RunContextWrapper, agent, input_text: str) -> GuardrailFunctionOutput:
    """Detect jailbreak attempts in input."""
    text = input_text.lower() if isinstance(input_text, str) else str(input_text).lower()

    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, text):
            logger.warning("Jailbreak attempt detected: %s", pattern)
            return GuardrailFunctionOutput(
                output_info={"pattern": pattern},
                tripwire_triggered=True,
            )
    return GuardrailFunctionOutput(output_info={}, tripwire_triggered=False)
