"""Governance audit log page."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.audit_view import render_audit_log_page
from app.ui_components import inject_css


st.set_page_config(page_title="Audit Log | AI Advisor Agent", layout="wide")
inject_css()
render_audit_log_page()
