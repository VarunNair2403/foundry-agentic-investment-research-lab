from src.workflow.research_workflow import ResearchWorkflow


result = ResearchWorkflow.with_foundry().run("Horizon Growth Fund")

print("Provider:", result["provider"])
print("Fund:", result["fund_name"])
print("Validation passed:", result["validation"]["passed"])
print("Review status:", result["review_status"])
print("\n--- Draft ---\n")
print(result["draft"])

if not result["validation"]["passed"]:
    print("\n--- Validation details ---\n")
    print(result["validation"])