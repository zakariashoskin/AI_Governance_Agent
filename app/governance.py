"""Governance policy loading and decision logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


POLICY_PATH = Path(__file__).resolve().parents[1] / "governance" / "policy.yaml"


class GovernanceEngine:
    """Evaluates data use and agent actions against a YAML policy."""

    def __init__(self, policy_path: Path = POLICY_PATH) -> None:
        self.policy_path = policy_path
        self.policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

    def check_action(
        self,
        action: str,
        *,
        data_sensitivity: str = "aggregated",
        provenance_approved: bool = True,
        confidence_level: float = 1.0,
        missing_context: bool = False,
    ) -> dict[str, Any]:
        """Return allowed / requires_approval / blocked for an action."""

        triggered: list[dict[str, Any]] = []

        for rule in self.policy.get("blocked_actions", []):
            if rule["action"] == action:
                triggered.append(self._rule_event(rule, "blocked"))
                return self._decision(
                    "blocked",
                    triggered,
                    rule["explanation"],
                    "Governance owner",
                    "Do not execute this action.",
                )

        for rule in self.policy.get("approval_required_actions", []):
            if rule["action"] == action:
                triggered.append(self._rule_event(rule, "requires_approval"))
                return self._decision(
                    "requires_approval",
                    triggered,
                    rule["explanation"],
                    rule.get("required_human_role", "Advisor"),
                    "Request human approval before proceeding.",
                )

        for rule in self.policy.get("allowed_actions", []):
            if rule["action"] == action:
                triggered.append(self._rule_event(rule, "allowed"))

        if not provenance_approved:
            rule = self._data_rule("DATA-001")
            triggered.append(self._rule_event(rule, "blocked"))
            return self._decision(
                "blocked",
                triggered,
                "Data is not approved for agent use.",
                "Governance owner",
                "Remove or replace the data source.",
            )

        if data_sensitivity == "potentially_sensitive":
            rule = self._data_rule("DATA-002")
            triggered.append(self._rule_event(rule, "requires_approval"))

        if confidence_level < self.policy["thresholds"]["minimum_provenance_confidence"]:
            rule = self._data_rule("DATA-003")
            triggered.append(self._rule_event(rule, "requires_approval"))

        if missing_context:
            rule = self._oversight_rule("HITL-001")
            triggered.append(self._rule_event(rule, "requires_approval"))

        if any(rule["decision"] == "blocked" for rule in triggered):
            return self._decision(
                "blocked",
                triggered,
                "One or more governance rules block this action.",
                "Governance owner",
                "Stop and replace the action or data source.",
            )

        if any(rule["decision"] == "requires_approval" for rule in triggered):
            required_role = next(
                (
                    rule.get("required_human_role")
                    for rule in triggered
                    if rule.get("required_human_role")
                ),
                "Advisor",
            )
            return self._decision(
                "requires_approval",
                triggered,
                "Human approval is required before proceeding.",
                required_role,
                "Request approval and log the decision.",
            )

        return self._decision(
            "allowed",
            triggered,
            "Action is allowed under the current policy.",
            None,
            "Proceed and log the action.",
        )

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
        """Backward-compatible governance check used by existing tests."""

        action = "generate_final_recommendation" if includes_final_recommendation else "generate_advisory_hypotheses"
        result = self.check_action(
            action,
            data_sensitivity="potentially_sensitive" if contains_pii else "aggregated",
            provenance_approved=uses_only_aggregated_data,
            confidence_level=data_quality_score,
            missing_context=not organizational_context_available,
        )
        if contains_pii:
            pii_result = self.check_action("process_personal_identifiable_information")
            result = self._merge(result, pii_result)
        if attempts_external_action:
            external_result = self.check_action("contact_customer_directly")
            result = self._merge(result, external_result)

        return {
            "can_show_directly": result["decision"] == "allowed",
            "human_approval_required": result["decision"] == "requires_approval",
            "triggered_rules": result["triggered_rules"],
            "decision": result["decision"],
            "explanation": result["explanation"],
            "required_human_role": result["required_human_role"],
            "next_step": result["next_step"],
        }

    def _merge(self, primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
        severity_order = {"allowed": 0, "requires_approval": 1, "blocked": 2}
        decision = max(
            [primary["decision"], secondary["decision"]],
            key=lambda item: severity_order[item],
        )
        merged = {**primary, "decision": decision}
        merged["triggered_rules"] = primary["triggered_rules"] + secondary["triggered_rules"]
        if decision == secondary["decision"]:
            merged["explanation"] = secondary["explanation"]
            merged["required_human_role"] = secondary["required_human_role"]
            merged["next_step"] = secondary["next_step"]
        return merged

    def _decision(
        self,
        decision: str,
        triggered_rules: list[dict[str, Any]],
        explanation: str,
        required_human_role: str | None,
        next_step: str,
    ) -> dict[str, Any]:
        return {
            "decision": decision,
            "triggered_rules": triggered_rules,
            "explanation": explanation,
            "required_human_role": required_human_role,
            "next_step": next_step,
        }

    def _rule_event(self, rule: dict[str, Any], decision: str) -> dict[str, Any]:
        return {
            "rule_id": rule.get("rule_id", rule.get("id", "UNKNOWN")),
            "decision": decision,
            "explanation": rule.get("explanation", rule.get("description", "")),
            "required_human_role": rule.get("required_human_role"),
        }

    def _data_rule(self, rule_id: str) -> dict[str, Any]:
        return self._find_rule("data_rules", rule_id)

    def _oversight_rule(self, rule_id: str) -> dict[str, Any]:
        return self._find_rule("oversight_rules", rule_id)

    def _find_rule(self, section: str, rule_id: str) -> dict[str, Any]:
        for rule in self.policy.get(section, []):
            if rule.get("id") == rule_id:
                return rule
        return {"id": rule_id, "description": "Rule not found."}
