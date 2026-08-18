from src.workflow.research_workflow import ResearchWorkflow


if __name__ == "__main__":
    workflow = ResearchWorkflow()
    result = workflow.run("Horizon Growth Fund")

    print(f"Request ID: {result['request_id']}")
    print(f"Provider: {result['provider']}")
    print(f"Review status: {result['review_status']}")
    print(f"Validation passed: {result['validation']['passed']}")
    print()
    print(result["draft"])