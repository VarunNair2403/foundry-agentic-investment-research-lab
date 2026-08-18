from __future__ import annotations

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
    "it is not investment advice and does not support a buy, sell, hold, "
    "allocation, or price-target recommendation."
)


def _normalize_text(text: str) -> str:
    """Lowercase text and collapse all whitespace to single spaces."""
    return " ".join(text.lower().split())


def validate_draft(
    draft: str,
    evidence_package: dict[str, Any],
) -> dict[str, Any]:
    """Run deterministic policy, structure, and evidence-source checks."""

    normalized_draft = _normalize_text(draft)
    normalized_disclaimer = _normalize_text(APPROVED_DISCLAIMER)

    disclaimer_count = normalized_draft.count(normalized_disclaimer)
    draft_without_disclaimer = normalized_draft.replace(
        normalized_disclaimer,
        "",
    )

    missing_sections = [
        section
        for section in REQUIRED_SECTIONS
        if section not in draft
    ]

    prohibited_terms_found = [
        term
        for term in PROHIBITED_TERMS
        if term in draft_without_disclaimer
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