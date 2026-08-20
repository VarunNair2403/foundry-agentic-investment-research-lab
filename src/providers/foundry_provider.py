from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


class FoundryResearchProvider:
    """Generates bounded internal research drafts through Azure AI Foundry."""

    provider_name = "azure_ai_foundry"

    def __init__(self) -> None:
        load_dotenv()

        responses_endpoint = os.getenv("AZURE_AI_ENDPOINT", "").rstrip("/")
        api_key = os.getenv("AZURE_AI_API_KEY", "")
        deployment_name = os.getenv("AZURE_AI_DEPLOYMENT_NAME", "")

        if not responses_endpoint:
            raise ValueError("AZURE_AI_ENDPOINT is required.")
        if not api_key:
            raise ValueError("AZURE_AI_API_KEY is required.")
        if not deployment_name:
            raise ValueError("AZURE_AI_DEPLOYMENT_NAME is required.")

        if not responses_endpoint.endswith("/openai/v1/responses"):
            raise ValueError(
                "AZURE_AI_ENDPOINT must end with '/openai/v1/responses'."
            )

        base_url = f"{responses_endpoint.rsplit('/responses', 1)[0]}/"

        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self._deployment_name = deployment_name

    def generate_draft(self, evidence_package: dict[str, Any]) -> str:
        response = self._client.responses.create(
            model=self._deployment_name,
            instructions=(
                            "Create a Markdown internal research-preparation draft using only the "
                            "supplied synthetic evidence package. Do not introduce facts that are "
                            "not in that package. Do not make investment recommendations or use "
                            "buy, sell, hold, allocation, suitability, or price-target language "
                            "anywhere except in the exact required disclaimer below. Use exactly "
                            "these Markdown section headings, spelled and capitalized exactly as "
                            "shown, in this exact order:\n\n"
                            "## Scope\n"
                            "## Fund Summary\n"
                            "## Synthetic Exposure Profile\n"
                            "## Documented Risks\n"
                            "## Relevant Market-Event Scenarios\n"
                            "## Evidence Sources\n"
                            "## Analyst Review Required\n\n"
                            "Under ## Evidence Sources, include the exact name of every provided "
                            "source document. Include this exact sentence once and only once, "
                            "inside ## Scope:\n"
                            "It is not investment advice and does not support a buy, sell, hold, "
                            "allocation, or price-target recommendation.\n\n"
                            "In ## Analyst Review Required, state that qualified human review is "
                            "required before the draft can be relied upon. Do not add any section "
                            "headings other than the required headings."
            ),
            input=(
                "Create a concise Markdown internal research brief from this "
                "controlled evidence package:\n\n"
                f"{evidence_package}"
            ),
        )

        if not response.output_text:
            raise RuntimeError("Foundry returned an empty draft.")

        return response.output_text