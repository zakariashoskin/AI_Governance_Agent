# Architecture

This document explains how the AI Advisor Agent MVP is structured and how the main runtime flow works.

## Overview

The app is a small Streamlit prototype with a modular Python backend. The design goal is readability: each file maps to one thesis-relevant concern.

- `app/main.py`: Streamlit user interface.
- `app/agent.py`: Agent workflow, planning, tool orchestration, and final brief construction.
- `app/tools.py`: Bounded tool functions the agent is allowed to call.
- `app/governance.py`: YAML policy loading and governance checks.
- `app/audit.py`: Local JSONL audit logging.
- `app/prompts.py`: Replaceable placeholder LLM layer.
- `governance/policy.yaml`: Human-readable governance policy.
- `data/*.csv`: Synthetic aggregated sample data.

## Agent Workflow

The agent follows a fixed, inspectable workflow:

1. Interpret the user's request as an advisory goal.
2. Write a short plan before using tools.
3. Retrieve customer context from synthetic data.
4. Analyze aggregated claims and absence indicators.
5. Compare the customer metrics with synthetic benchmark data.
6. Assess data quality.
7. Generate advisory hypotheses.
8. Check governance policy.
9. Request human approval when governance rules require it.
10. Produce the final advisory brief and append an audit log entry.

The workflow is deliberately bounded. The agent does not browse the web, contact customers, send emails, access external systems, or process personal data.

## Tools

The tool layer is implemented in `app/tools.py`.

- `get_customer_context()`: Loads synthetic customer metadata.
- `analyze_claims_data()`: Summarizes aggregated claims, absence, and health-related indicators.
- `compare_to_benchmark()`: Compares customer metrics with synthetic industry benchmarks.
- `assess_data_quality()`: Determines whether the available data is strong enough for advisory use.
- `generate_advisory_hypotheses()`: Produces hypotheses without making final recommendations.
- `check_governance_policy()`: Evaluates the proposed output against governance rules.
- `request_human_approval()`: Creates a clear approval status when policy requires human oversight.

Each tool call is captured in the UI and audit trail.

## Governance Layer

The governance layer is policy-based. Rules are stored in `governance/policy.yaml` and evaluated by `app/governance.py`.

The current policy covers:

- Aggregated data only.
- No personally identifiable information.
- No customer contact or external actions.
- No final strategic recommendations without human approval.
- Human validation when data quality is insufficient.
- Stakeholder input when organizational context is missing.
- Logging of tool calls and governance decisions.

Governance output includes:

- Whether direct display is allowed.
- Whether human approval is required.
- Which policy rules were triggered.
- The reason each rule was triggered.

## Audit Trail

Each agent run is appended as one JSON object to:

```text
audit_logs/agent_audit.jsonl
```

The audit record includes:

- Run ID.
- Timestamp.
- User request.
- Selected customer.
- Agent plan.
- Tool calls.
- Data sources used.
- Governance rules triggered.
- Human approval status.
- Final output summary.

Generated audit logs are ignored by git because they are local runtime artifacts.

## Human-In-The-Loop Logic

The prototype treats the agent as an advisory support system, not an autonomous decision-maker.

Human approval is required when:

- The agent would move from hypotheses to final strategic recommendations.
- Data quality is below the configured threshold.
- Organizational context is missing.
- A prohibited action is detected, such as PII processing or external customer contact.

This supports a responsible AI design pattern: the agent can accelerate analysis, but accountability remains with a human advisor.

## Deployment Note

For Streamlit Community Cloud, the app entry point is:

```text
app/main.py
```

The repository should include source files, synthetic data, governance policy, docs, tests, `requirements.txt`, `.gitignore`, and `.env.example`. It should not include `.env`, virtual environments, logs, cache folders, or real data.
