"""Streamlit UI for the AI Advisor Agent MVP."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import AdvisorAgent
from app.tools import DATA_DIR


st.set_page_config(page_title="AI Advisor Agent", layout="wide")


@st.cache_data
def load_customer_names() -> list[str]:
    customers = pd.read_csv(DATA_DIR / "sample_customer_data.csv")
    return customers["customer_name"].tolist()


st.title("AI Advisor Agent")
st.caption("Thesis MVP for governed, knowledge-intensive advisory work")

with st.sidebar:
    st.header("Advisory Goal")
    customer = st.selectbox("Customer", load_customer_names(), index=0)
    user_request = st.text_area(
        "Request",
        value="Generate an advisory brief based on aggregated claims, absence, and benchmark data.",
        height=120,
    )
    run_agent = st.button("Generate advisory brief", type="primary")

st.info(
    "This prototype uses synthetic aggregated data only. It demonstrates agent planning, "
    "bounded tool use, governance checks, approval gating, and audit logging."
)

if run_agent:
    with st.spinner("The agent is planning, analyzing data, and checking governance rules..."):
        result = AdvisorAgent().generate_advisory_brief(customer, user_request)

    st.subheader("Agent Goal")
    st.write(result.goal)

    st.subheader("Agent Plan")
    for index, step in enumerate(result.plan, start=1):
        st.write(f"{index}. {step}")

    st.subheader("Tool Calls")
    st.dataframe(pd.DataFrame(result.tool_calls), use_container_width=True)

    decision = result.governance
    st.subheader("Governance Checks")
    if decision["human_approval_required"]:
        st.warning("Human approval required before customer-facing use.")
    else:
        st.success("Output can be shown directly under the configured policy.")

    if result.governance["triggered_rules"]:
        st.dataframe(pd.DataFrame(result.governance["triggered_rules"]), use_container_width=True)
    else:
        st.write("No governance rules were triggered.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Stress gap", result.benchmark_comparison["stress_gap"])
    col2.metric("Absence gap", result.benchmark_comparison["absence_gap"])
    col3.metric("Data quality", result.data_quality["data_quality_score"])

    st.subheader("Final Advisory Brief")
    st.markdown(result.advisory_brief)

    st.subheader("Audit Log")
    st.code(result.audit_log_path)
else:
    st.subheader("What this MVP demonstrates")
    st.write("- Goal interpretation and a visible agent plan")
    st.write("- Bounded local data tools")
    st.write("- Governance policy checks before output")
    st.write("- Explicit human approval gating")
    st.write("- JSONL audit logs for each run")
