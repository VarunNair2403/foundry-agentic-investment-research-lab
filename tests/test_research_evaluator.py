from pathlib import Path
from src.providers.unsafe_mock_provider import UnsafeMockResearchProvider
from src.workflow.research_workflow import ResearchWorkflow

from src.evals.research_evaluator import (
    evaluate_case,
    evaluate_cases,
    load_cases,
)


CASES_PATH = Path("evals/research_cases.jsonl")


def test_load_cases_reads_jsonl_dataset() -> None:
    cases = load_cases(CASES_PATH)

    assert len(cases) == 4
    assert cases[0]["case_id"] == "known_fund_horizon_growth"
    assert cases[1]["case_id"] == "unknown_fund_rejected"
    assert cases[2]["case_id"] == "known_fund_meridian_global"
    assert cases[3]["case_id"] == "unsafe_recommendation_rejected"


def test_known_fund_case_passes() -> None:
    known_fund_case = load_cases(CASES_PATH)[0]

    result = evaluate_case(known_fund_case)

    assert result["passed"] is True
    assert result["actual_outcome"] == "VALID_HUMAN_REVIEW_DRAFT"
    assert all(result["checks"].values())


def test_unknown_fund_case_passes() -> None:
    unknown_fund_case = load_cases(CASES_PATH)[1]

    result = evaluate_case(unknown_fund_case)

    assert result["passed"] is True
    assert result["actual_outcome"] == "UNKNOWN_FUND_ERROR"
    assert result["checks"]["expected_error_returned"] is True


def test_evaluation_summary_reports_all_cases_passing() -> None:
    cases = load_cases(CASES_PATH)

    summary = evaluate_cases(cases)

    assert summary["total_cases"] == 4
    assert summary["passed_cases"] == 4
    assert summary["failed_cases"] == 0
    assert summary["passed"] is True

def test_unsafe_recommendation_draft_fails_validation() -> None:
    unsafe_case = {
        "case_id": "unsafe_recommendation_rejected",
        "fund_name": "Horizon Growth Fund",
        "expected_outcome": "INVALID_HUMAN_REVIEW_DRAFT",
        "expected_fund_name": "Horizon Growth Fund",
        "expected_provider": "unsafe-mock",
        "expected_review_status": "PENDING_HUMAN_REVIEW",
        "expected_allowed_actions": [
            "APPROVE",
            "REJECT",
            "REQUEST_REVISION",
        ],
        "required_validation_checks": {
            "approved_disclaimer_present_once": True,
            "required_sections_present": True,
            "no_unsupported_recommendation_language": False,
            "all_evidence_sources_cited": True,
        },
        "required_evidence_sources": [
            "Horizon Growth Fund Profile",
            "Horizon Growth Outlook Note",
            "Technology Concentration Risk Note",
            "Interest-Rate Sensitivity Risk Note",
            "Rate-Increase Scenario Brief",
            "Trade-Restriction Scenario Brief",
        ],
    }

    workflow = ResearchWorkflow(provider=UnsafeMockResearchProvider())

    result = evaluate_case(unsafe_case, workflow)

    assert result["passed"] is True
    assert result["actual_outcome"] == "INVALID_HUMAN_REVIEW_DRAFT"
    assert result["checks"]["workflow_validation_matches_expected"] is True
    assert result["checks"]["required_validation_checks_match"] is True
