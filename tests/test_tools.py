import pytest

from openincident.models.incident import ActionType, AgentDecision
from openincident.tools.investigation import run_investigation_tool
from openincident.tools.remediation import execute
from openincident.tools.simulated import SimulatedBackend
from openincident.tools.verification import verify_recovery


def decision(action: ActionType, service: str = "payment-api") -> AgentDecision:
    return AgentDecision(
        incident_type="database_connection_exhaustion",
        confidence=0.9,
        recommended_action=action,
        service=service,
    )


def test_broken_state_is_unhealthy():
    backend = SimulatedBackend()
    assert not verify_recovery(backend, "payment-api").resolved


def test_rollback_fixes_incident():
    backend = SimulatedBackend()
    result = execute(backend, decision(ActionType.ROLLBACK_DEPLOYMENT))
    assert result.success
    assert verify_recovery(backend, "payment-api").resolved


def test_restart_does_not_fix_incident():
    backend = SimulatedBackend()
    assert execute(backend, decision(ActionType.RESTART_SERVICE)).success
    assert not verify_recovery(backend, "payment-api").resolved


def test_unsupported_action_fails_cleanly():
    result = execute(SimulatedBackend(), decision(ActionType.SCALE_SERVICE))
    assert not result.success


def test_unknown_service_fails_cleanly():
    result = execute(SimulatedBackend(), decision(ActionType.RESTART_SERVICE, service="nope"))
    assert not result.success


def test_hallucinated_tool_name_is_rejected():
    with pytest.raises(ValueError):
        run_investigation_tool(SimulatedBackend(), "delete_everything", "payment-api")


def test_investigation_tools_return_evidence():
    backend = SimulatedBackend()
    assert "ConnectionPoolExhausted" in " ".join(
        run_investigation_tool(backend, "get_logs", "payment-api")
    )
    deployments = run_investigation_tool(backend, "get_recent_deployments", "payment-api")
    assert deployments[0]["version"] == "v1.8.2"
