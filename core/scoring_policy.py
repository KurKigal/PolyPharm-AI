from __future__ import annotations

from dataclasses import dataclass, field

from models.schemas import FindingCategory, Severity


DEFAULT_SEVERITY_PENALTIES: dict[Severity, int] = {
    "critical": 50,
    "high": 35,
    "medium": 20,
    "low": 10,
}


@dataclass(frozen=True)
class ScoringPolicy:
    """Versioned deterministic scoring configuration.

    Category caps are supported but disabled by default. They should only be
    enabled after evaluation against a documented synthetic or expert-reviewed
    case set.
    """

    version: str = "1.1.0"
    starting_score: int = 100
    severity_penalties: dict[Severity, int] = field(
        default_factory=lambda: dict(DEFAULT_SEVERITY_PENALTIES)
    )
    category_caps: dict[FindingCategory, int] = field(default_factory=dict)

    def penalty_for(self, severity: Severity) -> int:
        return max(int(self.severity_penalties.get(severity, 0)), 0)

    def cap_for(self, category: FindingCategory) -> int | None:
        cap = self.category_caps.get(category)
        if cap is None:
            return None
        return max(int(cap), 0)


DEFAULT_SCORING_POLICY = ScoringPolicy()
