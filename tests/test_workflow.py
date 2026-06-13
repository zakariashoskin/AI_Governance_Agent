from app.agent import AdvisorWorkflowAgent


def test_default_workflow_requires_human_input_and_blocks_external_email():
    workflow = AdvisorWorkflowAgent().start_workflow(
        "Novo Nordisk",
        "Advisory center conversation",
        "Investigate the signal.",
    )

    assert workflow["missing_context"]["missing_context"] is True
    assert any(check["decision"] == "requires_approval" for check in workflow["governance_checks"])
    assert any(item["action"] == "send_real_external_email" for item in workflow["blocked_actions"])


def test_prepare_action_creates_simulated_draft_requiring_approval():
    agent = AdvisorWorkflowAgent()
    workflow = agent.start_workflow(
        "Novo Nordisk",
        "Advisory center conversation",
        "Investigate the signal.",
    )
    workflow = agent.prepare_action(workflow, "prepare_email_hr")

    action = workflow["prepared_actions"][-1]
    assert action["simulated_only"] is True
    assert action["status"] == "draft_requires_approval"
    assert action["governance"]["decision"] == "requires_approval"
