from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.providers.mock_provider import MockResearchProvider
from src.providers.unsafe_mock_provider import UnsafeMockResearchProvider
from src.workflow.research_workflow import ResearchWorkflow


VALID_DRAFT_OUTCOME = "VALID_HUMAN_REVIEW_DRAFT"
INVALID_DRAFT_OUTCOME = "INVALID_HUMAN_REVIEW_DRAFT"
UNKNOWN_FUND_ERROR_OUTCOME = "UNKNOWN_FUND_ERROR"

PROVIDERS = {
    "mock": MockResearchProvider,
    "unsafe-mock": UnsafeMockResearchProvider,
}


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Load one evaluation case per JSONL line."""
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def _workflow_for_case(case: dict[str, Any]) -> ResearchWorkflow:
    """Create a local allowlisted provider workflow for one eval case."""
    provider_name = case.get("provider", "mock")
    provider_class = PROVIDERS.get(provider_name)

    if provider_class is None:
        allowed_provider_names = ", ".join(sorted(PROVIDERS))
        raise ValueError(
            f"Unsupported evaluation provider: {provider_name!r}. "
            f"Allowed providers: {allowed_provider_names}."
        )

    return ResearchWorkflow(provider=provider_class())


def evaluate_case(
    case: dict[str, Any],
    workflow: ResearchWorkflow | None = None,
) -> dict[str, Any]:
    """Run one deterministic workflow evaluation case."""
    workflow = workflow or _workflow_for_case(case)
    expected_outcome = case["expected_outcome"]

    try:
        result = workflow.run(case["fund_name"])
    except ValueError as error:
        expected_error_fragment = case.get("expected_error_fragment", "")
        error_matches = expected_error_fragment in str(error)
        passed = (
            expected_outcome == UNKNOWN_FUND_ERROR_OUTCOME
            and error_matches
        )

        return {
            "case_id": case["case_id"],
            "passed": passed,
            "expected_outcome": expected_outcome,
            "actual_outcome": UNKNOWN_FUND_ERROR_OUTCOME,
            "error": str(error),
            "checks": {
                "expected_error_returned": passed,
            },
        }

    if expected_outcome not in {
        VALID_DRAFT_OUTCOME,
        INVALID_DRAFT_OUTCOME,
    }:
        return {
            "case_id": case["case_id"],
            "passed": False,
            "expected_outcome": expected_outcome,
            "actual_outcome": "UNEXPECTED_WORKFLOW_SUCCESS",
            "checks": {
                "unexpected_success": False,
            },
            "request_id": result["request_id"],
        }

    evidence_source_names = {
        document["name"]
        for document in result["evidence_package"]["documents"]
    }
    required_source_names = set(case["required_evidence_sources"])
    expected_validation_checks = case.get("required_validation_checks", {})
    expected_allowed_actions = case.get("expected_allowed_actions")

    expected_validation_passed = expected_outcome == VALID_DRAFT_OUTCOME
    actual_outcome = (
        VALID_DRAFT_OUTCOME
        if result["validation"]["passed"]
        else INVALID_DRAFT_OUTCOME
    )

    checks = {
        "fund_name_matches": result["fund_name"] == case["expected_fund_name"],
        "provider_matches": result["provider"] == case["expected_provider"],
        "review_status_matches": (
            result["review_status"] == case["expected_review_status"]
        ),
        "workflow_validation_matches_expected": (
            result["validation"]["passed"] is expected_validation_passed
        ),
        "required_sources_retrieved": (
            required_source_names <= evidence_source_names
        ),
        "required_sources_cited": all(
            source_name in result["draft"]
            for source_name in required_source_names
        ),
        "allowed_actions_match": (
            expected_allowed_actions is None
            or result["allowed_actions"] == expected_allowed_actions
        ),
        "required_validation_checks_match": all(
            result["validation"]["checks"].get(name) is expected_value
            for name, expected_value in expected_validation_checks.items()
        ),
    }

    return {
        "case_id": case["case_id"],
        "passed": actual_outcome == expected_outcome and all(checks.values()),
        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
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