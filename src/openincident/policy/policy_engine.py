"""Safety gate: decides whether an AI-proposed action may run, needs a human, or escalates.

Rules are deny-by-default: only actions explicitly listed as auto-approved run
without a human. The model's own opinion about approval is never trusted.
"""

from collections.abc import Collection

from openincident.models.incident import (
    ActionType,
    AgentDecision,
    PolicyOutcome,
    PolicyResult,
)

MIN_CONFIDENCE = 0.6
AUTO_APPROVED_ACTIONS = frozenset({ActionType.RESTART_SERVICE})


def evaluate(
    decision: AgentDecision,
    *,
    min_confidence: float = MIN_CONFIDENCE,
    auto_actions: Collection[ActionType] = AUTO_APPROVED_ACTIONS,
) -> PolicyResult:
    if decision.recommended_action is ActionType.ESCALATE:
        return PolicyResult(outcome=PolicyOutcome.ESCALATE, reason="Agent recommended escalation.")
    if decision.confidence < min_confidence:
        return PolicyResult(
            outcome=PolicyOutcome.ESCALATE,
            reason=f"Confidence {decision.confidence:.2f} is below {min_confidence:.2f}.",
        )
    if decision.recommended_action in auto_actions:
        return PolicyResult(
            outcome=PolicyOutcome.AUTO_EXECUTE,
            reason=f"{decision.recommended_action} is pre-approved.",
        )
    return PolicyResult(
        outcome=PolicyOutcome.REQUIRE_APPROVAL,
        reason=f"{decision.recommended_action} needs human approval.",
    )
