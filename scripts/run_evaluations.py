from __future__ import annotations


import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from src.evals.research_evaluator import evaluate_cases, load_cases


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = PROJECT_ROOT / "evals" / "research_cases.jsonl"
REPORTS_DIRECTORY = PROJECT_ROOT / "evals" / "reports"


def main() -> None:
    cases = load_cases(CASES_PATH)
    summary = evaluate_cases(cases)

    REPORTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_path = REPORTS_DIRECTORY / f"evaluation_report_{timestamp}.json"

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": str(CASES_PATH.relative_to(PROJECT_ROOT)),
        **summary,
    }

    report_path.write_text(json.dumps(report, indent=2) + "\n")

    print(f"Evaluation passed: {report['passed']}")
    print(
        "Cases: "
        f"{report['passed_cases']}/{report['total_cases']} passed"
    )
    print(f"Report written: {report_path.relative_to(PROJECT_ROOT)}")
    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
