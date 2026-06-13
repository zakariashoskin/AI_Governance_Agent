# Thesis Notes

Research question:

> How can AI agents be used to automate knowledge-intensive work processes in the financial sector, and what governance mechanisms are necessary to ensure responsible and value-creating use?

## AI Agents

The prototype demonstrates agentic behavior through planning, tool use, stateful workflow progression, missing-context detection, human input requests, action preparation, approval gates, and audit logging.

## Knowledge-Intensive Work

The modeled work is knowledge-intensive because the advisor must interpret weak signals, compare evidence sources, understand customer context, judge uncertainty, coordinate stakeholders, and remain accountable for advice.

## Financial Advisory

The default scenario shows a strategic B2B advisory situation where an emerging wellbeing signal may have insurance, health, absence, and customer relationship implications. The agent supports the advisor's preparation, but does not replace human judgment.

## Governance

The governance layer demonstrates that agent autonomy must be bounded. Some actions are allowed, some require approval, and some are blocked. Governance is displayed in the UI so that the advisor can understand why the agent pauses or requests approval.

## Responsible AI

Responsible AI is represented through:

- Synthetic data only.
- Explicit data provenance.
- No PII processing.
- No real external communication.
- Human approval for sensitive or customer-facing actions.
- Transparent audit trail.

## Design Science Research

The artifact can be evaluated through scenario walkthroughs, governance tests, stakeholder feedback, and audit review. The design knowledge contribution is the workflow pattern: AI agents can create value in advisory work when embedded in transparent, governed, human-in-the-loop processes.
