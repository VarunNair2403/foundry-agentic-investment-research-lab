from __future__ import annotations

import re
from typing import Any


PROHIBITED_TERMS = (
    "buy",
    "sell",
    "hold",
    "price target",
    "price-target",
    "allocation recommendation",
)

REQUIRED_SECTIONS = (
    "## Scope",
    "## Fund Summary",
    "## Synthetic Exposure Profile",
    "## Documented Risks",
    "## Relevant Market-Event Scenarios",
    "## Evidence Sources",
    "## Analyst Review Required",
)

APPROVED_DISCLAIMER = (
    "It is not investment advice and does not support a buy, sell, hold, "
    "allocation, or price-target recommendation."
)


def _normalize_text(text: str) -> str:
    """Lowercase text and collapse all whitespace to single spaces."""
    return " ".join(text.lower().split())


def _term_occurrences(text: str, term: str) -> int:
    """Count a prohibited term only as a complete word or phrase."""
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return len(re.findall(pattern, text))


def validate_draft(
    draft: str,
    evidence_package: dict[str, Any],
) -> dict[str, Any]:
    """Run deterministic policy, structure, and evidence-source checks."""
    normalized_draft = _normalize_text(draft)
    normalized_disclaimer = _normalize_text(APPROVED_DISCLAIMER)

    disclaimer_count = normalized_draft.count(normalized_disclaimer)

    prohibited_terms_found = []
    for term in PROHIBITED_TERMS:
        total_occurrences = _term_occurrences(normalized_draft, term)

        allowed_occurrences = (
            _term_occurrences(normalized_disclaimer, term)
            if disclaimer_count == 1
            else 0
        )

        if total_occurrences > allowed_occurrences:
            prohibited_terms_found.append(term)

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if section not in draft
    ]

    source_names = [
        document["name"]
        for document in evidence_package["documents"]
    ]
    missing_sources = [
        source_name
        for source_name in source_names
        if source_name not in draft
    ]

    checks = {
        "approved_disclaimer_present_once": disclaimer_count == 1,
        "required_sections_present": not missing_sections,
        "no_unsupported_recommendation_language": not prohibited_terms_found,
        "all_evidence_sources_cited": not missing_sources,
    }

    return {
        "passed": all(checks.values()),
        "checks": checks,
        "details": {
            "approved_disclaimer_count": disclaimer_count,
            "missing_sections": missing_sections,
            "prohibited_terms_found": prohibited_terms_found,
            "missing_sources": missing_sources,
        },
    }