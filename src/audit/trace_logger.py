from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRACE_DIRECTORY = PROJECT_ROOT / "traces"


def create_trace_event(
    request_id: str,
    event_name: str,
    status: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a serializable trace event with safe operational metadata."""
    return {
        "request_id": request_id,
        "event_name": event_name,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "metadata": metadata or {},
    }


def write_trace_event(
    event: dict[str, Any],
    trace_directory: Path = DEFAULT_TRACE_DIRECTORY,
) -> Path:
    """Append one trace event to a request-specific local JSONL trace file."""
    trace_directory.mkdir(parents=True, exist_ok=True)
    trace_path = trace_directory / f"{event['request_id']}.jsonl"

    with trace_path.open("a", encoding="utf-8") as trace_file:
        trace_file.write(json.dumps(event) + "\n")

    return trace_path
