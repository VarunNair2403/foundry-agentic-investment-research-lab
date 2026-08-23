from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from src.audit import trace_logger
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
        trace_directory: Path | None = None,
    ) -> None:
        self.retriever = retriever or GraphRetriever()
        self.provider = provider or MockResearchProvider()
        self.trace_directory = trace_directory

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

    def _trace(
        self,
        request_id: str,
        event_name: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write one safe local trace event for a workflow request."""
        event = trace_logger.create_trace_event(
            request_id=request_id,
            event_name=event_name,
            status=status,
            metadata=metadata,
        )

        if self.trace_directory is None:
            trace_logger.write_trace_event(event)
        else:
            trace_logger.write_trace_event(
                event,
                trace_directory=self.trace_directory,
            )

    @staticmethod
    def _safe_error_metadata(error: Exception) -> dict[str, str]:
        """Return bounded, non-secret error details for trace events."""
        message = " ".join(str(error).split())

        return {
            "error_type": type(error).__name__,
            "error_message": message[:200],
        }

    def run(self, fund_name: str) -> dict[str, Any]:
        request_id = f"REQ-{uuid4().hex[:8].upper()}"

        self._trace(
            request_id,
            "RETRIEVAL_STARTED",
            "STARTED",
            {"requested_fund_name": fund_name.strip()},
        )
        try:
            evidence_package = self.retriever.get_evidence_package(fund_name)
        except Exception as error:
            self._trace(
                request_id,
                "RETRIEVAL_FAILED",
                "FAILED",
                self._safe_error_metadata(error),
            )
            raise

        self._trace(
            request_id,
            "RETRIEVAL_COMPLETED",
            "SUCCESS",
            {
                "fund_name": evidence_package["fund"]["name"],
                "exposure_count": len(evidence_package["exposures"]),
                "risk_count": len(evidence_package["risks"]),
                "event_count": len(evidence_package["events"]),
                "document_count": len(evidence_package["documents"]),
            },
        )

        self._trace(
            request_id,
            "DRAFT_GENERATION_STARTED",
            "STARTED",
            {"provider": self.provider.provider_name},
        )
        try:
            draft = self.provider.generate_draft(evidence_package)
        except Exception as error:
            self._trace(
                request_id,
                "DRAFT_GENERATION_FAILED",
                "FAILED",
                self._safe_error_metadata(error),
            )
            raise

        self._trace(
            request_id,
            "DRAFT_GENERATION_COMPLETED",
            "SUCCESS",
            {"provider": self.provider.provider_name},
        )

        try:
            validation = validate_draft(draft, evidence_package)
        except Exception as error:
            self._trace(
                request_id,
                "VALIDATION_FAILED",
                "FAILED",
                self._safe_error_metadata(error),
            )
            raise

        self._trace(
            request_id,
            "VALIDATION_COMPLETED",
            "SUCCESS" if validation["passed"] else "FAILED",
            {
                "validation_passed": validation["passed"],
                "failed_checks": [
                    name
                    for name, passed in validation["checks"].items()
                    if not passed
                ],
            },
        )

        return {
            "request_id": request_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "provider": self.provider.provider_name,
            "fund_name": evidence_package["fund"]["name"],
            "evidence_package": evidence_package,
            "draft": draft,
            "validation": validation,
            "review_status": "PENDING_HUMAN_REVIEW",
            "allowed_actions": ["APPROVE", "REJECT", "REQUEST_REVISION"],
        }
