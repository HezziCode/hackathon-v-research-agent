"""T043/T061: Integration tests for workflow and approval gates."""

from __future__ import annotations

import pytest


class TestWorkflowEndpoints:
    """Test workflow-related API endpoints."""

    def test_workflow_status_requires_dapr(self, client):
        """Without Dapr sidecar, workflow status returns error."""
        resp = client.get("/workflows/nonexistent/status")
        assert resp.status_code == 500

    def test_approval_requires_dapr(self, client):
        """Without Dapr sidecar, approval returns error."""
        resp = client.post(
            "/workflows/nonexistent/approve",
            json={"approved": True, "reason": "Looks good"},
        )
        assert resp.status_code == 500
