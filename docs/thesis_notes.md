# Thesis Notes

Research question:

> How can AI agents be used to automate knowledge-intensive work processes in the financial sector, and what governance mechanisms are necessary to ensure responsible and value-creating use?

This prototype is a Design Science Research artifact. It translates the research question into a working system that can be demonstrated, tested, and improved through iteration.

## AI Agents

The prototype demonstrates agentic behavior through:

- Goal interpretation.
- Planning before action.
- Tool use.
- Bounded execution.
- Governance checks.
- Human approval routing.
- Audit logging.

This distinguishes the artifact from a simple chatbot. The agent does not only respond with text; it follows a structured workflow and exposes its intermediate actions.

## Knowledge-Intensive Work

Financial advisory work often involves interpreting incomplete information, comparing data sources, identifying risks, and forming hypotheses. These tasks are knowledge-intensive because they require judgment, context, and accountability.

The prototype models this by asking the agent to:

- Read customer context.
- Analyze aggregated indicators.
- Compare with benchmarks.
- Identify possible advisory hypotheses.
- State when more organizational context is needed.

## Financial Advisory Context

The prototype is framed around advisory support in a financial-sector setting. The example scenario uses synthetic health, claims, absence, and benchmark data to generate an advisory brief.

The agent's role is not to replace the advisor. Its role is to support preparation, structure analysis, surface hypotheses, and make governance constraints visible before advice becomes customer-facing.

## Governance

Governance is implemented as explicit policy rules in `governance/policy.yaml`. The policy defines what the agent may do, what it may not do, and when it must stop for human approval.

Important governance mechanisms include:

- Aggregated data only.
- No personally identifiable information.
- No customer contact.
- No final strategic recommendation without approval.
- Data quality checks.
- Stakeholder input when organizational context is missing.
- Audit logging of tool calls and decisions.

## Responsible AI

The prototype demonstrates responsible AI principles through:

- Transparency: the UI shows the goal, plan, tool calls, governance checks, and final brief.
- Accountability: each run produces an audit trail.
- Human oversight: risky or incomplete outputs require human approval.
- Privacy: the system uses synthetic aggregated data only.
- Bounded autonomy: the agent can analyze and hypothesize, but it cannot take external action.

## Design Science Research

The artifact supports Design Science Research by providing something concrete to build and evaluate.

Possible evaluation activities:

- Scenario walkthroughs with synthetic customer cases.
- Tests of governance blocking behavior.
- Review of audit trail completeness.
- Advisor feedback on usefulness and interpretability.
- Governance stakeholder feedback on policy clarity and control.

The research contribution is not only the code. It is the design knowledge gained from building an agent that can create value in advisory work while remaining bounded, inspectable, and accountable.

## Current Scope

Included:

- Streamlit app.
- Synthetic local data.
- Deterministic placeholder hypothesis generation.
- YAML governance policy.
- JSONL audit trail.
- Basic tests.

Not included:

- Real customer data.
- Real employee or claims data.
- External customer contact.
- Autonomous recommendations.
- Production authentication or deployment hardening.

## Next Research Iterations

Useful next steps:

- Add a human review screen where advisors can approve, reject, or revise the brief.
- Store approval decisions in the audit trail.
- Add more scenario cases for different governance outcomes.
- Introduce a replaceable LLM provider behind the existing wrapper.
- Evaluate the artifact with domain experts using a structured feedback protocol.
