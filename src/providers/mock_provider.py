from __future__ import annotations

from typing import Any


PROHIBITED_TERMS = (
    "buy",
    "sell",
    "hold",
    "price target",
    "allocation recommendation",
)


class MockResearchProvider:
    """Creates deterministic internal research drafts for local development."""

    provider_name = "mock"

    def generate_draft(self, evidence_package: dict[str, Any]) -> str:
        fund = evidence_package["fund"]
        exposures = ", ".join(
            item["name"] for item in evidence_package["exposures"]
        )
        risks = ", ".join(item["name"] for item in evidence_package["risks"])
        events = ", ".join(item["name"] for item in evidence_package["events"])
        sources = "\n".join(
            f"- {item['name']}" for item in evidence_package["documents"]
        )

        return f"""# Draft Internal Research Brief — {fund["name"]}

## Scope

This is a synthetic portfolio demonstration draft for internal research preparation only.
It is not investment advice and does not support a buy, sell, hold, allocation,
or price-target recommendation.

## Fund Summary

- Strategy: {fund["strategy"]}
- Primary region: {fund["primary_region"]}
- Description: {fund["description"]}

## Synthetic Exposure Profile

{exposures}

## Documented Risks

{risks}

## Relevant Market-Event Scenarios

{events}

## Evidence Sources

{sources}

## Analyst Review Required

This draft was generated from a controlled synthetic evidence package.
A qualified human reviewer must verify the evidence, interpretation, completeness,
and appropriate use before this draft can be relied upon.
"""