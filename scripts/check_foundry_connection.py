from dotenv import load_dotenv

from src.providers.foundry_provider import FoundryResearchProvider

load_dotenv()

provider = FoundryResearchProvider()

response = provider._client.responses.create(
    model=provider._deployment_name,
    input="Reply with exactly: Foundry connection successful.",
)

print(response.output_text)