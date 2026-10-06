"""Checks whether a remediation actually fixed the incident."""

from openincident.models.incident import VerificationResult
from openincident.tools.backend import InfrastructureBackend


def verify_recovery(
    backend: InfrastructureBackend,
    service: str,
    *,
    max_error_rate: float = 0.05,
    max_latency_ms: float = 1000.0,
) -> VerificationResult:
    metrics = backend.get_metrics(service)
    resolved = metrics["error_rate"] <= max_error_rate and metrics["latency_ms"] <= max_latency_ms
    return VerificationResult(resolved=resolved, metrics=metrics)
