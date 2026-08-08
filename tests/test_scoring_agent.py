from agents.scoring_agent import ScoringAgent
from models.schemas import RiskFinding


def finding(severity: str) -> RiskFinding:
    return RiskFinding(title="t", severity=severity, description="d", recommendation="r")


def test_no_findings_gives_perfect_score():
    score, risk_level = ScoringAgent().calculate_score([])
    assert score == 100
    assert risk_level == "low"


def test_penalties_accumulate():
    score, risk_level = ScoringAgent().calculate_score([finding("high"), finding("medium")])
    assert score == 45
    assert risk_level == "high"


def test_score_never_goes_below_zero():
    score, _ = ScoringAgent().calculate_score([finding("critical")] * 4)
    assert score == 0


def test_any_critical_finding_forces_critical_risk():
    score, risk_level = ScoringAgent().calculate_score([finding("critical")])
    assert score == 50
    assert risk_level == "critical"
