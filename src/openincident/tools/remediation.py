"""Actions that change infrastructure. Only called after the policy engine allows it."""

from openincident.models.incident import ActionType, AgentDecision, RemediationResult
from openincident.tools.backend import InfrastructureBackend


def execute(backend: InfrastructureBackend, decision: AgentDecision) -> RemediationResult:
    action = decision.recommended_action
    try:
        if action is ActionType.RESTART_SERVICE:
            message = backend.restart_service(decision.service)
        elif action is ActionType.ROLLBACK_DEPLOYMENT:
            message = backend.rollback_deployment(decision.service)
        else:
            return RemediationResult(success=False, message=f"Action {action} is not supported.")
    except ValueError as exc:
        return RemediationResult(success=False, message=str(exc))
    return RemediationResult(success=True, message=message)
