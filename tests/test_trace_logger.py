import json
from pathlib import Path

from src.audit.trace_logger import create_trace_event, write_trace_event


def test_create_trace_event_includes_required_fields() -> None:
    event = create_trace_event(
        request_id="REQ-TRACE01",
        event_name="RETRIEVAL_COMPLETED",
        status="SUCCESS",
        metadata={"fund_name": "Horizon Growth Fund"},
    )

    assert event["request_id"] == "REQ-TRACE01"
    assert event["event_name"] == "RETRIEVAL_COMPLETED"
    assert event["status"] == "SUCCESS"
    assert event["metadata"] == {"fund_name": "Horizon Growth Fund"}
    assert event["timestamp"]


def test_write_trace_event_appends_jsonl_records(tmp_path: Path) -> None:
    first_event = create_trace_event(
        request_id="REQ-TRACE01",
        event_name="RETRIEVAL_STARTED",
        status="STARTED",
    )
    second_event = create_trace_event(
        request_id="REQ-TRACE01",
        event_name="RETRIEVAL_COMPLETED",
        status="SUCCESS",
        metadata={"document_count": 6},
    )

    trace_path = write_trace_event(first_event, tmp_path)
    returned_path = write_trace_event(second_event, tmp_path)

    assert returned_path == trace_path
    assert trace_path == tmp_path / "REQ-TRACE01.jsonl"

    stored_events = [
        json.loads(line)
        for line in trace_path.read_text().splitlines()
    ]

    assert stored_events == [first_event, second_event]
