from agents.scoring_agent import ScoringAgent
from core.scoring_policy import ScoringPolicy
from models.schemas import RiskFinding


def finding(
    severity: str,
    *,
    title: str = "test finding",
    category: str = "other",
    source: str = "test source",
    agent: str = "TestAgent",
) -> RiskFinding:
    return RiskFinding(
        title=title,
        severity=severity,
        description="description",
        recommendation="recommendation",
        category=category,
        evidence_type="prototype_rule",
        source=source,
        agent=agent,
        rule_id="TEST-RULE",
        rule_version="1.0.0",
    )


def test_no_findings_gives_perfect_score_and_versioned_breakdown():
    score, risk_level, breakdown = ScoringAgent().calculate_score([])

    assert score == 100
    assert risk_level == "low"
    assert breakdown.policy_version == "1.1.0"
    assert breakdown.starting_score == 100
    assert breakdown.total_penalty == 0
    assert breakdown.raw_score == 100
    assert breakdown.final_score == 100
    assert breakdown.contributions == []


def test_penalties_accumulate_and_provenance_is_preserved():
    score, risk_level, breakdown = ScoringAgent().calculate_score(
        [
            finding(
                "high",
                title="High finding",
                category="drug_interaction",
                source="Source A",
                agent="AgentA",
            ),
            finding(
                "medium",
                title="Medium finding",
                category="renal",
                source="Source B",
                agent="AgentB",
            ),
        ]
    )

    assert score == 45
    assert risk_level == "high"
    assert breakdown.total_penalty == 55
    assert breakdown.category_penalties == {
        "drug_interaction": 35,
        "renal": 20,
    }

    first = breakdown.contributions[0]
    assert first.base_penalty == 35
    assert first.penalty == 35
    assert first.category == "drug_interaction"
    assert first.evidence_type == "prototype_rule"
    assert first.rule_id == "TEST-RULE"
    assert first.rule_version == "1.0.0"


def test_score_floor_preserves_negative_raw_score_for_explainability():
    score, _, breakdown = ScoringAgent().calculate_score(
        [finding("critical")] * 4
    )

    assert score == 0
    assert breakdown.total_penalty == 200
    assert breakdown.raw_score == -100
    assert breakdown.final_score == 0


def test_optional_category_cap_is_explicit_and_traceable():
    policy = ScoringPolicy(
        version="test-cap",
        category_caps={
            "drug_interaction": 40,
        },
    )
    agent = ScoringAgent(
        policy=policy
    )

    score, _, breakdown = agent.calculate_score(
        [
            finding(
                "high",
                category="drug_interaction",
            ),
            finding(
                "high",
                category="drug_interaction",
            ),
        ]
    )

    assert score == 60
    assert breakdown.total_penalty == 40
    assert breakdown.category_penalties["drug_interaction"] == 40
    assert breakdown.contributions[0].penalty == 35
    assert breakdown.contributions[1].base_penalty == 35
    assert breakdown.contributions[1].penalty == 5
    assert breakdown.contributions[1].capped is True


def test_default_policy_does_not_enable_category_caps():
    agent = ScoringAgent()

    score, _, breakdown = agent.calculate_score(
        [
            finding(
                "high",
                category="drug_interaction",
            ),
            finding(
                "high",
                category="drug_interaction",
            ),
        ]
    )

    assert score == 30
    assert breakdown.total_penalty == 70
    assert all(
        not contribution.capped
        for contribution in breakdown.contributions
    )
