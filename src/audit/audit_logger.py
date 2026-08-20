from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_DIRECTORY = PROJECT_ROOT / "audit"


def build_audit_record(workflow_result: dict[str, Any]) -> dict[str, Any]:
    """Create a minimal, serializable audit record for one workflow run."""
    evidence_package = workflow_result["evidence_package"]

    return {
        "request_id": workflow_result["request_id"],
        "generated_at": workflow_result["generated_at"],
        "provider": workflow_result["provider"],
        "fund_name": workflow_result["fund_name"],
        "review_status": workflow_result["review_status"],
        "allowed_actions": workflow_result["allowed_actions"],
        "validation": workflow_result["validation"],
        "evidence": {
            "exposure_names": [
                item["name"] for item in evidence_package["exposures"]
            ],
            "risk_names": [
                item["name"] for item in evidence_package["risks"]
            ],
            "event_names": [
                item["name"] for item in evidence_package["events"]
            ],
            "document_names": [
                item["name"] for item in evidence_package["documents"]
            ],
        },
    }


def write_audit_record(
    workflow_result: dict[str, Any],
    audit_directory: Path = DEFAULT_AUDIT_DIRECTORY,
) -> Path:
    """Write one immutable local JSON audit record and return its path."""
    audit_directory.mkdir(parents=True, exist_ok=True)
    audit_path = audit_directory / f"{workflow_result['request_id']}.json"

    if audit_path.exists():
        raise FileExistsError(
            f"Audit record already exists for {workflow_result['request_id']}."
        )

    audit_record = build_audit_record(workflow_result)
    audit_path.write_text(json.dumps(audit_record, indent=2) + "\n")

    return audit_path
