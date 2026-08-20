from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.workflow.research_workflow import ResearchWorkflow


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Load one evaluation case per JSONL line."""
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def evaluate_case(
    case: dict[str, Any],
    workflow: ResearchWorkflow | None = None,
) -> dict[str, Any]:
    """Run one deterministic workflow evaluation case."""
    workflow = workflow or ResearchWorkflow()
    expected_outcome = case["expected_outcome"]

    try:
        result = workflow.run(case["fund_name"])
    except ValueError as error:
        passed = (
            expected_outcome == "UNKNOWN_FUND_ERROR"
            and case["expected_error_fragment"] in str(error)
        )
        return {
            "case_id": case["case_id"],
            "passed": passed,
            "expected_outcome": expected_outcome,
            "actual_outcome": "UNKNOWN_FUND_ERROR",
            "error": str(error),
            "checks": {
                "expected_error_returned": passed,
            },
        }

    if expected_outcome != "VALID_HUMAN_REVIEW_DRAFT":
        return {
            "case_id": case["case_id"],
            "passed": False,
            "expected_outcome": expected_outcome,
            "actual_outcome": "VALID_HUMAN_REVIEW_DRAFT",
            "checks": {
                "unexpected_success": False,
            },
        }

    evidence_source_names = {
        document["name"]
        for document in result["evidence_package"]["documents"]
    }
    required_source_names = set(case["required_evidence_sources"])

    checks = {
        "fund_name_matches": result["fund_name"] == case["expected_fund_name"],
        "provider_matches": result["provider"] == case["expected_provider"],
        "review_status_matches": (
            result["review_status"] == case["expected_review_status"]
        ),
        "workflow_validation_passed": result["validation"]["passed"],
        "required_sources_retrieved": (
            required_source_names <= evidence_source_names
        ),
        "required_sources_cited": all(
            source_name in result["draft"]
            for source_name in required_source_names
        ),
    }

    return {
        "case_id": case["case_id"],
        "passed": all(checks.values()),
        "expected_outcome": expected_outcome,
        "actual_outcome": "VALID_HUMAN_REVIEW_DRAFT",
        "checks": checks,
        "request_id": result["request_id"],
    }


def evaluate_cases(
    cases: list[dict[str, Any]],
    workflow: ResearchWorkflow | None = None,
) -> dict[str, Any]:
    """Evaluate a dataset and return a machine-readable summary."""
    results = [evaluate_case(case, workflow) for case in cases]

    return {
        "total_cases": len(results),
        "passed_cases": sum(result["passed"] for result in results),
        "failed_cases": sum(not result["passed"] for result in results),
        "passed": all(result["passed"] for result in results),
        "results": results,
    }
