from src.graph.retriever import GraphRetriever
from src.providers.foundry_provider import FoundryResearchProvider
from src.validators.draft_validator import validate_draft


fund_name = "Horizon Growth Fund"

package = GraphRetriever().get_evidence_package(fund_name)
provider = FoundryResearchProvider()

draft = provider.generate_draft(package)
validation = validate_draft(draft, package)

print("Provider:", provider.provider_name)
print("Fund:", fund_name)
print("Validation passed:", validation["passed"])
print("Review status: PENDING_HUMAN_REVIEW")
print("\n--- Draft ---\n")
print(draft)

if not validation["passed"]:
    print("\n--- Validation details ---\n")
    print(validation)
    