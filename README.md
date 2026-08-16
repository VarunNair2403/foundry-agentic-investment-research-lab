# Foundry Agentic Investment Research Lab

A Foundry-centered, human-approved agentic research workflow that uses a synthetic investment knowledge graph to generate traceable internal research briefs.

## Business problem

An asset-management analyst preparing a first-pass fund research brief may need to combine information from fund profiles, exposures, risk records, market-event notes, and research documents. This project demonstrates how a bounded AI workflow can automate research preparation while preserving human judgment, source traceability, and auditability.

## What the workflow does

1. Accepts a structured internal research request.
2. Identifies the requested fund and research topics.
3. Traverses a synthetic knowledge graph of funds, sectors, risks, market events, and source documents.
4. Builds a controlled evidence package from approved synthetic sources.
5. Produces a structured internal research draft.
6. Runs quality, grounding, and policy checks.
7. Routes every output to a human reviewer.
8. Records an audit trail of sources, tool actions, validation outcomes, model/provider, and review status.

## Boundaries

This project:

- Uses synthetic data only.
- Produces internal research drafts, not investment advice.
- Does not generate buy, sell, hold, allocation, suitability, or price-target recommendations.
- Does not execute trades, change source data, or take external actions.
- Requires qualified human review before any output can be used.
- Clearly distinguishes live integrations from mocked or documented integration patterns.

## Technology focus

- **Primary AI platform:** Azure AI Foundry
- **Knowledge layer:** Synthetic graph data with source-backed relationships
- **Data integration pattern:** Snowflake Cortex
- **Alternative model-provider pattern:** Amazon Bedrock
- **Local implementation:** Python
- **Version control and automation:** GitHub and GitHub Actions

## Repository structure

| Path | Purpose |
|---|---|
| `src/graph/` | Knowledge-graph loading, traversal, and evidence assembly |
| `src/workflow/` | Bounded research-preparation workflow |
| `src/providers/` | Mock, Foundry, and optional Bedrock provider adapters |
| `src/validators/` | Grounding, structure, and policy checks |
| `src/audit/` | Audit-record creation and storage interfaces |
| `data/documents/` | Synthetic source documents |
| `data/graph/` | Synthetic nodes and source-backed relationships |
| `evals/` | Evaluation datasets, expected results, and reports |
| `docs/` | Architecture, decisions, and learning notes |
| `infra/` | Azure deployment configuration, added later |
| `launch/` | Readiness checklist, risk log, rollout, rollback, and incident plan |
| `tests/` | Automated unit and workflow tests |

## Delivery phases

1. Build the synthetic investment-research knowledge graph.
2. Implement and test deterministic graph traversal locally.
3. Build a bounded local agent workflow using a mock model provider.
4. Integrate a low-cost Azure AI Foundry model.
5. Add evaluations, policy checks, tracing, and auditability.
6. Document Snowflake Cortex and Amazon Bedrock integration patterns.
7. Package launch-readiness artifacts and an interview demo.

## Status

- **Current phase:** Project foundation
- **Live Azure AI Foundry integration:** Not started
- **Data classification:** Synthetic only
- **Human review:** Required for every research draft