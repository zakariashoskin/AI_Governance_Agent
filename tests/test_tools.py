from app.tools import (
    analyze_claims,
    compare_with_benchmark,
    detect_missing_context,
    get_customer_context,
    get_signal,
    trace_data_provenance,
)


def test_customer_context_for_default_scenario():
    context = get_customer_context("Novo Nordisk")

    assert context["customer_id"] == "CUST-001"
    assert context["organizational_context_available"] is False


def test_signal_and_provenance_are_loaded():
    context = get_customer_context("Novo Nordisk")
    signal = get_signal(context["customer_id"], "Advisory center conversation")
    provenance = trace_data_provenance(context["customer_id"], signal["signal_id"])

    assert signal["signal_title"] == "Increasing stress-related inquiries among employees"
    assert provenance
    assert all("approved_for_agent_use" in item for item in provenance)


def test_claim_analysis_and_benchmark_comparison():
    context = get_customer_context("Novo Nordisk")
    analysis = analyze_claims(customer_id=context["customer_id"])
    comparison = compare_with_benchmark(context, analysis)

    assert analysis["top_claim_category"] == "Stress and mental health"
    assert comparison["stress_gap"] > 0


def test_missing_context_detection_changes_after_human_input():
    context = get_customer_context("Novo Nordisk")

    missing = detect_missing_context(context)
    updated = detect_missing_context(context, "HR is already investigating stress-related absence.")

    assert missing["missing_context"] is True
    assert updated["missing_context"] is False
