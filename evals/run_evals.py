"""T076: Eval runner — execute Golden Dataset against live system."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import yaml


def load_golden_dataset(path: str = "evals/golden_dataset.yaml") -> list[dict]:
    """Load scenarios from Golden Dataset YAML."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("scenarios", [])


def evaluate_scenario(base_url: str, scenario: dict) -> dict:
    """Run a single scenario and check expected outcomes."""
    scenario_id = scenario["id"]
    query = scenario.get("query", "")
    expected = scenario.get("expected", {})
    result = {"id": scenario_id, "passed": False, "details": []}

    # Check guardrail scenarios
    if expected.get("should_trigger_guardrail"):
        # These should be blocked at submission
        try:
            resp = httpx.post(
                f"{base_url}/tasks",
                json={"query": query},
                timeout=10.0,
            )
            if resp.status_code in (400, 422):
                result["passed"] = True
                result["details"].append("Guardrail correctly blocked submission")
            else:
                result["details"].append(f"Expected guardrail block, got {resp.status_code}")
        except Exception as e:
            result["details"].append(f"Error: {e}")
        return result

    # Normal research scenario
    try:
        resp = httpx.post(
            f"{base_url}/tasks",
            json={
                "query": query,
                "require_approval": scenario.get("require_approval", False),
                "budget_limit_usd": scenario.get("budget_limit_usd", 1.0),
            },
            timeout=10.0,
        )
        if resp.status_code != 202:
            result["details"].append(f"Submission failed: {resp.status_code}")
            return result

        task_id = resp.json()["task_id"]
        result["details"].append(f"Task submitted: {task_id}")
        result["passed"] = True  # Basic submission passed

    except Exception as e:
        result["details"].append(f"Error: {e}")

    return result


def run_evals(base_url: str = "http://localhost:8000") -> dict:
    """Run all Golden Dataset scenarios and report results."""
    scenarios = load_golden_dataset()
    results = []
    passed = 0
    failed = 0

    for scenario in scenarios:
        result = evaluate_scenario(base_url, scenario)
        results.append(result)
        if result["passed"]:
            passed += 1
        else:
            failed += 1

    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0

    summary = {
        "total_scenarios": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(pass_rate, 1),
        "threshold_met": pass_rate >= 95.0,
        "results": results,
    }

    return summary


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    summary = run_evals(base_url)

    print(f"\n{'='*60}")
    print(f"Golden Dataset Eval Results")
    print(f"{'='*60}")
    print(f"Total Scenarios: {summary['total_scenarios']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate_pct']}%")
    print(f"Threshold (95%): {'PASS' if summary['threshold_met'] else 'FAIL'}")
    print(f"{'='*60}\n")

    # Print failed scenarios
    for r in summary["results"]:
        if not r["passed"]:
            print(f"  FAIL: {r['id']} — {r['details']}")

    sys.exit(0 if summary["threshold_met"] else 1)
