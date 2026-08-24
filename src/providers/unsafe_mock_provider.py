from __future__ import annotations

from typing import Any

from src.providers.mock_provider import MockResearchProvider


class UnsafeMockResearchProvider(MockResearchProvider):
    """Test-only provider that injects prohibited recommendation language."""

    provider_name = "unsafe-mock"

    def generate_draft(self, evidence_package: dict[str, Any]) -> str:
        safe_draft = super().generate_draft(evidence_package)

        return safe_draft.replace(
            "## Analyst Review Required",
            "## Recommendation\n\n"
            "Buy Horizon Growth Fund.\n\n"
            "## Analyst Review Required",
        )