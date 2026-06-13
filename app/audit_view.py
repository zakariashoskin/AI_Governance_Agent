"""Readable Streamlit audit log view for governance review."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from app.audit import load_audit_entries


BLOCKING_RULE_IDS = {"GOV-001", "GOV-003", "GOV-004"}


def render_audit_log_page() -> None:
    """Render a thesis-friendly audit log view."""

    st.subheader("Audit Log")
    st.write(
        "The audit log documents how the AI Advisor Agent uses tools, applies "
        "governance rules, and determines when human oversight is required."
    )

    entries = load_audit_entries()
    if not entries:
        st.info("No audit entries yet. Generate an advisory brief to create the first log.")
        return

    filter_choice = st.radio(
        "Filter audit entries",
        ["Show all", "Allowed only", "Requires approval", "Blocked"],
        horizontal=True,
    )
    filtered_entries = [
        entry for entry in reversed(entries) if _matches_filter(entry, filter_choice)
    ]

    if not filtered_entries:
        st.info("No audit entries match this filter.")
        return

    for entry in filtered_entries:
        _render_audit_card(entry)


def _render_audit_card(entry: dict[str, Any]) -> None:
    status = _entry_status(entry)
    timestamp = _format_timestamp(entry.get("timestamp_utc", ""))
    title = f"{entry.get('customer', 'Unknown customer')} | {timestamp}"

    with st.container(border=True):
        st.markdown(f"### {title}")
        _render_status(status)

        st.markdown("**User request**")
        st.write(entry.get("user_request", "Not recorded."))

        st.markdown("**Agent goal**")
        st.write(_agent_goal(entry))

        st.markdown("**Agent plan**")
        for index, step in enumerate(entry.get("plan", []), start=1):
            st.write(f"{index}. {step}")

        st.markdown("**Tools used**")
        tool_calls = entry.get("tool_calls", [])
        if tool_calls:
            st.dataframe(_tool_call_table(tool_calls), use_container_width=True)
        else:
            st.write("No tool calls recorded.")

        st.markdown("**Data sources used**")
        data_sources = entry.get("data_sources_used", [])
        st.write(", ".join(data_sources) if data_sources else "No data sources recorded.")

        st.markdown("**Governance rules triggered**")
        rules = entry.get("governance_rules_triggered", [])
        if rules:
            st.dataframe(pd.DataFrame(rules), use_container_width=True)
        else:
            st.success("No governance rules were triggered.")

        st.markdown("**Missing organizational context**")
        if _missing_context(entry):
            st.warning("Organizational context is missing. Stakeholder input is required.")
        else:
            st.success("Organizational context is available for this run.")

        st.markdown("**Human approval requirement**")
        if entry.get("human_approval_required", False):
            st.warning("Human approval is required before customer-facing use.")
        else:
            st.success("Human approval is not required under the current policy.")

        st.markdown("**Final agent decision**")
        st.write(_final_decision(entry))

        with st.expander("Raw JSON"):
            st.json(entry)


def _render_status(status: str) -> None:
    if status == "Blocked":
        st.error("Blocked by governance policy.")
    elif status == "Requires approval":
        st.warning("Requires human approval.")
    else:
        st.success("Allowed under the current governance policy.")


def _entry_status(entry: dict[str, Any]) -> str:
    triggered_ids = {
        rule.get("rule_id") for rule in entry.get("governance_rules_triggered", [])
    }
    if triggered_ids.intersection(BLOCKING_RULE_IDS):
        return "Blocked"
    if entry.get("human_approval_required", False):
        return "Requires approval"
    return "Allowed"


def _matches_filter(entry: dict[str, Any], filter_choice: str) -> bool:
    status = _entry_status(entry)
    if filter_choice == "Allowed only":
        return status == "Allowed"
    if filter_choice == "Requires approval":
        return status == "Requires approval"
    if filter_choice == "Blocked":
        return status == "Blocked"
    return True


def _tool_call_table(tool_calls: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Tool": call.get("tool", ""),
                "Summary": call.get("result_summary", ""),
                "Timestamp": _format_timestamp(call.get("timestamp_utc", "")),
            }
            for call in tool_calls
        ]
    )


def _missing_context(entry: dict[str, Any]) -> bool:
    if "missing_organizational_context" in entry:
        return bool(entry["missing_organizational_context"])
    return any(
        rule.get("rule_id") == "GOV-007"
        for rule in entry.get("governance_rules_triggered", [])
    )


def _agent_goal(entry: dict[str, Any]) -> str:
    if entry.get("agent_goal"):
        return entry["agent_goal"]
    customer = entry.get("customer", "the selected customer")
    return f"Produce a governed advisory brief for {customer} using synthetic data."


def _final_decision(entry: dict[str, Any]) -> str:
    if entry.get("final_agent_decision"):
        return entry["final_agent_decision"]
    status = _entry_status(entry)
    if status == "Blocked":
        return "Blocked by governance policy."
    if status == "Requires approval":
        return "Requires human approval before customer-facing use."
    return "Allowed for direct display under the current policy."


def _format_timestamp(timestamp: str) -> str:
    if not timestamp:
        return "No timestamp"
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return timestamp
    return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
