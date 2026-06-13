"""Goal-driven advisory agent orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.audit import AuditLogger
from app.tools import (
    analyze_claims_data,
    assess_data_quality,
    check_governance_policy,
    compare_to_benchmark,
    generate_advisory_hypotheses,
    get_customer_context,
    request_human_approval,
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


class AdvisorAgent:
    """Coordinates planning, tool use, governance checks, and brief generation."""

    def generate_advisory_brief(self, customer_name: str, user_request: str) -> AgentResult:
        audit = AuditLogger()
        goal = self._interpret_goal(customer_name, user_request)
        plan = self._create_plan(customer_name)
        tool_calls: list[dict[str, Any]] = []

        customer_context = self._run_tool(
            audit,
            tool_calls,
            "get_customer_context",
            get_customer_context,
            {"customer_name": customer_name},
            f"Loaded context for {customer_name}.",
        )
        audit.log_data_source("data/sample_customer_data.csv")

        claims_analysis = self._run_tool(
            audit,
            tool_calls,
            "analyze_claims_data",
            analyze_claims_data,
            {"customer_name": customer_name},
            "Analyzed aggregated synthetic claims and absence metrics.",
        )
        audit.log_data_source("data/sample_claims_data.csv")

        benchmark_comparison = self._run_tool(
            audit,
            tool_calls,
            "compare_to_benchmark",
            compare_to_benchmark,
            {
                "customer_context": customer_context,
                "claims_analysis": claims_analysis,
            },
            "Compared customer metrics with synthetic benchmark data.",
        )
        audit.log_data_source("data/sample_benchmark_data.csv")

        data_quality = self._run_tool(
            audit,
            tool_calls,
            "assess_data_quality",
            assess_data_quality,
            {"claims_analysis": claims_analysis},
            "Assessed data quality for advisory use.",
        )

        hypotheses_result = self._run_tool(
            audit,
            tool_calls,
            "generate_advisory_hypotheses",
            generate_advisory_hypotheses,
            {
                "customer_context": customer_context,
                "claims_analysis": claims_analysis,
                "benchmark_comparison": benchmark_comparison,
            },
            "Generated advisory hypotheses from aggregated data.",
        )
        hypotheses = hypotheses_result["hypotheses"]

        governance_result = self._run_tool(
            audit,
            tool_calls,
            "check_governance_policy",
            check_governance_policy,
            {
                "customer_context": customer_context,
                "data_quality": data_quality,
                "includes_final_recommendation": True,
                "attempts_external_action": False,
                "contains_pii": False,
                "uses_only_aggregated_data": True,
            },
            "Checked policy rules before releasing the brief.",
        )
        for rule in governance_result["triggered_rules"]:
            audit.log_governance_decision(rule)

        approval_request = self._run_tool(
            audit,
            tool_calls,
            "request_human_approval",
            request_human_approval,
            {"governance_result": governance_result},
            "Created a human approval request when required.",
        )

        advisory_brief = self._format_brief(
            customer_context,
            claims_analysis,
            benchmark_comparison,
            data_quality,
            hypotheses,
            governance_result,
            approval_request,
        )
        output_summary = advisory_brief.splitlines()[0]
        audit_path = audit.save(
            user_request=user_request,
            customer=customer_name,
            plan=plan,
            human_approval_required=governance_result["human_approval_required"],
            final_output_summary=output_summary,
        )

        return AgentResult(
            goal=goal,
            plan=plan,
            tool_calls=tool_calls,
            customer_context=customer_context,
            claims_analysis=claims_analysis,
            benchmark_comparison=benchmark_comparison,
            data_quality=data_quality,
            hypotheses=hypotheses,
            governance=governance_result,
            approval_request=approval_request,
            advisory_brief=advisory_brief,
            audit_log_path=str(audit_path),
        )

    def _interpret_goal(self, customer_name: str, user_request: str) -> str:
        return (
            f"Produce a governed advisory brief for {customer_name} using only "
            f"synthetic aggregated data. User request: {user_request}"
        )

    def _create_plan(self, customer_name: str) -> list[str]:
        return [
            f"Retrieve customer context for {customer_name}.",
            "Analyze aggregated claims, absence, and health-related indicators.",
            "Compare the customer metrics with industry benchmarks.",
            "Assess data quality and identify missing organizational context.",
            "Generate hypotheses, run governance checks, and request approval if needed.",
        ]

    def _run_tool(
        self,
        audit: AuditLogger,
        tool_calls: list[dict[str, Any]],
        tool_name: str,
        tool_function: Callable[..., Any],
        inputs: dict[str, Any],
        result_summary: str,
    ) -> Any:
        result = tool_function(**inputs)
        call = {
            "tool": tool_name,
            "inputs": inputs,
            "result_summary": result_summary,
        }
        tool_calls.append(call)
        audit.log_tool_call(tool_name, inputs, result_summary)
        return result

    def _format_brief(
        self,
        customer_context: dict[str, Any],
        claims_analysis: dict[str, Any],
        benchmark_comparison: dict[str, Any],
        data_quality: dict[str, Any],
        hypotheses: list[str],
        governance_result: dict[str, Any],
        approval_request: dict[str, Any],
    ) -> str:
        approval_text = (
            "Human approval required before this can be used as customer-facing advice."
            if governance_result["human_approval_required"]
            else "Output can be shown directly under the current policy."
        )
        context_note = (
            customer_context["known_context"]
            if customer_context["organizational_context_available"]
            else "Organizational context is not available in the dataset."
        )

        hypothesis_text = "\n".join(f"- {item}" for item in hypotheses)
        triggered_text = "\n".join(
            f"- {rule['rule_id']}: {rule['reason']}"
            for rule in governance_result["triggered_rules"]
        ) or "- No governance rules triggered."

        return f"""Advisory brief for {customer_context['customer_name']}

Customer context:
- Industry: {customer_context['industry']}
- Employees: {customer_context['employees']}
- Region: {customer_context['region']}
- Context note: {context_note}

Aggregated data analysis:
- Latest year: {claims_analysis['latest_year']}
- Top claim category: {claims_analysis['top_claim_category']}
- Stress claims per 100 employees: {claims_analysis['stress_claims_per_100_employees']}
- Change in stress claims: {claims_analysis['stress_claims_change']}
- Absence days per employee: {claims_analysis['absence_days_per_employee']}
- Change in absence days: {claims_analysis['absence_days_change']}
- Data quality score: {data_quality['data_quality_score']}
- Data quality assessment: {data_quality['assessment']}

Benchmark comparison:
- Benchmark industry: {benchmark_comparison['industry']}
- Stress gap vs benchmark: {benchmark_comparison['stress_gap']} per 100 employees
- Absence gap vs benchmark: {benchmark_comparison['absence_gap']} days per employee

Advisory hypotheses:
{hypothesis_text}

Governance decision:
- {approval_text}
- Approval workflow status: {approval_request['status']}

Rules triggered:
{triggered_text}
"""
