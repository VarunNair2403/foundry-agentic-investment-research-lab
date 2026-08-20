from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from src.graph.retriever import GraphRetriever
from src.providers.foundry_provider import FoundryResearchProvider
from src.providers.mock_provider import MockResearchProvider
from src.validators.draft_validator import validate_draft


class ResearchProvider(Protocol):
    """Minimal interface required by the research workflow."""

    provider_name: str

    def generate_draft(self, evidence_package: dict[str, Any]) -> str:
        """Return a draft grounded in the supplied evidence package."""


class ResearchWorkflow:
    """Produces a controlled, human-review-required research draft."""

    def __init__(
        self,
        retriever: GraphRetriever | None = None,
        provider: ResearchProvider | None = None,
    ) -> None:
        self.retriever = retriever or GraphRetriever()
        self.provider = provider or MockResearchProvider()

    @classmethod
    def with_foundry(
        cls,
        retriever: GraphRetriever | None = None,
    ) -> ResearchWorkflow:
        """Create an explicit live Foundry workflow."""
        return cls(
            retriever=retriever,
            provider=FoundryResearchProvider(),
        )

    def run(self, fund_name: str) -> dict[str, Any]:
        evidence_package = self.retriever.get_evidence_package(fund_name)
        draft = self.provider.generate_draft(evidence_package)
        validation = validate_draft(draft, evidence_package)

        return {
            "request_id": f"REQ-{uuid4().hex[:8].upper()}",
            "generated_at": datetime.now(UTC).isoformat(),
            "provider": self.provider.provider_name,
            "fund_name": evidence_package["fund"]["name"],
            "evidence_package": evidence_package,
            "draft": draft,
            "validation": validation,
            "review_status": "PENDING_HUMAN_REVIEW",
            "allowed_actions": ["APPROVE", "REJECT", "REQUEST_REVISION"],
        }