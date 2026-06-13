"""Governance policy loading and rule checks for advisory outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


POLICY_PATH = Path(__file__).resolve().parents[1] / "governance" / "policy.yaml"


class GovernanceEngine:
    """Evaluates bounded agent behavior against a YAML policy."""

    def __init__(self, policy_path: Path = POLICY_PATH) -> None:
        self.policy_path = policy_path
        self.policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

    def evaluate(
        self,
        *,
        uses_only_aggregated_data: bool,
        contains_pii: bool,
        data_quality_score: float,
        organizational_context_available: bool,
        includes_final_recommendation: bool,
        attempts_external_action: bool,
    ) -> dict[str, Any]:
        triggered: list[dict[str, Any]] = []
        approval_required = False
        can_show_directly = True

        def trigger(rule_id: str, reason: str, requires_approval: bool) -> None:
            nonlocal approval_required, can_show_directly
            rule = self._rule_by_id(rule_id)
            triggered.append(
                {
                    "rule_id": rule_id,
                    "severity": rule.get("severity", "medium"),
                    "reason": reason,
                    "requires_human_approval": requires_approval,
                }
            )
            approval_required = approval_required or requires_approval
            if rule.get("blocks_direct_output", False):
                can_show_directly = False

        if not uses_only_aggregated_data:
            trigger("GOV-001", "Agent attempted to use non-aggregated data.", True)

        if contains_pii:
            trigger("GOV-003", "Potential personally identifiable information detected.", True)

        if attempts_external_action:
            trigger("GOV-004", "Agent attempted an external customer action.", True)

        if includes_final_recommendation:
            trigger("GOV-005", "Strategic recommendations require human approval.", True)

        if data_quality_score < self.policy["thresholds"]["minimum_data_quality_score"]:
            trigger("GOV-006", "Data quality is below the policy threshold.", True)

        if not organizational_context_available:
            trigger(
                "GOV-007",
                "Organizational context is missing; stakeholder input is required.",
                True,
            )

        return {
            "can_show_directly": can_show_directly and not approval_required,
            "human_approval_required": approval_required,
            "triggered_rules": triggered,
        }

    def _rule_by_id(self, rule_id: str) -> dict[str, Any]:
        for rule in self.policy["rules"]:
            if rule["id"] == rule_id:
                return rule
        return {"id": rule_id, "severity": "medium"}
