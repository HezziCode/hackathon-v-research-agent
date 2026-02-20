"""T023: Integration tests for API endpoints."""

from __future__ import annotations

import pytest


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}


class TestTaskSubmission:
    def test_submit_task_returns_202(self, client, sample_task_request):
        resp = client.post("/tasks", json=sample_task_request)
        assert resp.status_code == 202
        data = resp.json()
        assert "task_id" in data
        assert data["status"] == "accepted"

    def test_submit_invalid_query_returns_422(self, client):
        resp = client.post("/tasks", json={"query": "short"})
        assert resp.status_code == 422

    def test_get_task_status(self, client, sample_task_request):
        # Submit first
        submit_resp = client.post("/tasks", json=sample_task_request)
        task_id = submit_resp.json()["task_id"]
        # Get status
        status_resp = client.get(f"/tasks/{task_id}/status")
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "accepted"

    def test_get_task_not_found(self, client):
        resp = client.get("/tasks/nonexistent/status")
        assert resp.status_code == 404

    def test_get_artifacts_empty(self, client, sample_task_request):
        submit_resp = client.post("/tasks", json=sample_task_request)
        task_id = submit_resp.json()["task_id"]
        resp = client.get(f"/tasks/{task_id}/artifacts")
        assert resp.status_code == 200
        assert resp.json()["artifacts"] == []


class TestAgentCard:
    def test_agent_card_returns_200(self, client):
        resp = client.get("/.well-known/agent.json")
        assert resp.status_code == 200
        card = resp.json()
        assert card["name"] == "Research Analyst FTE"
        assert len(card["skills"]) > 0
        assert card["skills"][0]["id"] == "web-research"
