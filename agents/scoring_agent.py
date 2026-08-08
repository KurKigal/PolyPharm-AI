from core.scoring_policy import DEFAULT_SCORING_POLICY, ScoringPolicy
from models.schemas import (
    FindingCategory,
    RiskFinding,
    RiskLevel,
    ScoreBreakdown,
    ScoreContribution,
)


class ScoringAgent:
    """Convert findings into a versioned, deterministic, explainable score."""

    def __init__(
        self,
        policy: ScoringPolicy | None = None,
    ):
        self.policy = policy or DEFAULT_SCORING_POLICY

    def calculate_score(
        self,
        findings: list[RiskFinding],
        *,
        duplicates_suppressed: int = 0,
    ) -> tuple[int, RiskLevel, ScoreBreakdown]:
        category_penalties: dict[str, int] = {}
        contributions: list[ScoreContribution] = []

        for index, finding in enumerate(findings):
            category: FindingCategory = finding.category
            base_penalty = self.policy.penalty_for(
                finding.severity
            )

            category_total = category_penalties.get(
                category,
                0,
            )
            category_cap = self.policy.cap_for(
                category
            )

            if category_cap is None:
                applied_penalty = base_penalty
            else:
                remaining = max(
                    category_cap - category_total,
                    0,
                )
                applied_penalty = min(
                    base_penalty,
                    remaining,
                )

            category_penalties[category] = (
                category_total + applied_penalty
            )

            contributions.append(
                ScoreContribution(
                    finding_index=index,
                    severity=finding.severity,
                    category=category,
                    base_penalty=base_penalty,
                    penalty=applied_penalty,
                    capped=applied_penalty < base_penalty,
                    title=finding.title,
                    source=finding.source,
                    agent=finding.agent,
                    evidence_type=finding.evidence_type,
                    rule_id=finding.rule_id,
                    rule_version=finding.rule_version,
                    evidence_reference=finding.evidence_reference,
                )
            )

        total_penalty = sum(
            contribution.penalty
            for contribution in contributions
        )
        raw_score = (
            self.policy.starting_score
            - total_penalty
        )
        final_score = max(
            raw_score,
            0,
        )

        breakdown = ScoreBreakdown(
            policy_version=self.policy.version,
            starting_score=self.policy.starting_score,
            total_penalty=total_penalty,
            raw_score=raw_score,
            final_score=final_score,
            duplicates_suppressed=duplicates_suppressed,
            category_penalties=category_penalties,
            contributions=contributions,
        )

        risk_level = self._risk_level_from_score(
            score=final_score,
            findings=findings,
        )

        return (
            final_score,
            risk_level,
            breakdown,
        )

    def _risk_level_from_score(
        self,
        score: int,
        findings: list[RiskFinding],
    ) -> RiskLevel:
        if any(
            finding.severity == "critical"
            for finding in findings
        ):
            return "critical"

        if score >= 85:
            return "low"
        if score >= 60:
            return "medium"
        if score >= 30:
            return "high"

        return "critical"
