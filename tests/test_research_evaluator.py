from pathlib import Path

from src.evals.research_evaluator import (
    evaluate_case,
    evaluate_cases,
    load_cases,
)


CASES_PATH = Path("evals/research_cases.jsonl")


def test_load_cases_reads_jsonl_dataset() -> None:
    cases = load_cases(CASES_PATH)

    assert len(cases) == 2
    assert cases[0]["case_id"] == "known_fund_horizon_growth"
    assert cases[1]["case_id"] == "unknown_fund_rejected"


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

    assert summary["total_cases"] == 2
    assert summary["passed_cases"] == 2
    assert summary["failed_cases"] == 0
    assert summary["passed"] is True
