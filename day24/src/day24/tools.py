"""Custom tools exposed to the Deep Agent and its subagents."""

from typing import Any

from langchain_core.tools import tool

from day24.data import DIAGNOSTICS, INCIDENTS, RUNBOOKS


@tool
def get_incident(incident_id: str) -> dict[str, Any]:
    """Return the structured incident record for an incident ID."""

    incident = INCIDENTS.get(incident_id)
    if incident is None:
        return {"error": f"Incident {incident_id!r} was not found."}
    return {"incident_id": incident_id, **incident}


@tool
def run_diagnostics(service: str) -> dict[str, Any]:
    """Return simulated logs, metrics, and dependency health for a service."""

    diagnostics = DIAGNOSTICS.get(service)
    if diagnostics is None:
        return {"error": f"No diagnostics are available for {service!r}."}
    return {"service": service, **diagnostics}


@tool
def search_runbook(problem: str) -> dict[str, Any]:
    """Find the most relevant operational runbook for a problem description."""

    normalized_problem = problem.casefold()
    for title, steps in RUNBOOKS.items():
        if title in normalized_problem or any(
            token in normalized_problem for token in title.split()
        ):
            return {"title": title, "steps": steps}
    return {
        "title": "generic incident investigation",
        "steps": [
            "Collect logs and metrics.",
            "Identify the failing component.",
            "Propose a reversible remediation.",
            "Verify service recovery.",
        ],
    }
