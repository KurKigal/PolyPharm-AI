from core.findings import deduplicate_findings
from models.schemas import RiskFinding


def finding(
    title: str,
    severity: str,
    *,
    dedupe_key: str | None,
    source: str = "source",
) -> RiskFinding:
    return RiskFinding(
        title=title,
        severity=severity,
        description="description",
        recommendation="recommendation",
        category="drug_interaction",
        evidence_type="curated_rule",
        source=source,
        agent="TestAgent",
        dedupe_key=dedupe_key,
    )


def test_explicit_duplicate_key_suppresses_duplicate():
    findings, suppressed = deduplicate_findings(
        [
            finding(
                "first",
                "medium",
                dedupe_key="same",
            ),
            finding(
                "duplicate",
                "medium",
                dedupe_key="same",
            ),
        ]
    )

    assert suppressed == 1
    assert len(findings) == 1
    assert findings[0].title == "first"


def test_more_severe_duplicate_replaces_lower_severity():
    findings, suppressed = deduplicate_findings(
        [
            finding(
                "lower",
                "medium",
                dedupe_key="same",
            ),
            finding(
                "higher",
                "high",
                dedupe_key="same",
            ),
        ]
    )

    assert suppressed == 1
    assert len(findings) == 1
    assert findings[0].title == "higher"
    assert findings[0].severity == "high"


def test_independent_sources_are_not_collapsed_without_shared_key():
    findings, suppressed = deduplicate_findings(
        [
            finding(
                "interaction",
                "high",
                dedupe_key=None,
                source="curated",
            ),
            finding(
                "interaction",
                "high",
                dedupe_key=None,
                source="official label",
            ),
        ]
    )

    assert suppressed == 0
    assert len(findings) == 2
