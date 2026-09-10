"""Deterministic mock enterprise data used by the Day 24 tools."""

INCIDENTS = {
    "INC-2026-024": {
        "service": "checkout-api",
        "severity": "high",
        "summary": "Checkout requests are returning HTTP 503 errors.",
        "started_at": "2026-09-10T08:42:00Z",
        "affected_region": "westeurope",
    }
}

DIAGNOSTICS = {
    "checkout-api": {
        "application_logs": [
            "08:41:58 connection pool utilization=98%",
            "08:42:03 database connection timeout after 5s",
            "08:42:06 request POST /checkout returned 503",
        ],
        "metrics": {
            "error_rate_percent": 31.8,
            "p95_latency_ms": 6120,
            "cpu_percent": 44,
            "db_pool_utilization_percent": 98,
        },
        "dependencies": {
            "payments-api": "healthy",
            "orders-db": "degraded",
            "inventory-api": "healthy",
        },
    }
}

RUNBOOKS = {
    "database connection exhaustion": [
        "Confirm database health and connection-pool saturation.",
        "Temporarily reduce idle connection lifetime.",
        "Scale the application pool only after checking database capacity.",
        "Verify error rate and p95 latency after remediation.",
    ],
    "http 503": [
        "Check upstream dependencies and recent deployments.",
        "Inspect error rate, latency, and resource saturation.",
        "Use rollback or controlled scaling only with approval.",
    ],
}
