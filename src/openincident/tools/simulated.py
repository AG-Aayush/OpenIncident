"""Simulated infrastructure for the payment-api DB connection exhaustion scenario.

Restarting does not fix this incident; only rolling back the bad deploy does.
"""

from typing import Any

BROKEN_METRICS = {
    "error_rate": 0.31,
    "latency_ms": 4200.0,
    "db_connections": 98.0,
    "db_connection_limit": 100.0,
    "cpu_percent": 42.0,
    "memory_percent": 51.0,
}
HEALTHY_METRICS = {
    "error_rate": 0.012,
    "latency_ms": 380.0,
    "db_connections": 61.0,
    "db_connection_limit": 100.0,
    "cpu_percent": 40.0,
    "memory_percent": 50.0,
}


class SimulatedBackend:
    SERVICE = "payment-api"

    def __init__(self) -> None:
        self.rolled_back = False
        self.actions: list[str] = []

    def _check(self, service: str) -> None:
        if service != self.SERVICE:
            raise ValueError(f"Unknown service: {service}")

    def get_logs(self, service: str) -> list[str]:
        self._check(service)
        if self.rolled_back:
            return ["INFO payment-api v1.8.1 healthy", "INFO HTTP 200 /payments"]
        return [
            "ERROR ConnectionPoolExhausted",
            "ERROR Failed to acquire database connection",
            "ERROR HTTP 500 /payments",
        ]

    def get_metrics(self, service: str) -> dict[str, float]:
        self._check(service)
        return dict(HEALTHY_METRICS if self.rolled_back else BROKEN_METRICS)

    def get_recent_deployments(self, service: str) -> list[dict[str, Any]]:
        self._check(service)
        if self.rolled_back:
            return [{"service": service, "version": "v1.8.1", "deployed_at": "just now"}]
        return [{"service": service, "version": "v1.8.2", "deployed_at": "10 minutes ago"}]

    def get_service_status(self, service: str) -> dict[str, Any]:
        self._check(service)
        version = "v1.8.1" if self.rolled_back else "v1.8.2"
        return {"service": service, "replicas_ready": 3, "replicas_desired": 3, "version": version}

    def restart_service(self, service: str) -> str:
        self._check(service)
        self.actions.append("restart_service")
        return f"Restarted {service}."

    def rollback_deployment(self, service: str) -> str:
        self._check(service)
        self.actions.append("rollback_deployment")
        self.rolled_back = True
        return f"Rolled {service} back to v1.8.1."
