"""Readable Streamlit audit log view for governance review."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from app.audit import load_audit_entries
from app.ui_components import status_message


def render_audit_log_page() -> None:
    """Render a thesis-friendly audit log view."""

    st.title("Governance Audit Log")
    st.write(
        "The audit log documents how the AI Advisor Agent uses tools, applies "
        "governance rules, and determines when human oversight is required."
    )

    entries = load_audit_entries()
    if not entries:
        st.info("No audit entries yet. Run the workflow to create the first log.")
        return

    filter_choice = st.radio(
        "Filter audit entries",
        ["Show all", "Allowed only", "Requires approval", "Blocked"],
        horizontal=True,
    )
    filtered = [
        entry for entry in reversed(entries) if _matches_filter(entry, filter_choice)
    ]
    if not filtered:
        st.info("No audit entries match this filter.")
        return

    for entry in filtered:
        _render_card(entry)


def _render_card(entry: dict[str, Any]) -> None:
    status = _entry_status(entry)
    with st.container(border=True):
        st.markdown(
            f"### {entry.get('customer', 'Unknown customer')} | {_timestamp(entry)}"
        )
        status_message(status, _status_text(status))

        st.markdown("**User request**")
        st.write(entry.get("user_request", "Not recorded."))

        st.markdown("**Signal source**")
        st.write(entry.get("signal_source") or "Not recorded.")

        st.markdown("**Agent plan**")
        for index, step in enumerate(_plan(entry), start=1):
            st.write(f"{index}. {step}")

        st.markdown("**Tool calls**")
        _table(_tool_calls(entry))

        st.markdown("**Data sources used**")
        sources = entry.get("data_sources_used", [])
        st.write(", ".join(sources) if sources else "No data sources recorded.")

        st.markdown("**Human inputs added**")
        _table(entry.get("human_inputs_added", []))

        st.markdown("**Governance checks**")
        checks = entry.get("governance_checks", [])
        if checks:
            _table(_flatten_checks(checks))
        else:
            st.write("No governance checks recorded.")

        st.markdown("**Approvals requested**")
        _table(entry.get("approvals_requested", []))

        st.markdown("**Approvals granted or denied**")
        _table(entry.get("approvals_granted_or_denied", []))

        st.markdown("**Blocked actions**")
        _table(entry.get("blocked_actions", []))

        st.markdown("**Prepared actions**")
        _table(_prepared_actions(entry.get("prepared_actions", [])))

        st.markdown("**Final output**")
        st.write(entry.get("final_output") or entry.get("final_output_summary", "Not recorded."))

        with st.expander("Raw JSON"):
            st.json(entry)


def _entry_status(entry: dict[str, Any]) -> str:
    checks = entry.get("governance_checks", [])
    decisions = [check.get("decision") for check in checks if isinstance(check, dict)]
    if "blocked" in decisions or entry.get("blocked_actions"):
        return "blocked"
    if "requires_approval" in decisions or entry.get("approvals_requested") or entry.get("human_approval_required"):
        return "requires_approval"
    return "allowed"


def _matches_filter(entry: dict[str, Any], filter_choice: str) -> bool:
    status = _entry_status(entry)
    return (
        filter_choice == "Show all"
        or (filter_choice == "Allowed only" and status == "allowed")
        or (filter_choice == "Requires approval" and status == "requires_approval")
        or (filter_choice == "Blocked" and status == "blocked")
    )


def _status_text(status: str) -> str:
    if status == "blocked":
        return "Blocked action detected. The agent did not execute prohibited behavior."
    if status == "requires_approval":
        return "Human approval is required before external or customer-facing action."
    return "Allowed internal analysis under the current policy."


def _timestamp(entry: dict[str, Any]) -> str:
    timestamp = entry.get("timestamp") or entry.get("timestamp_utc")
    if not timestamp:
        return "No timestamp"
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return timestamp


def _plan(entry: dict[str, Any]) -> list[str]:
    return entry.get("agent_plan") or entry.get("plan") or []


def _tool_calls(entry: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "Tool": call.get("tool"),
            "Summary": call.get("result_summary"),
            "Timestamp": call.get("timestamp") or call.get("timestamp_utc"),
        }
        for call in entry.get("tool_calls", [])
    ]


def _flatten_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for check in checks:
        rows.append(
            {
                "Action": check.get("action"),
                "Decision": check.get("decision"),
                "Explanation": check.get("explanation"),
                "Required role": check.get("required_human_role"),
                "Next step": check.get("next_step"),
            }
        )
    return rows


def _prepared_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Action": action.get("action_type"),
            "Stakeholder": action.get("stakeholder"),
            "Status": action.get("status"),
            "Reason": action.get("reason"),
            "Simulated only": action.get("simulated_only"),
        }
        for action in actions
    ]


def _table(records: list[dict[str, Any]]) -> None:
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True)
    else:
        st.write("None recorded.")
