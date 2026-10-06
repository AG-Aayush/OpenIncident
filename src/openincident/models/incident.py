"""Core data models shared across OpenIncident."""

from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ActionType(StrEnum):
    RESTART_SERVICE = "restart_service"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"
    SCALE_SERVICE = "scale_service"
    ESCALATE = "escalate"


class PolicyOutcome(StrEnum):
    AUTO_EXECUTE = "auto_execute"
    REQUIRE_APPROVAL = "require_approval"
    ESCALATE = "escalate"


class Incident(BaseModel):
    id: str
    alert_name: str
    service: str
    severity: Severity = Severity.WARNING
    summary: str = ""
    started_at: datetime | None = None
    labels: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_alertmanager_alert(cls, alert: dict[str, Any], incident_id: str) -> Self:
        """Build an Incident from one entry of an Alertmanager webhook's `alerts` list."""
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        try:
            severity = Severity(labels.get("severity", "warning").lower())
        except ValueError:
            severity = Severity.WARNING
        service = (
            labels.get("service") or labels.get("app") or labels.get("deployment") or "unknown"
        )
        return cls(
            id=incident_id,
            alert_name=labels.get("alertname", "unknown"),
            service=service,
            severity=severity,
            summary=annotations.get("summary", ""),
            started_at=alert.get("startsAt"),
            labels=labels,
        )


class AgentDecision(BaseModel):
    """What the LLM concluded. Validated before any code acts on it."""

    incident_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_action: ActionType
    service: str
    version: str | None = None
    reasoning: str = ""


class PolicyResult(BaseModel):
    outcome: PolicyOutcome
    reason: str


class RemediationResult(BaseModel):
    success: bool
    message: str = ""


class VerificationResult(BaseModel):
    resolved: bool
    metrics: dict[str, float] = Field(default_factory=dict)
