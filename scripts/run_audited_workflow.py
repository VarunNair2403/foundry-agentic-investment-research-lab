from __future__ import annotations

from src.audit.audit_logger import write_audit_record
from src.workflow.research_workflow import ResearchWorkflow


def main() -> None:
    workflow_result = ResearchWorkflow().run("Horizon Growth Fund")
    audit_path = write_audit_record(workflow_result)

    print(f"Request ID: {workflow_result['request_id']}")
    print(f"Provider: {workflow_result['provider']}")
    print(f"Validation passed: {workflow_result['validation']['passed']}")
    print(f"Review status: {workflow_result['review_status']}")
    print(f"Audit record written: {audit_path.relative_to(audit_path.parents[1])}")


if __name__ == "__main__":
    main()
