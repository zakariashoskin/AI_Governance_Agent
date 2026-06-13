# Architecture

The upgraded prototype is a multipage Streamlit application backed by a small governed agent runtime. It is designed to be explainable in a master thesis rather than optimized for production scale.

## Components

- `app/main.py`: dashboard home and workflow start.
- `app/pages/2_Workflow.py`: step-by-step advisor journey.
- `app/pages/3_Audit_Log.py`: thesis-friendly audit log.
- `app/agent.py`: agent orchestration and workflow state transitions.
- `app/tools.py`: bounded tools for provenance, context, analysis, hypotheses, brief drafting, and simulated action preparation.
- `app/governance.py`: policy engine returning allowed, requires approval, or blocked.
- `app/audit.py`: JSONL audit logging.
- `app/data_loader.py`: synthetic CSV loading.
- `app/ui_components.py`: reusable cards, status badges, and status messages.

## Agent Workflow

1. Receive advisor goal and selected signal source.
2. Create a plan before tool use.
3. Retrieve the selected signal.
4. Trace data provenance.
5. Retrieve customer context.
6. Analyze aggregated claims and absence data.
7. Compare findings with benchmark data.
8. Detect missing business context.
9. Ask the advisor for human input.
10. Generate advisory hypotheses.
11. Draft an advisory brief.
12. Run governance checks.
13. Prepare simulated stakeholder action.
14. Request approval.
15. Append audit entry.

## Tools

The agent uses explicit bounded tools:

- `get_customer_context`
- `get_signal`
- `trace_data_provenance`
- `analyze_claims_data`
- `compare_to_benchmark`
- `assess_data_quality`
- `detect_missing_context`
- `generate_advisory_hypotheses`
- `draft_advisory_brief`
- `prepare_stakeholder_action`
- `check_governance_policy`
- `request_human_approval`

None of the tools send real emails, contact customers, process personal data, or perform external side effects.

## Governance Layer

The governance layer loads `governance/policy.yaml`. Each action returns:

- `decision`: `allowed`, `requires_approval`, or `blocked`
- `triggered_rules`
- `explanation`
- `required_human_role`
- `next_step`

This makes governance visible as part of the workflow, not an invisible post-processing step.

## Audit Trail

Each workflow state change appends a JSONL record with:

- timestamp
- user request
- customer
- signal source
- agent plan
- tool calls
- data sources used
- human inputs added
- governance checks
- approvals requested
- approvals granted or denied
- blocked actions
- prepared actions
- final output
- raw workflow state

## Human-In-The-Loop Logic

The agent pauses when business context is missing. The advisor can add context in the UI. The workflow is rerun with the new context, updating hypotheses and the advisory brief. Stakeholder actions are drafts only and require explicit simulated approval.
