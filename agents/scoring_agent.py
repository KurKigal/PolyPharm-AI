from models.schemas import (
    RiskFinding,
    RiskLevel,
    ScoreBreakdown,
    ScoreContribution,
)

STARTING_SCORE = 100

SEVERITY_PENALTY = {
    "critical": 50,
    "high": 35,
    "medium": 20,
    "low": 10,
}


class ScoringAgent:
    """Convert findings into a deterministic, explainable 0-100 safety score."""

    def calculate_score(
        self,
        findings: list[RiskFinding],
    ) -> tuple[int, RiskLevel, ScoreBreakdown]:
        contributions = [
            ScoreContribution(
                finding_index=index,
                severity=finding.severity,
                penalty=SEVERITY_PENALTY.get(finding.severity, 0),
                title=finding.title,
                source=finding.source,
                agent=finding.agent,
            )
            for index, finding in enumerate(findings)
        ]

        total_penalty = sum(item.penalty for item in contributions)
        raw_score = STARTING_SCORE - total_penalty
        final_score = max(raw_score, 0)

        breakdown = ScoreBreakdown(
            starting_score=STARTING_SCORE,
            total_penalty=total_penalty,
            raw_score=raw_score,
            final_score=final_score,
            contributions=contributions,
        )

        risk_level = self._risk_level_from_score(
            score=final_score,
            findings=findings,
        )

        return final_score, risk_level, breakdown

    def _risk_level_from_score(
        self,
        score: int,
        findings: list[RiskFinding],
    ) -> RiskLevel:
        if any(finding.severity == "critical" for finding in findings):
            return "critical"

        if score >= 85:
            return "low"
        if score >= 60:
            return "medium"
        if score >= 30:
            return "high"

        return "critical"
