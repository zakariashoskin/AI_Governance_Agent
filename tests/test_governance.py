from app.governance import GovernanceEngine


def test_allowed_action_returns_allowed():
    result = GovernanceEngine().check_action("analyze_aggregated_data")

    assert result["decision"] == "allowed"


def test_approval_required_action_returns_required_role():
    result = GovernanceEngine().check_action("prepare_stakeholder_email")

    assert result["decision"] == "requires_approval"
    assert result["required_human_role"] == "Advisor"


def test_blocked_action_is_blocked():
    result = GovernanceEngine().check_action("send_real_external_email")

    assert result["decision"] == "blocked"
    assert result["triggered_rules"][0]["rule_id"] == "BLOCK-001"


def test_legacy_evaluate_blocks_prohibited_actions():
    result = GovernanceEngine().evaluate(
        uses_only_aggregated_data=False,
        contains_pii=True,
        data_quality_score=0.90,
        organizational_context_available=True,
        includes_final_recommendation=False,
        attempts_external_action=True,
    )

    assert result["decision"] == "blocked"
    assert result["can_show_directly"] is False
