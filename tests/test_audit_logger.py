import json
from pathlib import Path

import pytest

from src.audit.audit_logger import build_audit_record, write_audit_record
from src.workflow.research_workflow import ResearchWorkflow


def test_build_audit_record_captures_workflow_provenance() -> None:
    workflow_result = ResearchWorkflow().run("Horizon Growth Fund")

    record = build_audit_record(workflow_result)

    assert record["request_id"] == workflow_result["request_id"]
    assert record["generated_at"] == workflow_result["generated_at"]
    assert record["provider"] == "mock"
    assert record["fund_name"] == "Horizon Growth Fund"
    assert record["review_status"] == "PENDING_HUMAN_REVIEW"
    assert record["validation"]["passed"] is True
    assert "Technology" in record["evidence"]["exposure_names"]
    assert "Horizon Growth Fund Profile" in record["evidence"]["document_names"]
    assert "draft" not in record


def test_write_audit_record_creates_immutable_json_file(
    tmp_path: Path,
) -> None:
    workflow_result = ResearchWorkflow().run("Horizon Growth Fund")

    audit_path = write_audit_record(workflow_result, tmp_path)

    assert audit_path == tmp_path / f"{workflow_result['request_id']}.json"
    assert audit_path.exists()

    stored_record = json.loads(audit_path.read_text())
    assert stored_record["request_id"] == workflow_result["request_id"]
    assert stored_record["validation"]["passed"] is True

    with pytest.raises(FileExistsError, match="already exists"):
        write_audit_record(workflow_result, tmp_path)
