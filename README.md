# AI Advisor Agent

AI Advisor Agent is a thesis prototype of a governed AI agent that supports a financial advisor working with a strategic B2B customer. The prototype models a full advisory journey from early signal detection to governed simulated follow-up action.

The app is not a chatbot. It demonstrates an agent that receives a goal, creates a plan, uses tools, traces data provenance, detects missing context, asks for human input, applies governance policy, prepares bounded actions, requests approval, and writes an audit trail.

All data is synthetic and for thesis demonstration only. The repository must not be used with real customer, employee, health, claims, insurance, PFA, or personal data.

## Thesis Context

Research question:

> How can AI agents be used to automate knowledge-intensive work processes in the financial sector, and what governance mechanisms are necessary to ensure responsible and value-creating use?

The prototype supports a Design Science Research thesis by making the research argument visible in a working artifact: AI agents can support advisory work only when embedded in transparent workflows, human decision points, data provenance, governance mechanisms, and auditability.

## Work Process Represented

A financial advisor receives a signal that a customer may have an emerging health, insurance, or wellbeing issue. The signal may come from:

- Customer-facing chatbot
- Advisory center conversation
- Incident report
- Claims data
- Absence data
- Previous customer meeting
- Benchmark deviation

The advisor uses the AI Advisor Agent to understand the signal, trace data sources, analyze aggregated data, identify hypotheses, detect missing business context, ask for human input, decide whether stakeholders should be contacted, draft a brief, run governance checks, prepare simulated actions, and log the process.

## Default Demo Scenario

- Customer: `Novo Nordisk`
- Signal source: `Advisory center conversation`
- Signal: increasing stress-related inquiries among employees
- Supporting evidence: aggregated claims trend, advisory center notes, benchmark comparison, previous meeting note
- Missing context: existing HR initiatives, ongoing reorganization, HR appetite for proactive intervention

The agent concludes that there may be an emerging wellbeing issue, but the data is not sufficient for a final recommendation. HR input is required. The app can prepare a simulated HR email draft, but no real email is sent and approval is required.

## App Structure

```text
app/
  main.py
  pages/
    1_Dashboard.py
    2_Workflow.py
    3_Audit_Log.py
  agent.py
  tools.py
  governance.py
  audit.py
  ui_components.py
  data_loader.py
  prompts.py

data/
  customers.csv
  signals.csv
  claims_data.csv
  benchmark_data.csv
  stakeholder_directory.csv
  previous_meetings.csv
  advisory_center_notes.csv
  chatbot_interactions.csv
  incident_reports.csv

governance/
  policy.yaml

docs/
  architecture.md
  thesis_notes.md
  workflow_design.md
```

## Governance Model

Green actions are allowed:

- Analyze aggregated data
- Summarize approved internal context
- Generate draft hypotheses

Yellow actions require approval:

- Generate final advisory recommendation
- Prepare stakeholder email
- Create customer-facing material
- Escalate risk
- Use sensitive business context

Red actions are blocked:

- Send real external emails
- Process personally identifiable information
- Make final decisions autonomously
- Contact customer directly
- Change customer strategy

## Run Locally

```bash
cd advisor-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```

Open the local URL shown by Streamlit, usually:

```text
http://127.0.0.1:8501
```

## Deploy On Streamlit Cloud

Use:

```text
Repository: zakariashoskin/AI_Governance_Agent
Branch: main
Main file path: app/main.py
```

The repository includes `runtime.txt` and minimal production dependencies in `requirements.txt`.

## Tests

```bash
PYTHONPATH=. pytest
```

The tests verify governance decisions, tool behavior, missing-context detection, workflow execution, simulated action preparation, and blocked actions.
