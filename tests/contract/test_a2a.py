"""T054/T055: Contract tests for A2A protocol compliance."""

from __future__ import annotations

import pytest


class TestAgentCardContract:
    """T054: Agent Card must conform to A2A spec."""

    def test_agent_card_has_required_fields(self, client):
        resp = client.get("/.well-known/agent.json")
        assert resp.status_code == 200
        card = resp.json()
        assert "name" in card
        assert "description" in card
        assert "url" in card
        assert "version" in card
        assert "capabilities" in card
        assert "skills" in card
        assert isinstance(card["skills"], list)
        assert len(card["skills"]) > 0

    def test_agent_card_skill_has_required_fields(self, client):
        resp = client.get("/.well-known/agent.json")
        skill = resp.json()["skills"][0]
        assert "id" in skill
        assert "name" in skill
        assert "description" in skill

    def test_agent_card_capabilities(self, client):
        resp = client.get("/.well-known/agent.json")
        caps = resp.json()["capabilities"]
        assert "streaming" in caps
        assert "pushNotifications" in caps
        assert "stateTransitionHistory" in caps


class TestA2AJsonRpc:
    """T055: A2A JSON-RPC 2.0 endpoint compliance."""

    def test_invalid_jsonrpc_version(self, client):
        resp = client.post("/a2a", json={"jsonrpc": "1.0", "id": "1", "method": "tasks/send", "params": {}})
        assert resp.status_code == 400

    def test_unknown_method(self, client):
        resp = client.post("/a2a", json={"jsonrpc": "2.0", "id": "1", "method": "unknown/method", "params": {}})
        assert resp.status_code == 400
        assert "Method not found" in resp.json()["error"]["message"]

    def test_tasks_send_with_short_query(self, client):
        resp = client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "req-1",
            "method": "tasks/send",
            "params": {
                "id": "task-001",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "short"}],
                },
            },
        })
        assert resp.status_code == 400

    def test_tasks_send_valid(self, client):
        resp = client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "req-1",
            "method": "tasks/send",
            "params": {
                "id": "task-001",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Research the current state of AI agents market in 2026"}],
                },
            },
        })
        assert resp.status_code == 200
        result = resp.json()["result"]
        assert "id" in result
        assert result["status"]["state"] == "submitted"

    def test_tasks_get_not_found(self, client):
        resp = client.post("/a2a", json={
            "jsonrpc": "2.0",
            "id": "req-2",
            "method": "tasks/get",
            "params": {"id": "nonexistent-task"},
        })
        assert resp.status_code == 404
