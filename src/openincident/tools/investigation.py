"""Read-only tools the model may choose from during an investigation."""

from typing import Any

from openincident.tools.backend import InfrastructureBackend

INVESTIGATION_TOOLS = (
    "get_logs",
    "get_metrics",
    "get_recent_deployments",
    "get_service_status",
)


def run_investigation_tool(backend: InfrastructureBackend, name: str, service: str) -> Any:
    """Run a tool by name. Raises ValueError for names outside the allowed list,
    so a hallucinated tool name from the model can never reach the backend."""
    if name not in INVESTIGATION_TOOLS:
        raise ValueError(f"Unknown investigation tool: {name}")
    return getattr(backend, name)(service)
