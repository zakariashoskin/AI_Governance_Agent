"""Bounded tools the advisory agent may use for local data analysis.

Each public function below represents one explicit agent tool. The names are
intentionally plain so the Streamlit UI can show exactly what the agent did.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.governance import GovernanceEngine
from app.prompts import LLMClient


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def get_customer_context(customer_name: str) -> dict[str, Any]:
    """Retrieve synthetic customer metadata."""

    customers = pd.read_csv(DATA_DIR / "sample_customer_data.csv")
    match = customers[customers["customer_name"].str.lower() == customer_name.lower()]
    if match.empty:
        raise ValueError(f"Customer not found: {customer_name}")
    row = match.iloc[0].to_dict()
    return {
        "customer_name": row["customer_name"],
        "industry": row["industry"],
        "employees": int(row["employees"]),
        "region": row["region"],
        "organizational_context_available": bool(row["organizational_context_available"]),
        "known_context": row["known_context"],
    }


def analyze_claims_data(customer_name: str) -> dict[str, Any]:
    """Analyze aggregated synthetic health, claims, and absence patterns."""

    claims = pd.read_csv(DATA_DIR / "sample_claims_data.csv")
    customer_claims = claims[claims["customer_name"].str.lower() == customer_name.lower()]
    if customer_claims.empty:
        raise ValueError(f"No claims data found for: {customer_name}")

    latest_year = int(customer_claims["year"].max())
    previous_year = latest_year - 1
    latest = customer_claims[customer_claims["year"] == latest_year]
    previous = customer_claims[customer_claims["year"] == previous_year]

    def metric(frame: pd.DataFrame, column: str) -> float:
        return float(frame[column].mean()) if not frame.empty else 0.0

    stress_rate_latest = metric(latest, "stress_claims_per_100_employees")
    stress_rate_previous = metric(previous, "stress_claims_per_100_employees")
    absence_latest = metric(latest, "absence_days_per_employee")
    absence_previous = metric(previous, "absence_days_per_employee")

    return {
        "latest_year": latest_year,
        "stress_claims_per_100_employees": stress_rate_latest,
        "stress_claims_change": round(stress_rate_latest - stress_rate_previous, 2),
        "absence_days_per_employee": absence_latest,
        "absence_days_change": round(absence_latest - absence_previous, 2),
        "top_claim_category": latest.sort_values("claim_count", ascending=False).iloc[0][
            "claim_category"
        ],
        "data_quality_score": float(latest["data_quality_score"].mean()),
        "record_count": int(latest["claim_count"].sum()),
    }


def compare_to_benchmark(
    customer_context: dict[str, Any], claims_analysis: dict[str, Any]
) -> dict[str, Any]:
    """Compare customer metrics with synthetic industry benchmark data."""

    benchmark = pd.read_csv(DATA_DIR / "sample_benchmark_data.csv")
    match = benchmark[benchmark["industry"].str.lower() == customer_context["industry"].lower()]
    if match.empty:
        match = benchmark[benchmark["industry"].str.lower() == "general"]

    row = match.iloc[0].to_dict()
    return {
        "industry": row["industry"],
        "benchmark_stress_claims_per_100": float(row["benchmark_stress_claims_per_100"]),
        "benchmark_absence_days_per_employee": float(row["benchmark_absence_days_per_employee"]),
        "stress_gap": round(
            claims_analysis["stress_claims_per_100_employees"]
            - float(row["benchmark_stress_claims_per_100"]),
            2,
        ),
        "absence_gap": round(
            claims_analysis["absence_days_per_employee"]
            - float(row["benchmark_absence_days_per_employee"]),
            2,
        ),
    }


def assess_data_quality(claims_analysis: dict[str, Any]) -> dict[str, Any]:
    """Assess whether the synthetic data is strong enough for advisory use."""

    score = float(claims_analysis["data_quality_score"])
    is_sufficient = score >= 0.75
    return {
        "data_quality_score": score,
        "record_count": claims_analysis["record_count"],
        "is_sufficient": is_sufficient,
        "assessment": (
            "Data quality is sufficient for generating advisory hypotheses."
            if is_sufficient
            else "Data quality is insufficient; human validation is required."
        ),
    }


def generate_advisory_hypotheses(
    customer_context: dict[str, Any],
    claims_analysis: dict[str, Any],
    benchmark_comparison: dict[str, Any],
) -> dict[str, Any]:
    """Generate advisory hypotheses without making final recommendations."""

    return {
        "hypotheses": LLMClient().generate_advisory_hypotheses(
            customer_context,
            claims_analysis,
            benchmark_comparison,
        )
    }


def check_governance_policy(
    *,
    customer_context: dict[str, Any],
    data_quality: dict[str, Any],
    includes_final_recommendation: bool,
    attempts_external_action: bool = False,
    contains_pii: bool = False,
    uses_only_aggregated_data: bool = True,
) -> dict[str, Any]:
    """Run the configured governance policy before output is released."""

    return GovernanceEngine().evaluate(
        uses_only_aggregated_data=uses_only_aggregated_data,
        contains_pii=contains_pii,
        data_quality_score=data_quality["data_quality_score"],
        organizational_context_available=customer_context[
            "organizational_context_available"
        ],
        includes_final_recommendation=includes_final_recommendation,
        attempts_external_action=attempts_external_action,
    )


def request_human_approval(governance_result: dict[str, Any]) -> dict[str, Any]:
    """Create a clear approval request when governance rules require it."""

    required = bool(governance_result["human_approval_required"])
    return {
        "approval_required": required,
        "status": "pending_human_approval" if required else "not_required",
        "reasons": [rule["reason"] for rule in governance_result["triggered_rules"]],
    }


# Backward-compatible aliases for the initial tests and earlier examples.
load_customer_context = get_customer_context
analyze_claims = analyze_claims_data
compare_with_benchmark = compare_to_benchmark
