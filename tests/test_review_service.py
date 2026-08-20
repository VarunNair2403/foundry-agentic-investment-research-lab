import json
from pathlib import Path

import pytest

from src.audit.audit_logger import write_audit_record
from src.audit.review_service import record_review_decision
from src.workflow.research_workflow import ResearchWorkflow


def create_pending_audit_record(tmp_path: Path) -> Path:
    workflow_result = ResearchWorkflow().run("Horizon Growth Fund")
    return write_audit_record(workflow_result, tmp_path)


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [
        ("APPROVE", "APPROVED"),
        ("REJECT", "REJECTED"),
        ("REQUEST_REVISION", "REVISION_REQUESTED"),
    ],
)
def test_record_review_decision_writes_append_only_event(
    tmp_path: Path,
    action: str,
    expected_status: str,
) -> None:
    audit_path = create_pending_audit_record(tmp_path)
    original_record = json.loads(audit_path.read_text())

    event = record_review_decision(
        audit_path=audit_path,
        action=action,
        reviewer="portfolio-reviewer",
        notes="Reviewed synthetic evidence package.",
    )

    assert event["event_type"] == "HUMAN_REVIEW_DECISION"
    assert event["request_id"] == original_record["request_id"]
    assert event["action"] == action
    assert event["review_status"] == expected_status
    assert event["reviewer"] == "portfolio-reviewer"
    assert event["notes"] == "Reviewed synthetic evidence package."
    assert event["decided_at"]

    assert json.loads(audit_path.read_text()) == original_record

    event_paths = list(
        (tmp_path / "review_events").glob(f"{original_record['request_id']}_*.json")
    )
    assert len(event_paths) == 1
    assert json.loads(event_paths[0].read_text()) == event


def test_record_review_decision_rejects_invalid_action(
    tmp_path: Path,
) -> None:
    audit_path = create_pending_audit_record(tmp_path)

    with pytest.raises(ValueError, match="Unsupported review action"):
        record_review_decision(
            audit_path=audit_path,
            action="PUBLISH",
            reviewer="portfolio-reviewer",
        )


def test_record_review_decision_requires_reviewer(
    tmp_path: Path,
) -> None:
    audit_path = create_pending_audit_record(tmp_path)

    with pytest.raises(ValueError, match="Reviewer identity is required"):
        record_review_decision(
            audit_path=audit_path,
            action="APPROVE",
            reviewer="  ",
        )


def test_record_review_decision_rejects_second_event(
    tmp_path: Path,
) -> None:
    audit_path = create_pending_audit_record(tmp_path)

    record_review_decision(
        audit_path=audit_path,
        action="APPROVE",
        reviewer="portfolio-reviewer",
    )

    with pytest.raises(
        ValueError,
        match="A review decision already exists for this request",
    ):
        record_review_decision(
            audit_path=audit_path,
            action="REJECT",
            reviewer="another-reviewer",
        )
