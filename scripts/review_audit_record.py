from __future__ import annotations

import argparse
from pathlib import Path

from src.audit.review_service import record_review_decision


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record a controlled human-review decision for an audit record."
    )
    parser.add_argument(
        "--audit-file",
        required=True,
        help="Path to an audit JSON file, relative to the project root.",
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["APPROVE", "REJECT", "REQUEST_REVISION"],
        help="Human-review decision.",
    )
    parser.add_argument(
        "--reviewer",
        required=True,
        help="Reviewer identity.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional reviewer notes.",
    )
    args = parser.parse_args()

    audit_path = PROJECT_ROOT / args.audit_file
    event = record_review_decision(
        audit_path=audit_path,
        action=args.action,
        reviewer=args.reviewer,
        notes=args.notes,
    )

    print(f"Request ID: {event['request_id']}")
    print(f"Review status: {event['review_status']}")
    print(f"Reviewer: {event['reviewer']}")
    print(f"Decision recorded for: {args.audit_file}")


if __name__ == "__main__":
    main()
