# AI Advisor Agent

AI Advisor Agent is a thesis prototype that demonstrates how an AI agent can support knowledge-intensive advisory work in the financial sector while operating under explicit governance rules.

The prototype is intentionally small and readable. It is not a generic chatbot. It shows an agent that interprets a goal, creates a plan, uses bounded tools, checks governance policy, requests human approval when needed, and writes an audit trail.

All data in this repository is synthetic. The project must not be used with real customer, employee, health, claims, or personally identifiable data.

## Thesis Context

The prototype supports the research question:

> How can AI agents be used to automate knowledge-intensive work processes in the financial sector, and what governance mechanisms are necessary to ensure responsible and value-creating use?

The artifact is designed for a Design Science Research thesis. It makes abstract concepts such as agentic behavior, governance, human oversight, and auditability concrete enough to demonstrate, test, and discuss with stakeholders.

## What The App Demonstrates

- A user selects a synthetic customer, such as `Example Pharma`.
- The agent interprets the advisory goal.
- The agent writes a short plan before using tools.
- The agent calls bounded tools for data retrieval, analysis, benchmarking, quality checks, hypothesis generation, governance, and approval routing.
- The governance layer blocks or gates risky outputs.
- The final brief explicitly identifies missing organizational context.
- Each run is appended to a local JSONL audit log.

## Architecture

```text
advisor-agent/
  app/
    main.py          Streamlit UI
    agent.py         Agent orchestration and planning
    tools.py         Bounded tool functions
    governance.py    Governance policy evaluation
    audit.py         JSONL audit logging
    prompts.py       Replaceable LLM wrapper
  data/              Synthetic CSV data only
  governance/
    policy.yaml      Human-readable policy rules
  docs/
    architecture.md
    thesis_notes.md
  tests/
    test_governance.py
    test_tools.py
```

Core workflow:

1. Interpret the user request as an advisory goal.
2. Create a 3-5 step plan before tool use.
3. Retrieve synthetic customer context.
4. Analyze aggregated claims and absence data.
5. Compare the customer with synthetic benchmark data.
6. Assess data quality.
7. Generate advisory hypotheses.
8. Check governance policy.
9. Request human approval if policy requires it.
10. Produce the advisory brief and audit log entry.

## Agent Tools

The current agent tools are:

- `get_customer_context()`
- `analyze_claims_data()`
- `compare_to_benchmark()`
- `assess_data_quality()`
- `generate_advisory_hypotheses()`
- `check_governance_policy()`
- `request_human_approval()`

These tools are local and bounded. They do not contact customers, send messages, access external systems, or process personal data.

## Governance

The policy in `governance/policy.yaml` includes rules such as:

- The agent may analyze aggregated data.
- The agent may generate advisory hypotheses.
- The agent may not process personally identifiable information.
- The agent may not contact customers.
- The agent may not make final strategic recommendations without human approval.
- The agent must request human validation when data quality is insufficient.
- The agent must request stakeholder input when organizational context is missing.
- The agent must log all tool calls and governance decisions.

## Setup

```bash
cd advisor-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

Open the local Streamlit URL shown in the terminal.

If local port permissions are strict, this form can be more reliable:

```bash
streamlit run app/main.py --server.address 127.0.0.1 --server.port 8501
```

## Environment Variables

Copy `.env.example` to `.env` if you later add a real LLM provider:

```bash
cp .env.example .env
```

The current MVP works without an API key because it uses deterministic placeholder generation.

## Example Workflow

1. Start the Streamlit app.
2. Select `Example Pharma`.
3. Keep the default request: `Generate an advisory brief based on aggregated claims, absence, and benchmark data.`
4. Click `Generate advisory brief`.
5. Review the visible agent goal, plan, tool calls, governance checks, and final advisory brief.
6. Notice that the agent requests human approval when policy rules are triggered.
7. Inspect `audit_logs/agent_audit.jsonl` locally to see the structured audit record.

## Tests

```bash
cd advisor-agent
PYTHONPATH=. pytest
```

The tests verify tool behavior and governance blocking for prohibited actions such as PII, non-aggregated data, and external customer actions.

## Design Science Research Relevance

This repository is the first functional artifact for the thesis. It can be evaluated through scenario walkthroughs, governance rule tests, and feedback from advisors or governance stakeholders.

Useful evaluation questions:

- Does the agent behave differently from a chatbot?
- Are tool calls and decisions understandable to a human reviewer?
- Does the governance layer block prohibited behavior?
- Does the agent clearly identify missing organizational context?
- Is the audit trail sufficient for accountability?

## Data And Privacy

This project contains mock data only. Do not commit real company data, personal data, secrets, `.env` files, generated logs, or local cache files.
