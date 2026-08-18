from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NODES_PATH = PROJECT_ROOT / "data" / "graph" / "nodes.json"
RELATIONSHIPS_PATH = PROJECT_ROOT / "data" / "graph" / "relationships.json"


class GraphRetriever:
    """Retrieves source-backed evidence from the synthetic research graph."""

    def __init__(
        self,
        nodes_path: Path = NODES_PATH,
        relationships_path: Path = RELATIONSHIPS_PATH,
    ) -> None:
        self.nodes = self._load_nodes(nodes_path)
        self.relationships = self._load_relationships(relationships_path)
        self.nodes_by_id = {node["id"]: node for node in self.nodes}
        self.nodes_by_name = {
            node["name"].lower(): node for node in self.nodes
        }

    @staticmethod
    def _load_nodes(path: Path) -> list[dict[str, Any]]:
        return json.loads(path.read_text())["nodes"]

    @staticmethod
    def _load_relationships(path: Path) -> list[dict[str, Any]]:
        return json.loads(path.read_text())["relationships"]

    def find_fund(self, fund_name: str) -> dict[str, Any]:
        fund = self.nodes_by_name.get(fund_name.strip().lower())

        if not fund or fund["type"] != "Fund":
            available_funds = sorted(
                node["name"] for node in self.nodes if node["type"] == "Fund"
            )
            raise ValueError(
                f"Unknown fund: '{fund_name}'. "
                f"Available funds: {', '.join(available_funds)}."
            )

        return fund

    def _outgoing(
        self,
        node_id: str,
        relationship_type: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            relationship
            for relationship in self.relationships
            if relationship["source"] == node_id
            and (
                relationship_type is None
                or relationship["type"] == relationship_type
            )
        ]

    def _nodes_from_relationships(
        self,
        relationships: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [self.nodes_by_id[relationship["target"]] for relationship in relationships]

    @staticmethod
    def _deduplicate_by_id(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        unique_items = {item["id"]: item for item in items}
        return sorted(unique_items.values(), key=lambda item: item["name"])

    def get_evidence_package(self, fund_name: str) -> dict[str, Any]:
        fund = self.find_fund(fund_name)

        exposure_relationships = self._outgoing(
            fund["id"],
            "HAS_EXPOSURE_TO",
        )
        risk_relationships = self._outgoing(fund["id"], "HAS_RISK")
        fund_document_relationships = [
            *self._outgoing(fund["id"], "SUPPORTED_BY"),
            *self._outgoing(fund["id"], "ANALYZED_IN"),
        ]

        exposures = self._nodes_from_relationships(exposure_relationships)
        risks = self._nodes_from_relationships(risk_relationships)
        fund_documents = self._nodes_from_relationships(fund_document_relationships)

        event_relationships = []
        for exposure in exposures:
            event_relationships.extend(
                self._outgoing(exposure["id"], "AFFECTED_BY")
            )

        for risk in risks:
            event_relationships.extend(
                self._outgoing(risk["id"], "AMPLIFIED_BY")
            )

        events = self._deduplicate_by_id(
            self._nodes_from_relationships(event_relationships)
        )

        risk_documents = []
        for risk in risks:
            risk_documents.extend(
                self._nodes_from_relationships(
                    self._outgoing(risk["id"], "DOCUMENTED_IN")
                )
            )

        event_documents = []
        for event in events:
            event_documents.extend(
                self._nodes_from_relationships(
                    self._outgoing(event["id"], "EVENT_DOCUMENTED_IN")
                )
            )

        documents = self._deduplicate_by_id(
            [*fund_documents, *risk_documents, *event_documents]
        )

        return {
            "fund": fund,
            "exposures": self._deduplicate_by_id(exposures),
            "risks": self._deduplicate_by_id(risks),
            "events": events,
            "documents": documents,
        }


def format_evidence_package(package: dict[str, Any]) -> str:
    """Formats a graph evidence package for a human-readable local demo."""

    def bullet_list(items: list[dict[str, Any]]) -> str:
        return "\n".join(f"- {item['name']}" for item in items) or "- None"

    return "\n".join(
        [
            f"Fund: {package['fund']['name']}",
            f"Strategy: {package['fund']['strategy']}",
            "",
            "Exposures:",
            bullet_list(package["exposures"]),
            "",
            "Risks:",
            bullet_list(package["risks"]),
            "",
            "Relevant market events:",
            bullet_list(package["events"]),
            "",
            "Supporting documents:",
            bullet_list(package["documents"]),
        ]
    )