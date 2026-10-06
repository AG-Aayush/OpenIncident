import pytest

from openincident.models.incident import ActionType, AgentDecision, PolicyOutcome
from openincident.policy.policy_engine import evaluate


def make_decision(**overrides) -> AgentDecision:
    data = {
        "incident_type": "database_connection_exhaustion",
        "confidence": 0.9,
        "recommended_action": ActionType.ROLLBACK_DEPLOYMENT,
        "service": "payment-api",
        "version": "v1.8.2",
    }
    data.update(overrides)
    return AgentDecision(**data)


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        (ActionType.RESTART_SERVICE, PolicyOutcome.AUTO_EXECUTE),
        (ActionType.ROLLBACK_DEPLOYMENT, PolicyOutcome.REQUIRE_APPROVAL),
        (ActionType.SCALE_SERVICE, PolicyOutcome.REQUIRE_APPROVAL),
        (ActionType.ESCALATE, PolicyOutcome.ESCALATE),
    ],
)
def test_outcome_per_action(action, expected):
    assert evaluate(make_decision(recommended_action=action)).outcome is expected


def test_low_confidence_escalates_even_for_safe_action():
    decision = make_decision(recommended_action=ActionType.RESTART_SERVICE, confidence=0.3)
    assert evaluate(decision).outcome is PolicyOutcome.ESCALATE


def test_confidence_exactly_at_threshold_is_allowed():
    decision = make_decision(recommended_action=ActionType.RESTART_SERVICE, confidence=0.6)
    assert evaluate(decision).outcome is PolicyOutcome.AUTO_EXECUTE


def test_auto_actions_are_configurable():
    decision = make_decision(recommended_action=ActionType.ROLLBACK_DEPLOYMENT)
    result = evaluate(decision, auto_actions={ActionType.ROLLBACK_DEPLOYMENT})
    assert result.outcome is PolicyOutcome.AUTO_EXECUTE


def test_invalid_confidence_is_rejected_by_the_model():
    with pytest.raises(ValueError):
        make_decision(confidence=1.5)
