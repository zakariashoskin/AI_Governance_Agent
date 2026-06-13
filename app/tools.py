"""Bounded tools for the governed advisor workflow."""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.data_loader import DATA_DIR, get_customer_by_name, read_csv
from app.governance import GovernanceEngine


def get_customer_context(customer_name: str) -> dict[str, Any]:
    """Retrieve synthetic customer metadata."""

    row = get_customer_by_name(customer_name)
    return {
        "customer_id": row["customer_id"],
        "customer_name": row["customer_name"],
        "industry": row["industry"],
        "employees": int(row["employees"]),
        "region": row["region"],
        "relationship_owner": row["relationship_owner"],
        "strategic_priority": row["strategic_priority"],
        "organizational_context_available": bool(row["organizational_context_available"]),
        "known_context": row["known_context"],
    }


def get_signal(customer_id: str, signal_source: str) -> dict[str, Any]:
    signals = read_csv("signals.csv")
    matches = signals[
        (signals["customer_id"] == customer_id)
        & (signals["signal_source"] == signal_source)
    ]
    if matches.empty:
        matches = signals[signals["customer_id"] == customer_id]
    if matches.empty:
        raise ValueError(f"No signal found for customer {customer_id}")
    return matches.iloc[0].to_dict()


def trace_data_provenance(customer_id: str, signal_id: str | None = None) -> list[dict[str, Any]]:
    """Collect provenance records across approved synthetic sources."""

    records: list[dict[str, Any]] = []
    signals = read_csv("signals.csv")
    if signal_id:
        signals = signals[signals["signal_id"] == signal_id]
    else:
        signals = signals[signals["customer_id"] == customer_id]

    for _, row in signals.iterrows():
        records.append(
            _provenance_record(
                source_type=row["signal_source"],
                source_name=row["signal_title"],
                timestamp=row["timestamp"],
                confidence=row["confidence_level"],
                structured=row["structured"],
                aggregated=row["aggregated"],
                sensitive=row["potentially_sensitive"],
                approved=row["approved_for_agent_use"],
                insight=row["signal_description"],
            )
        )

    source_specs = [
        ("advisory_center_notes.csv", "Advisory center conversation", "note_date", "source_name", "note_summary"),
        ("previous_meetings.csv", "Previous customer meeting", "meeting_date", "source_name", "summary"),
        ("chatbot_interactions.csv", "Customer-facing chatbot", "interaction_date", "source_name", "summary"),
        ("incident_reports.csv", "Incident report", "incident_date", "source_name", "summary"),
    ]
    for file_name, source_type, date_col, name_col, summary_col in source_specs:
        frame = read_csv(file_name)
        frame = frame[frame["customer_id"] == customer_id]
        for _, row in frame.iterrows():
            records.append(
                _provenance_record(
                    source_type=source_type,
                    source_name=row[name_col],
                    timestamp=f"{row[date_col]}T00:00:00Z",
                    confidence=row["confidence_level"],
                    structured=False,
                    aggregated=True,
                    sensitive=False,
                    approved=row["approved_for_agent_use"],
                    insight=row[summary_col],
                )
            )

    return records


def analyze_claims_data(customer_id: str | None = None, customer_name: str | None = None) -> dict[str, Any]:
    """Analyze aggregated synthetic health, claims, and absence patterns."""

    if customer_name and not customer_id:
        customer_id = get_customer_context(customer_name)["customer_id"]
    if not customer_id:
        raise ValueError("customer_id or customer_name is required")

    claims = read_csv("claims_data.csv")
    customer_claims = claims[claims["customer_id"] == customer_id]
    if customer_claims.empty:
        raise ValueError(f"No claims data found for customer {customer_id}")

    latest_year = int(customer_claims["year"].max())
    previous_year = latest_year - 1
    stress = customer_claims[customer_claims["claim_category"] == "Stress and mental health"]
    latest_stress = stress[stress["year"] == latest_year]
    previous_stress = stress[stress["year"] == previous_year]

    latest_rate = float(latest_stress["claims_per_100_employees"].mean())
    previous_rate = float(previous_stress["claims_per_100_employees"].mean())
    latest_all = customer_claims[customer_claims["year"] == latest_year]

    return {
        "latest_year": latest_year,
        "top_claim_category": latest_all.sort_values("claim_count", ascending=False).iloc[0]["claim_category"],
        "stress_claims_per_100_employees": latest_rate,
        "stress_claims_change": round(latest_rate - previous_rate, 2),
        "absence_days_per_employee": float(latest_all["absence_days_per_employee"].mean()),
        "data_quality_score": float(latest_all["data_quality_score"].mean()),
        "record_count": int(latest_all["claim_count"].sum()),
    }


def compare_to_benchmark(customer_context: dict[str, Any], claims_analysis: dict[str, Any]) -> dict[str, Any]:
    benchmark = read_csv("benchmark_data.csv")
    matches = benchmark[
        (benchmark["industry"] == customer_context["industry"])
        & (benchmark["claim_category"] == "Stress and mental health")
    ]
    if matches.empty:
        matches = benchmark[benchmark["industry"] == "General"]
    row = matches.iloc[0].to_dict()
    return {
        "industry": row["industry"],
        "claim_category": row["claim_category"],
        "benchmark_claims_per_100": float(row["benchmark_claims_per_100"]),
        "benchmark_absence_days_per_employee": float(row["benchmark_absence_days_per_employee"]),
        "stress_gap": round(
            claims_analysis["stress_claims_per_100_employees"]
            - float(row["benchmark_claims_per_100"]),
            2,
        ),
        "absence_gap": round(
            claims_analysis["absence_days_per_employee"]
            - float(row["benchmark_absence_days_per_employee"]),
            2,
        ),
    }


def assess_data_quality(claims_analysis: dict[str, Any]) -> dict[str, Any]:
    score = float(claims_analysis["data_quality_score"])
    return {
        "data_quality_score": score,
        "record_count": claims_analysis["record_count"],
        "is_sufficient": score >= 0.75,
        "assessment": (
            "Data quality is sufficient for hypothesis generation."
            if score >= 0.75
            else "Data quality is insufficient; human validation is required."
        ),
    }


def detect_missing_context(customer_context: dict[str, Any], human_context: str = "") -> dict[str, Any]:
    required_questions = [
        "whether the customer has existing HR initiatives",
        "whether there is an ongoing reorganization",
        "whether HR wants proactive intervention",
    ]
    missing = not customer_context["organizational_context_available"] and not human_context.strip()
    return {
        "missing_context": missing,
        "required_questions": required_questions,
        "prompt": (
            "The agent has identified a possible increase in stress-related claims, "
            "but lacks information about current HR initiatives."
        ),
        "human_context": human_context.strip(),
    }


def generate_advisory_hypotheses(
    customer_context: dict[str, Any],
    signal: dict[str, Any],
    claims_analysis: dict[str, Any],
    benchmark_comparison: dict[str, Any],
    missing_context: dict[str, Any],
) -> dict[str, Any]:
    hypotheses = [
        "There may be an emerging wellbeing issue related to stress and mental health.",
        (
            f"Stress-related claims are {benchmark_comparison['stress_gap']} per 100 employees "
            "above the synthetic benchmark."
        ),
        f"The initial signal from {signal['signal_source']} is consistent with the aggregated claims trend.",
    ]
    if missing_context["missing_context"]:
        hypotheses.append(
            "The evidence is not sufficient for a final recommendation because business context is missing."
        )
    else:
        hypotheses.append(
            f"Human-provided context has been added: {missing_context['human_context']}"
        )
    return {"hypotheses": hypotheses}


def draft_advisory_brief(
    customer_context: dict[str, Any],
    signal: dict[str, Any],
    hypotheses: list[str],
    missing_context: dict[str, Any],
) -> str:
    context_line = (
        "HR input is required before recommending a specific intervention."
        if missing_context["missing_context"]
        else "The advisor has added business context, so hypotheses can be refined for review."
    )
    hypothesis_text = "\n".join(f"- {item}" for item in hypotheses)
    return f"""Advisory brief draft for {customer_context['customer_name']}

Signal:
- Source: {signal['signal_source']}
- Description: {signal['signal_description']}

Agent interpretation:
{hypothesis_text}

Governance note:
- {context_line}
- Customer-facing recommendations require advisor approval.
"""


def prepare_stakeholder_action(action_type: str, workflow: dict[str, Any]) -> dict[str, Any]:
    customer_name = workflow["customer"]["customer_name"]
    reason = "Validate missing HR context before developing a customer-facing recommendation."
    stakeholder = _stakeholder_for_action(action_type)
    subject = f"Draft: Follow-up on wellbeing signal for {customer_name}"
    body = (
        f"Dear {stakeholder},\n\n"
        f"This is a simulated draft prepared inside the AI Advisor Agent prototype.\n\n"
        f"The agent identified a possible stress-related wellbeing signal for {customer_name}. "
        "The available evidence is aggregated and synthetic, but business context is missing. "
        "Could you help validate whether there are existing HR initiatives, ongoing reorganizations, "
        "or current investigations that should be considered before any advisory recommendation is made?\n\n"
        "No email has been sent. This draft requires human approval.\n"
    )
    return {
        "action_type": action_type,
        "stakeholder": stakeholder,
        "subject": subject,
        "body": body,
        "reason": reason,
        "status": "draft_requires_approval",
        "simulated_only": True,
    }


def check_governance_policy(
    action: str = "generate_final_recommendation",
    *,
    data_sensitivity: str = "aggregated",
    provenance_approved: bool = True,
    confidence_level: float = 1.0,
    missing_context: bool = False,
    **legacy: Any,
) -> dict[str, Any]:
    if legacy:
        customer_context = legacy.get("customer_context", {})
        data_quality = legacy.get("data_quality", {"data_quality_score": confidence_level})
        return GovernanceEngine().evaluate(
            uses_only_aggregated_data=legacy.get("uses_only_aggregated_data", True),
            contains_pii=legacy.get("contains_pii", False),
            data_quality_score=data_quality["data_quality_score"],
            organizational_context_available=customer_context.get("organizational_context_available", True),
            includes_final_recommendation=legacy.get("includes_final_recommendation", False),
            attempts_external_action=legacy.get("attempts_external_action", False),
        )
    return GovernanceEngine().check_action(
        action,
        data_sensitivity=data_sensitivity,
        provenance_approved=provenance_approved,
        confidence_level=confidence_level,
        missing_context=missing_context,
    )


def request_human_approval(governance_result: dict[str, Any]) -> dict[str, Any]:
    required = governance_result["decision"] == "requires_approval"
    return {
        "approval_required": required,
        "status": "pending_human_approval" if required else "not_required",
        "required_human_role": governance_result.get("required_human_role"),
        "reasons": [rule["explanation"] for rule in governance_result["triggered_rules"]],
    }


def _provenance_record(
    *,
    source_type: str,
    source_name: str,
    timestamp: str,
    confidence: float,
    structured: bool,
    aggregated: bool,
    sensitive: bool,
    approved: bool,
    insight: str,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_name": source_name,
        "timestamp": timestamp,
        "confidence_level": float(confidence),
        "structured": bool(structured),
        "aggregated": bool(aggregated),
        "potentially_sensitive": bool(sensitive),
        "approved_for_agent_use": bool(approved),
        "insight": insight,
    }


def _stakeholder_for_action(action_type: str) -> str:
    mapping = {
        "prepare_email_hr": "HR wellbeing partner",
        "prepare_email_compliance": "Compliance liaison",
        "create_follow_up_task": "Senior advisory lead",
        "request_customer_meeting": "Senior advisory lead",
        "escalate_to_senior_advisor": "Senior advisory lead",
    }
    return mapping.get(action_type, "Advisor")


# Backward-compatible aliases.
load_customer_context = get_customer_context
analyze_claims = analyze_claims_data
compare_with_benchmark = compare_to_benchmark
