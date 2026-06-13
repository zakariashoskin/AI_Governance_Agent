"""Step-by-step governed advisor workflow page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import AdvisorWorkflowAgent
from app.ui_components import dataframe, inject_css, status_badge, status_message


st.set_page_config(page_title="Workflow | AI Advisor Agent", layout="wide")
inject_css()

st.title("Advisor Workflow")
st.caption("Transparent journey from signal to governed simulated action")

workflow = st.session_state.get("workflow")
if not workflow:
    workflow = AdvisorWorkflowAgent().start_workflow(
        customer_name="Novo Nordisk",
        signal_source="Advisory center conversation",
        user_request=(
            "Investigate the signal, identify possible wellbeing risks, determine missing "
            "context, and prepare only governed next steps."
        ),
    )
    st.session_state.workflow = workflow

st.subheader("Agent Goal")
st.write(workflow["goal"])

st.subheader("Agent Plan")
for index, step in enumerate(workflow["plan"], start=1):
    st.write(f"{index}. {step}")

st.progress(0.9, text="Governed workflow prepared. Final external action remains approval-gated.")

st.subheader("Employee Journey Stages")
for stage in workflow["stages"]:
    st.markdown(
        f"""
        <div class="stage-card">
            <strong>{stage['stage']}</strong><br>
            {stage['what_agent_did']}<br>
            Tool: <code>{stage['tool']}</code> | Data source: <code>{stage['data_source']}</code><br>
            Human input required: <strong>{stage['human_input_required']}</strong><br>
            Governance rules: {', '.join(stage['governance_rules_triggered']) or 'None'}
        </div>
        """,
        unsafe_allow_html=True,
    )

tab_data, tab_context, tab_governance, tab_action, tab_brief = st.tabs(
    ["Data Provenance", "Human Input", "Governance", "Stakeholder Action", "Brief"]
)

with tab_data:
    st.subheader("Data Provenance")
    st.write("Each insight shows where the information came from and whether it is approved for agent use.")
    provenance_table = pd.DataFrame(workflow["data_provenance"])
    st.dataframe(provenance_table, use_container_width=True)

with tab_context:
    st.subheader("Missing Context / Human-in-the-Loop")
    if workflow["missing_context"]["missing_context"]:
        st.warning(workflow["missing_context"]["prompt"])
    else:
        st.success("Business context has been added by the advisor.")

    for question in workflow["missing_context"]["required_questions"]:
        st.write(f"- {question}")

    human_context = st.text_area(
        "Add business context",
        value=workflow["missing_context"].get("human_context", ""),
        placeholder=(
            "Example: Novo recently launched a wellbeing initiative in Q2; HR is "
            "already investigating stress-related absence; there is an ongoing reorganization."
        ),
        height=120,
    )
    if st.button("Update workflow with human context"):
        st.session_state.workflow = AdvisorWorkflowAgent().update_with_human_context(
            workflow,
            human_context,
        )
        st.rerun()

with tab_governance:
    st.subheader("Governance Checks")
    for check in workflow["governance_checks"]:
        status_message(check["decision"], f"{check['action']}: {check['explanation']}")
        st.write(f"Required human role: {check.get('required_human_role') or 'None'}")
        st.write(f"Next step: {check['next_step']}")
        dataframe(check["triggered_rules"])

with tab_action:
    st.subheader("Stakeholder Action")
    st.write("These actions are simulated only. No email, meeting, or task is sent outside the app.")
    action_options = {
        "Prepare email to HR": "prepare_email_hr",
        "Prepare email to Compliance": "prepare_email_compliance",
        "Create follow-up task": "create_follow_up_task",
        "Request customer meeting": "request_customer_meeting",
        "Escalate to senior advisor": "escalate_to_senior_advisor",
    }
    cols = st.columns(len(action_options))
    for col, (label, action_type) in zip(cols, action_options.items()):
        if col.button(label):
            st.session_state.workflow = AdvisorWorkflowAgent().prepare_action(workflow, action_type)
            st.rerun()

    for index, action in enumerate(workflow["prepared_actions"]):
        with st.container(border=True):
            st.markdown(f"#### {action['subject']}")
            st.markdown(status_badge(action["status"]), unsafe_allow_html=True)
            st.write(f"Stakeholder: {action['stakeholder']}")
            st.write(f"Reason: {action['reason']}")
            st.text_area("Draft body", value=action["body"], height=180, key=f"body_{index}")
            status_message(
                action["governance"]["decision"],
                f"Governance: {action['governance']['explanation']}",
            )
            if action["status"] == "draft_requires_approval":
                if st.button("Approve simulated action", key=f"approve_{index}"):
                    st.session_state.workflow = AdvisorWorkflowAgent().approve_action(workflow, index)
                    st.rerun()

with tab_brief:
    st.subheader("Draft Advisory Brief")
    st.markdown(workflow["advisory_brief"])
    st.subheader("Final Agent Decision")
    st.warning(workflow["final_agent_decision"])
