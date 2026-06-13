"""Agent orchestration for the end-to-end advisor workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.audit import AUDIT_PATH, append_audit_entry, new_run_id, utc_now
from app.tools import (
    analyze_claims_data,
    assess_data_quality,
    check_governance_policy,
    compare_to_benchmark,
    detect_missing_context,
    draft_advisory_brief,
    generate_advisory_hypotheses,
    get_customer_context,
    get_signal,
    prepare_stakeholder_action,
    request_human_approval,
    trace_data_provenance,
)


@dataclass
class AgentResult:
    goal: str
    plan: list[str]
    tool_calls: list[dict[str, Any]]
    customer_context: dict[str, Any]
    claims_analysis: dict[str, Any]
    benchmark_comparison: dict[str, Any]
    data_quality: dict[str, Any]
    hypotheses: list[str]
    governance: dict[str, Any]
    approval_request: dict[str, Any]
    advisory_brief: str
    audit_log_path: str


class AdvisorWorkflowAgent:
    """A transparent, governed agent that supports an advisor journey."""

    def start_workflow(
        self,
        customer_name: str,
        signal_source: str,
        user_request: str,
        human_context: str = "",
    ) -> dict[str, Any]:
        run_id = new_run_id()
        goal = (
            f"Support the advisor in investigating a {signal_source.lower()} signal for "
            f"{customer_name}, using approved synthetic data and governance checks."
        )
        plan = [
            "Understand the signal and trace data provenance.",
            "Retrieve customer context and analyze aggregated data.",
            "Compare findings with benchmark and previous context.",
            "Detect missing business context and request human input.",
            "Run governance checks, draft brief, and prepare only approved simulated actions.",
        ]
        workflow = {
            "run_id": run_id,
            "timestamp": utc_now(),
            "user_request": user_request,
            "customer_name": customer_name,
            "signal_source": signal_source,
            "goal": goal,
            "plan": plan,
            "tool_calls": [],
            "stages": [],
            "human_inputs_added": [],
            "prepared_actions": [],
            "approvals_requested": [],
            "approvals_granted_or_denied": [],
            "blocked_actions": [],
        }

        customer = self._run_tool(
            workflow,
            "get_customer_context",
            get_customer_context,
            {"customer_name": customer_name},
            "Retrieved synthetic customer context.",
        )
        signal = self._run_tool(
            workflow,
            "get_signal",
            get_signal,
            {"customer_id": customer["customer_id"], "signal_source": signal_source},
            "Loaded the selected signal.",
        )
        provenance = self._run_tool(
            workflow,
            "trace_data_provenance",
            trace_data_provenance,
            {"customer_id": customer["customer_id"], "signal_id": signal["signal_id"]},
            "Traced signal and supporting data sources.",
        )
        claims = self._run_tool(
            workflow,
            "analyze_claims_data",
            analyze_claims_data,
            {"customer_id": customer["customer_id"]},
            "Analyzed aggregated claims and absence data.",
        )
        benchmark = self._run_tool(
            workflow,
            "compare_to_benchmark",
            compare_to_benchmark,
            {"customer_context": customer, "claims_analysis": claims},
            "Compared aggregated metrics with synthetic benchmark data.",
        )
        quality = self._run_tool(
            workflow,
            "assess_data_quality",
            assess_data_quality,
            {"claims_analysis": claims},
            "Assessed data quality.",
        )
        missing_context = self._run_tool(
            workflow,
            "detect_missing_context",
            detect_missing_context,
            {"customer_context": customer, "human_context": human_context},
            "Checked whether business context is missing.",
        )
        if human_context.strip():
            workflow["human_inputs_added"].append(
                {"timestamp": utc_now(), "input": human_context.strip()}
            )

        hypotheses_result = self._run_tool(
            workflow,
            "generate_advisory_hypotheses",
            generate_advisory_hypotheses,
            {
                "customer_context": customer,
                "signal": signal,
                "claims_analysis": claims,
                "benchmark_comparison": benchmark,
                "missing_context": missing_context,
            },
            "Generated advisory hypotheses.",
        )
        brief = self._run_tool(
            workflow,
            "draft_advisory_brief",
            draft_advisory_brief,
            {
                "customer_context": customer,
                "signal": signal,
                "hypotheses": hypotheses_result["hypotheses"],
                "missing_context": missing_context,
            },
            "Drafted advisory brief.",
        )

        governance_checks = [
            self._govern(workflow, "analyze_aggregated_data", False, 0.82),
            self._govern(workflow, "generate_advisory_hypotheses", False, 0.82),
            self._govern(workflow, "generate_final_recommendation", missing_context["missing_context"], 0.82),
            self._govern(workflow, "send_real_external_email", False, 1.0),
        ]
        approval_request = request_human_approval(governance_checks[2])
        if approval_request["approval_required"]:
            workflow["approvals_requested"].append(
                {
                    "action": "generate_final_recommendation",
                    "required_human_role": approval_request["required_human_role"],
                    "status": "pending",
                    "timestamp": utc_now(),
                }
            )

        workflow.update(
            {
                "customer": customer,
                "signal": signal,
                "data_provenance": provenance,
                "claims_analysis": claims,
                "benchmark_comparison": benchmark,
                "data_quality": quality,
                "missing_context": missing_context,
                "hypotheses": hypotheses_result["hypotheses"],
                "advisory_brief": brief,
                "governance_checks": governance_checks,
                "approval_request": approval_request,
                "final_agent_decision": self._final_decision(governance_checks),
            }
        )
        workflow["stages"] = self._stages(workflow)
        self._save_audit(workflow)
        return workflow

    def update_with_human_context(self, workflow: dict[str, Any], human_context: str) -> dict[str, Any]:
        return self.start_workflow(
            workflow["customer"]["customer_name"],
            workflow["signal"]["signal_source"],
            workflow["user_request"],
            human_context,
        )

    def prepare_action(self, workflow: dict[str, Any], action_type: str) -> dict[str, Any]:
        action = prepare_stakeholder_action(action_type, workflow)
        governance_action = (
            "prepare_stakeholder_email"
            if "email" in action_type
            else "escalate_risk"
            if "escalate" in action_type
            else "create_customer_facing_material"
        )
        governance = check_governance_policy(governance_action)
        action["governance"] = governance
        workflow["prepared_actions"].append(action)
        if governance["decision"] == "blocked":
            workflow["blocked_actions"].append(action)
        if governance["decision"] == "requires_approval":
            workflow["approvals_requested"].append(
                {
                    "action": action_type,
                    "required_human_role": governance["required_human_role"],
                    "status": "pending",
                    "timestamp": utc_now(),
                }
            )
        self._save_audit(workflow)
        return workflow

    def approve_action(self, workflow: dict[str, Any], action_index: int) -> dict[str, Any]:
        action = workflow["prepared_actions"][action_index]
        action["status"] = "approved_simulated_action"
        action["approved_at"] = utc_now()
        workflow["approvals_granted_or_denied"].append(
            {
                "action": action["action_type"],
                "decision": "approved",
                "timestamp": utc_now(),
                "note": "Simulated approval only. No external action was executed.",
            }
        )
        self._save_audit(workflow)
        return workflow

    def _run_tool(
        self,
        workflow: dict[str, Any],
        tool_name: str,
        tool_function: Callable[..., Any],
        inputs: dict[str, Any],
        summary: str,
    ) -> Any:
        result = tool_function(**inputs)
        workflow["tool_calls"].append(
            {
                "tool": tool_name,
                "inputs": inputs,
                "result_summary": summary,
                "timestamp": utc_now(),
            }
        )
        return result

    def _govern(
        self,
        workflow: dict[str, Any],
        action: str,
        missing_context: bool,
        confidence: float,
    ) -> dict[str, Any]:
        result = check_governance_policy(
            action,
            confidence_level=confidence,
            missing_context=missing_context,
        )
        result["action"] = action
        if result["decision"] == "blocked":
            workflow["blocked_actions"].append({"action": action, "governance": result})
        return result

    def _stages(self, workflow: dict[str, Any]) -> list[dict[str, Any]]:
        stage_specs = [
            ("Signal received", "get_signal", "Selected source signal was loaded.", "signals.csv"),
            ("Data sources identified", "trace_data_provenance", "Evidence provenance was traced.", "signals and supporting source files"),
            ("Customer context retrieved", "get_customer_context", "Customer profile was retrieved.", "customers.csv"),
            ("Data analyzed", "analyze_claims_data", "Aggregated claims data was analyzed.", "claims_data.csv"),
            ("Missing context detected", "detect_missing_context", workflow["missing_context"]["prompt"], "customer context"),
            ("Human input collected", "human_input", "Advisor can add business context.", "manual input"),
            ("Governance check completed", "check_governance_policy", "Policy decisions were evaluated.", "policy.yaml"),
            ("Advisory brief generated", "draft_advisory_brief", "Draft brief was created.", "agent synthesis"),
            ("Action prepared", "prepare_stakeholder_action", "Bounded actions can be prepared as drafts.", "stakeholder_directory.csv"),
            ("Final approval required", "request_human_approval", workflow["final_agent_decision"], "policy.yaml"),
        ]
        return [
            {
                "stage": stage,
                "tool": tool,
                "what_agent_did": description,
                "data_source": source,
                "human_input_required": stage in {"Missing context detected", "Human input collected", "Final approval required"},
                "governance_rules_triggered": self._stage_rules(workflow, stage),
            }
            for stage, tool, description, source in stage_specs
        ]

    def _stage_rules(self, workflow: dict[str, Any], stage: str) -> list[str]:
        if stage == "Final approval required":
            return [
                rule["rule_id"]
                for check in workflow["governance_checks"]
                for rule in check["triggered_rules"]
                if check["decision"] != "allowed"
            ]
        if stage == "Missing context detected" and workflow["missing_context"]["missing_context"]:
            return ["HITL-001"]
        return []

    def _final_decision(self, governance_checks: list[dict[str, Any]]) -> str:
        if any(check["decision"] == "blocked" for check in governance_checks):
            return "Blocked actions exist. The agent must not execute prohibited actions."
        if any(check["decision"] == "requires_approval" for check in governance_checks):
            return "Human approval is required before customer-facing recommendation or stakeholder action."
        return "Allowed to continue with internal advisory preparation."

    def _save_audit(self, workflow: dict[str, Any]) -> None:
        append_audit_entry(
            {
                "run_id": workflow["run_id"],
                "user_request": workflow["user_request"],
                "customer": workflow["customer"]["customer_name"],
                "signal_source": workflow["signal"]["signal_source"],
                "agent_plan": workflow["plan"],
                "tool_calls": workflow["tool_calls"],
                "data_sources_used": [item["source_name"] for item in workflow.get("data_provenance", [])],
                "human_inputs_added": workflow["human_inputs_added"],
                "governance_checks": workflow["governance_checks"],
                "approvals_requested": workflow["approvals_requested"],
                "approvals_granted_or_denied": workflow["approvals_granted_or_denied"],
                "blocked_actions": workflow["blocked_actions"],
                "final_output": workflow["advisory_brief"],
                "prepared_actions": workflow["prepared_actions"],
                "raw_workflow": workflow,
            }
        )


class AdvisorAgent:
    """Compatibility facade for earlier README examples and tests."""

    def generate_advisory_brief(self, customer_name: str, user_request: str) -> AgentResult:
        workflow = AdvisorWorkflowAgent().start_workflow(
            customer_name=customer_name,
            signal_source="Advisory center conversation",
            user_request=user_request,
        )
        return AgentResult(
            goal=workflow["goal"],
            plan=workflow["plan"],
            tool_calls=workflow["tool_calls"],
            customer_context=workflow["customer"],
            claims_analysis=workflow["claims_analysis"],
            benchmark_comparison=workflow["benchmark_comparison"],
            data_quality=workflow["data_quality"],
            hypotheses=workflow["hypotheses"],
            governance=workflow["governance_checks"][2],
            approval_request=workflow["approval_request"],
            advisory_brief=workflow["advisory_brief"],
            audit_log_path=str(AUDIT_PATH),
        )
