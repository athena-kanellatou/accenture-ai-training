"""Offline unit tests for the deterministic custom tools."""

from day24.tools import get_incident, run_diagnostics, search_runbook


def test_get_known_incident() -> None:
    result = get_incident.invoke({"incident_id": "INC-2026-024"})
    assert result["service"] == "checkout-api"
    assert result["severity"] == "high"


def test_get_unknown_incident_returns_error() -> None:
    result = get_incident.invoke({"incident_id": "INC-404"})
    assert "error" in result


def test_diagnostics_expose_database_saturation() -> None:
    result = run_diagnostics.invoke({"service": "checkout-api"})
    assert result["metrics"]["db_pool_utilization_percent"] == 98
    assert result["dependencies"]["orders-db"] == "degraded"


def test_runbook_matching_is_case_insensitive() -> None:
    result = search_runbook.invoke(
        {"problem": "Likely DATABASE CONNECTION EXHAUSTION"}
    )
    assert result["title"] == "database connection exhaustion"
    assert len(result["steps"]) >= 3
