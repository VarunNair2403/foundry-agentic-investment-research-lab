from __future__ import annotations

import sys

from src.workflow.research_workflow import ResearchWorkflow


FUND_NAME = "Horizon Growth Fund"


def main() -> None:
    """Run one manual live Foundry smoke test on synthetic evidence."""
    result = ResearchWorkflow.with_foundry().run(FUND_NAME)
    validation = result["validation"]
    evidence_package = result["evidence_package"]

    print("Foundry smoke test completed")
    print(f"Request ID: {result['request_id']}")
    print(f"Provider: {result['provider']}")
    print(f"Fund: {result['fund_name']}")
    print(f"Evidence documents: {len(evidence_package['documents'])}")
    print(f"Validation passed: {validation['passed']}")
    print(f"Review status: {result['review_status']}")
    print(f"Allowed actions: {', '.join(result['allowed_actions'])}")

    if not validation["passed"]:
        print("\nValidation details:")
        print(validation)
        sys.exit(1)

    print(
        "\nSafety result: draft passed deterministic checks and remains "
        "pending qualified human review."
    )


if __name__ == "__main__":
    main()