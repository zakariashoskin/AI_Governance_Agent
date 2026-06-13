# Workflow Design

This prototype models an employee journey for a financial advisor working with a strategic B2B customer. The advisor receives a signal, asks the AI Advisor Agent to investigate, reviews the agent's tool use and governance checks, adds missing business context, and approves or rejects simulated follow-up actions.

## Work Process

1. A signal is received from a source such as an advisory center conversation, chatbot, claims data, absence data, incident report, benchmark deviation, or previous customer meeting.
2. The agent identifies where the signal came from and whether the data is approved for use.
3. The agent retrieves synthetic customer context.
4. The agent analyzes aggregated claims and benchmark data.
5. The agent generates advisory hypotheses.
6. The agent detects missing organizational context.
7. The advisor adds human context.
8. The agent updates the brief and governance status.
9. The advisor prepares a simulated stakeholder action.
10. The action requires explicit approval before it is marked as simulated execution.
11. The full process is logged.

## Why This Is Knowledge-Intensive Work

The advisor must interpret weak signals, assess data provenance, compare multiple evidence sources, understand customer context, and decide whether action is appropriate. The work depends on judgment and accountability, not only information retrieval.

## Human-In-The-Loop Design

The agent pauses when business context is missing. It asks the advisor for context such as existing HR initiatives, reorganizations, or ongoing investigations. The agent can update its hypotheses after human input, but final recommendations and stakeholder actions require approval.

## Governance Design

The governance layer separates actions into:

- Allowed: aggregated analysis, approved-document summaries, draft hypotheses.
- Requires approval: final recommendations, stakeholder emails, customer-facing material, risk escalation, sensitive business context.
- Blocked: real external emails, PII processing, autonomous final decisions, direct customer contact, changing customer strategy.

## Data Provenance

Each insight shows source type, source name, timestamp, confidence level, data structure, aggregation status, sensitivity status, and whether it is approved for agent use. This makes the agent's evidence base inspectable.

## Thesis Relevance

The workflow demonstrates that AI agents can support financial advisory work only when embedded in transparent processes with governance, auditability, human decision points, and clear data provenance.
