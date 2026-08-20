from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.audit.audit_logger import DEFAULT_AUDIT_DIRECTORY


ALLOWED_REVIEW_ACTIONS = {
    "APPROVE",
    "REJECT",
    "REQUEST_REVISION",
}

REVIEW_STATUS_BY_ACTION = {
    "APPROVE": "APPROVED",
    "REJECT": "REJECTED",
    "REQUEST_REVISION": "REVISION_REQUESTED",
}


def _review_events_directory(audit_path: Path) -> Path:
    """Return the directory that holds append-only review events."""
    return audit_path.parent / "review_events"


def _load_review_events(
    request_id: str,
    events_directory: Path,
) -> list[dict[str, Any]]:
    """Load all review events associated with a request."""
    return [
        json.loads(path.read_text())
        for path in sorted(events_directory.glob(f"{request_id}_*.json"))
    ]


def record_review_decision(
    audit_path: Path,
    action: str,
    reviewer: str,
    notes: str = "",
) -> dict[str, Any]:
    """Write one append-only human-review event for a pending audit record."""
    normalized_action = action.strip().upper()
    normalized_reviewer = reviewer.strip()

    if normalized_action not in ALLOWED_REVIEW_ACTIONS:
        allowed_actions = ", ".join(sorted(ALLOWED_REVIEW_ACTIONS))
        raise ValueError(
            f"Unsupported review action: '{action}'. "
            f"Allowed actions: {allowed_actions}."
        )

    if not normalized_reviewer:
        raise ValueError("Reviewer identity is required.")

    audit_record = json.loads(audit_path.read_text())

    if audit_record["review_status"] != "PENDING_HUMAN_REVIEW":
        raise ValueError(
            "Review decision is only allowed when status is "
            "PENDING_HUMAN_REVIEW."
        )

    events_directory = _review_events_directory(audit_path)
    events_directory.mkdir(parents=True, exist_ok=True)

    existing_events = _load_review_events(
        audit_record["request_id"],
        events_directory,
    )
    if existing_events:
        raise ValueError(
            "A review decision already exists for this request."
        )

    decided_at = datetime.now(UTC)
    event = {
        "event_type": "HUMAN_REVIEW_DECISION",
        "request_id": audit_record["request_id"],
        "action": normalized_action,
        "review_status": REVIEW_STATUS_BY_ACTION[normalized_action],
        "reviewer": normalized_reviewer,
        "notes": notes.strip(),
        "decided_at": decided_at.isoformat(),
    }

    event_name = (
        f"{audit_record['request_id']}_"
        f"{decided_at.strftime('%Y%m%dT%H%M%S%fZ')}.json"
    )
    event_path = events_directory / event_name

    event_path.write_text(json.dumps(event, indent=2) + "\n")

    return event
