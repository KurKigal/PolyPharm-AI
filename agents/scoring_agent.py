from models.schemas import RiskFinding, RiskLevel

SEVERITY_PENALTY = {
    "critical": 50,
    "high": 35,
    "medium": 20,
    "low": 10,
}


class ScoringAgent:
    """Convert findings into a deterministic 0-100 safety score."""

    def calculate_score(self, findings: list[RiskFinding]) -> tuple[int, RiskLevel]:
        score = 100
        for finding in findings:
            score -= SEVERITY_PENALTY.get(finding.severity, 0)

        score = max(score, 0)
        return score, self._risk_level_from_score(score=score, findings=findings)

    def _risk_level_from_score(self, score: int, findings: list[RiskFinding]) -> RiskLevel:
        if any(finding.severity == "critical" for finding in findings):
            return "critical"
        if score >= 85:
            return "low"
        if score >= 60:
            return "medium"
        if score >= 30:
            return "high"
        return "critical"
