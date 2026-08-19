# Local Development

This project is a portfolio demonstration that uses synthetic data only. It does not provide investment advice, execute trades, or require cloud credentials for local development and testing.

## Prerequisites

- Python 3.11 or later
- Git

## Clone the repository

```bash
git clone https://github.com/VarunNair2403/foundry-agentic-investment-research-lab.git
cd foundry-agentic-investment-research-lab
```

## Create and activate a virtual environment

Create the environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Install development dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## Run the test suite

```bash
python -m pytest -v
```

## Run the workflow demo

```bash
python -m src.workflow.demo
```

The local workflow uses a deterministic mock provider. No Azure AI Foundry, Snowflake Cortex, Amazon Bedrock, API credentials, or paid cloud services are used in this setup.
