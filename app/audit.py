"""JSONL audit logging for the governed workflow."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


AUDIT_DIR = Path(__file__).resolve().parents[1] / "audit_logs"
AUDIT_PATH = AUDIT_DIR / "agent_audit.jsonl"


def new_run_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_audit_entry(entry: dict[str, Any], path: Path = AUDIT_PATH) -> Path:
    """Append one workflow audit event to the local JSONL file."""

    AUDIT_DIR.mkdir(exist_ok=True)
    enriched = {
        "audit_schema_version": "2.0",
        "timestamp": utc_now(),
        **entry,
    }
    with path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(enriched) + "\n")
    return path


def load_audit_entries(path: Path | None = None) -> list[dict[str, Any]]:
    """Read audit entries from the local JSONL file."""

    audit_path = path or AUDIT_PATH
    if not audit_path.exists():
        return []

    entries: list[dict[str, Any]] = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


class AuditLogger:
    """Compatibility wrapper for older agent tests and demos."""

    def __init__(self) -> None:
        self.run_id = new_run_id()
        self.tool_calls: list[dict[str, Any]] = []
        self.data_sources_used: set[str] = set()
        self.governance_rules_triggered: list[dict[str, Any]] = []

    def log_tool_call(self, tool_name: str, inputs: dict[str, Any], result_summary: str) -> None:
        self.tool_calls.append(
            {
                "tool": tool_name,
                "inputs": inputs,
                "result_summary": result_summary,
                "timestamp": utc_now(),
            }
        )

    def log_data_source(self, source_name: str) -> None:
        self.data_sources_used.add(source_name)

    def log_governance_decision(self, rule: dict[str, Any]) -> None:
        self.governance_rules_triggered.append(rule)

    def save(
        self,
        user_request: str,
        customer: str,
        agent_goal: str,
        plan: list[str],
        missing_organizational_context: bool,
        human_approval_required: bool,
        final_agent_decision: str,
        final_output_summary: str,
    ) -> Path:
        return append_audit_entry(
            {
                "run_id": self.run_id,
                "user_request": user_request,
                "customer": customer,
                "signal_source": None,
                "agent_goal": agent_goal,
                "agent_plan": plan,
                "tool_calls": self.tool_calls,
                "data_sources_used": sorted(self.data_sources_used),
                "human_inputs_added": [],
                "governance_checks": [
                    {
                        "triggered_rules": self.governance_rules_triggered,
                        "human_approval_required": human_approval_required,
                    }
                ],
                "approvals_requested": [],
                "approvals_granted_or_denied": [],
                "blocked_actions": [],
                "prepared_actions": [],
                "missing_organizational_context": missing_organizational_context,
                "final_output": final_output_summary,
                "final_agent_decision": final_agent_decision,
            }
        )
