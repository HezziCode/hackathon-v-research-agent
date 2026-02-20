"""Shared test fixtures for Research Analyst FTE."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """FastAPI TestClient without Dapr sidecar."""
    from src.api.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sample_task_request() -> dict:
    """Valid task submission payload."""
    return {
        "query": "What is the current state of AI agents market in 2026?",
        "require_approval": False,
        "budget_limit_usd": 1.0,
        "priority": "P2",
    }


@pytest.fixture()
def sample_task_request_with_approval() -> dict:
    """Task submission with approval gates enabled."""
    return {
        "query": "Research the global renewable energy market trends for 2026",
        "require_approval": True,
        "budget_limit_usd": 2.0,
        "priority": "P1",
    }
