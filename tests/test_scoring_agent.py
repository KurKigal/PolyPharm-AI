from agents.scoring_agent import ScoringAgent
from models.schemas import RiskFinding


def finding(
    severity: str,
    *,
    title: str = "test finding",
    source: str = "test source",
    agent: str = "TestAgent",
) -> RiskFinding:
    return RiskFinding(
        title=title,
        severity=severity,
        description="description",
        recommendation="recommendation",
        source=source,
        agent=agent,
    )


def test_no_findings_gives_perfect_score_and_empty_breakdown():
    score, risk_level, breakdown = ScoringAgent().calculate_score([])

    assert score == 100
    assert risk_level == "low"
    assert breakdown.starting_score == 100
    assert breakdown.total_penalty == 0
    assert breakdown.raw_score == 100
    assert breakdown.final_score == 100
    assert breakdown.contributions == []


def test_penalties_accumulate_and_are_attributed():
    score, risk_level, breakdown = ScoringAgent().calculate_score(
        [
            finding(
                "high",
                title="High finding",
                source="Source A",
                agent="AgentA",
            ),
            finding(
                "medium",
                title="Medium finding",
                source="Source B",
                agent="AgentB",
            ),
        ]
    )

    assert score == 45
    assert risk_level == "high"
    assert breakdown.total_penalty == 55
    assert breakdown.raw_score == 45
    assert breakdown.final_score == 45

    assert [item.penalty for item in breakdown.contributions] == [35, 20]
    assert breakdown.contributions[0].finding_index == 0
    assert breakdown.contributions[0].title == "High finding"
    assert breakdown.contributions[0].source == "Source A"
    assert breakdown.contributions[0].agent == "AgentA"


def test_score_floor_preserves_negative_raw_score_for_explainability():
    score, _, breakdown = ScoringAgent().calculate_score(
        [finding("critical")] * 4
    )

    assert score == 0
    assert breakdown.total_penalty == 200
    assert breakdown.raw_score == -100
    assert breakdown.final_score == 0


def test_any_critical_finding_forces_critical_risk():
    score, risk_level, breakdown = ScoringAgent().calculate_score(
        [finding("critical")]
    )

    assert score == 50
    assert risk_level == "critical"
    assert breakdown.contributions[0].penalty == 50
