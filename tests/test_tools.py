from app.tools import (
    analyze_claims,
    assess_data_quality,
    check_governance_policy,
    compare_with_benchmark,
    get_customer_context,
    load_customer_context,
)


def test_load_customer_context_for_example_pharma():
    context = load_customer_context("Example Pharma")

    assert context["customer_name"] == "Example Pharma"
    assert context["organizational_context_available"] is False


def test_claim_analysis_and_benchmark_comparison():
    context = load_customer_context("Example Pharma")
    analysis = analyze_claims("Example Pharma")
    comparison = compare_with_benchmark(context, analysis)

    assert analysis["top_claim_category"] == "Stress and mental health"
    assert comparison["stress_gap"] > 0


def test_named_agent_tools_support_governance_flow():
    context = get_customer_context("Example Pharma")
    analysis = analyze_claims("Example Pharma")
    data_quality = assess_data_quality(analysis)

    result = check_governance_policy(
        customer_context=context,
        data_quality=data_quality,
        includes_final_recommendation=True,
    )

    assert result["human_approval_required"] is True
    assert any(rule["rule_id"] == "GOV-005" for rule in result["triggered_rules"])
