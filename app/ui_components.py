"""Reusable Streamlit UI components for the advisor prototype."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


STATUS_COLORS = {
    "allowed": "#15803d",
    "requires_approval": "#b7791f",
    "blocked": "#b91c1c",
    "pending": "#b7791f",
    "approved_simulated_action": "#15803d",
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .metric-card {
            border: 1px solid #d8e2dc;
            border-radius: 8px;
            padding: 16px;
            background: #ffffff;
            min-height: 112px;
        }
        .metric-label {
            color: #52616b;
            font-size: 0.85rem;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1f2937;
        }
        .stage-card {
            border-left: 5px solid #2c7be5;
            border-radius: 8px;
            padding: 14px 16px;
            background: #f8fafc;
            margin-bottom: 12px;
        }
        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 3px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#52616b")
    label = status.replace("_", " ").title()
    return f'<span class="badge" style="background:{color}">{label}</span>'


def status_message(decision: str, text: str) -> None:
    if decision == "allowed":
        st.success(text)
    elif decision == "blocked":
        st.error(text)
    else:
        st.warning(text)


def dataframe(records: list[dict[str, Any]]) -> None:
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True)
    else:
        st.write("No records available.")
