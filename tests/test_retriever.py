import pytest

from src.graph.retriever import GraphRetriever


@pytest.fixture
def retriever() -> GraphRetriever:
    return GraphRetriever()


def test_horizon_growth_evidence_package(retriever: GraphRetriever) -> None:
    package = retriever.get_evidence_package("Horizon Growth Fund")

    assert package["fund"]["id"] == "fund_horizon_growth"

    exposure_names = {item["name"] for item in package["exposures"]}
    assert exposure_names == {"Technology", "Healthcare"}

    risk_names = {item["name"] for item in package["risks"]}
    assert risk_names == {
        "Technology Concentration Risk",
        "Interest-Rate Sensitivity Risk",
    }

    event_names = {item["name"] for item in package["events"]}
    assert event_names == {
        "Hypothetical Rate-Increase Scenario",
        "Hypothetical Trade-Restriction Scenario",
    }

    document_names = {item["name"] for item in package["documents"]}
    assert "Horizon Growth Fund Profile" in document_names
    assert "Horizon Growth Outlook Note" in document_names
    assert "Technology Concentration Risk Note" in document_names
    assert "Interest-Rate Sensitivity Risk Note" in document_names
    assert "Rate-Increase Scenario Brief" in document_names
    assert "Trade-Restriction Scenario Brief" in document_names


def test_fund_lookup_ignores_case_and_extra_spaces(
    retriever: GraphRetriever,
) -> None:
    package = retriever.get_evidence_package("  horizon growth fund  ")

    assert package["fund"]["name"] == "Horizon Growth Fund"


def test_unknown_fund_returns_clear_error(retriever: GraphRetriever) -> None:
    with pytest.raises(ValueError, match="Unknown fund"):
        retriever.get_evidence_package("Imaginary Fund")