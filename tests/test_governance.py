from app.governance import GovernanceEngine


def test_missing_context_requires_human_approval():
    engine = GovernanceEngine()

    result = engine.evaluate(
        uses_only_aggregated_data=True,
        contains_pii=False,
        data_quality_score=0.90,
        organizational_context_available=False,
        includes_final_recommendation=False,
        attempts_external_action=False,
    )

    assert result["human_approval_required"] is True
    assert any(rule["rule_id"] == "GOV-007" for rule in result["triggered_rules"])


def test_low_data_quality_triggers_validation():
    engine = GovernanceEngine()

    result = engine.evaluate(
        uses_only_aggregated_data=True,
        contains_pii=False,
        data_quality_score=0.50,
        organizational_context_available=True,
        includes_final_recommendation=False,
        attempts_external_action=False,
    )

    assert result["can_show_directly"] is False
    assert any(rule["rule_id"] == "GOV-006" for rule in result["triggered_rules"])


def test_governance_blocks_prohibited_actions():
    engine = GovernanceEngine()

    result = engine.evaluate(
        uses_only_aggregated_data=False,
        contains_pii=True,
        data_quality_score=0.90,
        organizational_context_available=True,
        includes_final_recommendation=False,
        attempts_external_action=True,
    )

    triggered_ids = {rule["rule_id"] for rule in result["triggered_rules"]}

    assert result["can_show_directly"] is False
    assert result["human_approval_required"] is True
    assert {"GOV-001", "GOV-003", "GOV-004"}.issubset(triggered_ids)
