from src.graph.retriever import GraphRetriever
from src.providers.mock_provider import MockResearchProvider
from src.validators.draft_validator import validate_draft
from src.workflow.research_workflow import ResearchWorkflow


def test_workflow_returns_valid_human_review_draft() -> None:
    result = ResearchWorkflow().run("Horizon Growth Fund")

    assert result["provider"] == "mock"
    assert result["fund_name"] == "Horizon Growth Fund"
    assert result["validation"]["passed"] is True
    assert result["review_status"] == "PENDING_HUMAN_REVIEW"
    assert result["allowed_actions"] == [
        "APPROVE",
        "REJECT",
        "REQUEST_REVISION",
    ]
    assert "Horizon Growth Fund" in result["draft"]


def test_validator_rejects_unsupported_recommendation_language() -> None:
    package = GraphRetriever().get_evidence_package("Horizon Growth Fund")
    safe_draft = MockResearchProvider().generate_draft(package)

    unsafe_draft = safe_draft.replace(
        "## Analyst Review Required",
        "## Recommendation\n\nBuy Horizon Growth Fund.\n\n"
        "## Analyst Review Required",
    )

    result = validate_draft(unsafe_draft, package)

    assert result["passed"] is False
    assert result["checks"]["no_unsupported_recommendation_language"] is False
    assert "buy" in result["details"]["prohibited_terms_found"]


def test_validator_rejects_missing_disclaimer() -> None:
    package = GraphRetriever().get_evidence_package("Horizon Growth Fund")
    safe_draft = MockResearchProvider().generate_draft(package)

    draft_without_disclaimer = safe_draft.replace(
        "It is not investment advice and does not support a buy, sell, hold, "
        "allocation,\nor price-target recommendation.\n",
        "",
    )

    result = validate_draft(draft_without_disclaimer, package)

    assert result["passed"] is False
    assert result["checks"]["approved_disclaimer_present_once"] is False
    assert result["details"]["approved_disclaimer_count"] == 0

def test_workflow_uses_mock_provider_by_default() -> None:
    workflow = ResearchWorkflow()

    assert workflow.provider.provider_name == "mock"