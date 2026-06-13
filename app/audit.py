"""Audit logging for agent actions and governance decisions."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


AUDIT_DIR = Path(__file__).resolve().parents[1] / "audit_logs"


@dataclass
class AuditEvent:
    """A structured record of one advisory agent run."""

    run_id: str
    timestamp_utc: str
    user_request: str
    customer: str
    plan: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    data_sources_used: list[str] = field(default_factory=list)
    governance_rules_triggered: list[dict[str, Any]] = field(default_factory=list)
    human_approval_required: bool = False
    final_output_summary: str = ""


class AuditLogger:
    """Collects events during a run and appends them to a JSONL audit file."""

    def __init__(self) -> None:
        self.run_id = str(uuid4())
        self.tool_calls: list[dict[str, Any]] = []
        self.data_sources_used: set[str] = set()
        self.governance_rules_triggered: list[dict[str, Any]] = []

    def log_tool_call(self, tool_name: str, inputs: dict[str, Any], result_summary: str) -> None:
        self.tool_calls.append(
            {
                "tool": tool_name,
                "inputs": inputs,
                "result_summary": result_summary,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
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
        plan: list[str],
        human_approval_required: bool,
        final_output_summary: str,
    ) -> Path:
        AUDIT_DIR.mkdir(exist_ok=True)
        event = AuditEvent(
            run_id=self.run_id,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            user_request=user_request,
            customer=customer,
            plan=plan,
            tool_calls=self.tool_calls,
            data_sources_used=sorted(self.data_sources_used),
            governance_rules_triggered=self.governance_rules_triggered,
            human_approval_required=human_approval_required,
            final_output_summary=final_output_summary,
        )
        output_path = AUDIT_DIR / "agent_audit.jsonl"
        with output_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(asdict(event)) + "\n")
        return output_path
