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

def test_workflow_writes_expected_trace_events(
    tmp_path,
) -> None:
    import json

    workflow = ResearchWorkflow(trace_directory=tmp_path)
    result = workflow.run("Horizon Growth Fund")

    trace_path = tmp_path / f"{result['request_id']}.jsonl"
    trace_events = [
        json.loads(line)
        for line in trace_path.read_text().splitlines()
    ]

    assert [event["event_name"] for event in trace_events] == [
        "RETRIEVAL_STARTED",
        "RETRIEVAL_COMPLETED",
        "DRAFT_GENERATION_STARTED",
        "DRAFT_GENERATION_COMPLETED",
        "VALIDATION_COMPLETED",
    ]
    assert all(event["request_id"] == result["request_id"] for event in trace_events)
    assert trace_events[-1]["status"] == "SUCCESS"
    assert trace_events[-1]["metadata"]["validation_passed"] is True


def test_workflow_traces_and_reraises_retrieval_failure(tmp_path) -> None:
    class FailingRetriever:
        def get_evidence_package(self, fund_name: str) -> dict:
            raise RuntimeError("Synthetic retrieval failure")

    workflow = ResearchWorkflow(
        retriever=FailingRetriever(),
        trace_directory=tmp_path,
    )

    try:
        workflow.run("Horizon Growth Fund")
    except RuntimeError as error:
        assert str(error) == "Synthetic retrieval failure"
    else:
        raise AssertionError("Expected retrieval failure to be re-raised")

    trace_paths = list(tmp_path.glob("REQ-*.jsonl"))
    assert len(trace_paths) == 1

    import json

    trace_events = [
        json.loads(line)
        for line in trace_paths[0].read_text().splitlines()
    ]

    assert [event["event_name"] for event in trace_events] == [
        "RETRIEVAL_STARTED",
        "RETRIEVAL_FAILED",
    ]
    assert trace_events[-1]["status"] == "FAILED"
    assert trace_events[-1]["metadata"] == {
        "error_type": "RuntimeError",
        "error_message": "Synthetic retrieval failure",
    }


def test_workflow_traces_and_reraises_draft_generation_failure(
    tmp_path,
) -> None:
    class FailingProvider:
        provider_name = "failing-provider"

        def generate_draft(self, evidence_package: dict) -> str:
            raise RuntimeError("Synthetic draft generation failure")

    workflow = ResearchWorkflow(
        provider=FailingProvider(),
        trace_directory=tmp_path,
    )

    try:
        workflow.run("Horizon Growth Fund")
    except RuntimeError as error:
        assert str(error) == "Synthetic draft generation failure"
    else:
        raise AssertionError("Expected draft generation failure to be re-raised")

    trace_paths = list(tmp_path.glob("REQ-*.jsonl"))
    assert len(trace_paths) == 1

    import json

    trace_events = [
        json.loads(line)
        for line in trace_paths[0].read_text().splitlines()
    ]

    assert [event["event_name"] for event in trace_events] == [
        "RETRIEVAL_STARTED",
        "RETRIEVAL_COMPLETED",
        "DRAFT_GENERATION_STARTED",
        "DRAFT_GENERATION_FAILED",
    ]
    assert trace_events[-1]["status"] == "FAILED"
    assert trace_events[-1]["metadata"] == {
        "error_type": "RuntimeError",
        "error_message": "Synthetic draft generation failure",
    }


def test_workflow_traces_and_reraises_validation_failure(
    tmp_path,
    monkeypatch,
) -> None:
    import json
    import src.workflow.research_workflow as workflow_module

    def failing_validate_draft(
        draft: str,
        evidence_package: dict,
    ) -> dict:
        raise RuntimeError("Synthetic validation failure")

    monkeypatch.setattr(
        workflow_module,
        "validate_draft",
        failing_validate_draft,
    )

    workflow = ResearchWorkflow(trace_directory=tmp_path)

    try:
        workflow.run("Horizon Growth Fund")
    except RuntimeError as error:
        assert str(error) == "Synthetic validation failure"
    else:
        raise AssertionError("Expected validation failure to be re-raised")

    trace_paths = list(tmp_path.glob("REQ-*.jsonl"))
    assert len(trace_paths) == 1

    trace_events = [
        json.loads(line)
        for line in trace_paths[0].read_text().splitlines()
    ]

    assert [event["event_name"] for event in trace_events] == [
        "RETRIEVAL_STARTED",
        "RETRIEVAL_COMPLETED",
        "DRAFT_GENERATION_STARTED",
        "DRAFT_GENERATION_COMPLETED",
        "VALIDATION_FAILED",
    ]
    assert trace_events[-1]["status"] == "FAILED"
    assert trace_events[-1]["metadata"] == {
        "error_type": "RuntimeError",
        "error_message": "Synthetic validation failure",
    }
