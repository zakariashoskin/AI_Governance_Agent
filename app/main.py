"""Dashboard home for the governed AI Advisor Agent."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import AdvisorWorkflowAgent
from app.data_loader import get_customer_by_name, get_customer_names, get_signal_sources
from app.ui_components import card, inject_css, status_badge


st.set_page_config(page_title="AI Advisor Agent", layout="wide")
inject_css()

st.title("AI Advisor Agent")
st.caption("Governed workflow prototype for strategic B2B financial advisory")

st.markdown(
    """
    This prototype shows how an AI agent can support an advisor after an emerging
    customer signal is detected. The agent plans, uses bounded tools, traces data
    provenance, asks for missing human context, applies governance policy, prepares
    simulated actions, and logs the process for audit.
    """
)

customers = get_customer_names()
default_customer = "Novo Nordisk" if "Novo Nordisk" in customers else customers[0]

left, right = st.columns([1, 1])
with left:
    customer_name = st.selectbox(
        "Strategic customer",
        customers,
        index=customers.index(default_customer),
    )
with right:
    customer = get_customer_by_name(customer_name)
    signal_sources = get_signal_sources(customer["customer_id"])
    signal_source = st.selectbox(
        "Signal source",
        signal_sources,
        index=signal_sources.index("Advisory center conversation")
        if "Advisory center conversation" in signal_sources
        else 0,
    )

user_request = st.text_area(
    "Advisor goal",
    value=(
        "Investigate the signal, identify possible wellbeing risks, determine missing "
        "context, and prepare only governed next steps."
    ),
    height=90,
)

if st.button("Start governed workflow", type="primary"):
    st.session_state.workflow = AdvisorWorkflowAgent().start_workflow(
        customer_name=customer_name,
        signal_source=signal_source,
        user_request=user_request,
    )
    st.success("Workflow started. Open the Workflow page to inspect the agent journey.")

workflow = st.session_state.get("workflow")
status_cols = st.columns(4)
with status_cols[0]:
    card("Current customer", workflow["customer"]["customer_name"] if workflow else customer_name)
with status_cols[1]:
    card("Signal source", workflow["signal"]["signal_source"] if workflow else signal_source)
with status_cols[2]:
    governance_status = (
        workflow["governance_checks"][2]["decision"] if workflow else "pending"
    )
    card("Governance status", status_badge(governance_status))
with status_cols[3]:
    approval_status = (
        workflow["approval_request"]["status"] if workflow else "pending"
    )
    card("Human approval", status_badge(approval_status))

st.divider()
st.subheader("Demo Scenario")
st.write(
    "Default scenario: Novo Nordisk, advisory center conversation, increasing "
    "stress-related inquiries among employees. All data is synthetic and for thesis "
    "demonstration only."
)
