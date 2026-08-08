from __future__ import annotations

import re

from models.schemas import RiskFinding

SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def _fallback_key(finding: RiskFinding) -> str:
    """Build a conservative key when an agent did not provide one.

    Source and agent are included deliberately so findings from independent
    evidence sources are not silently collapsed.
    """

    title = re.sub(r"\s+", " ", finding.title.strip().lower())
    source = re.sub(r"\s+", " ", finding.source.strip().lower())
    agent = finding.agent.strip().lower()
    return f"{finding.category}|{agent}|{source}|{title}"


def finding_dedupe_key(finding: RiskFinding) -> str:
    explicit = (finding.dedupe_key or "").strip().lower()
    return explicit or _fallback_key(finding)


def deduplicate_findings(
    findings: list[RiskFinding],
) -> tuple[list[RiskFinding], int]:
    """Suppress exact logical duplicates while preserving independent evidence.

    Duplicate identity is controlled by ``dedupe_key``. If two findings share
    the same key, the more severe finding is retained. Equal-severity findings
    keep the first occurrence for deterministic ordering.
    """

    if not findings:
        return [], 0

    retained: list[RiskFinding] = []
    index_by_key: dict[str, int] = {}
    suppressed = 0

    for finding in findings:
        key = finding_dedupe_key(finding)

        if key not in index_by_key:
            index_by_key[key] = len(retained)
            retained.append(finding)
            continue

        suppressed += 1
        existing_index = index_by_key[key]
        existing = retained[existing_index]

        if SEVERITY_RANK.get(finding.severity, 0) > SEVERITY_RANK.get(
            existing.severity,
            0,
        ):
            retained[existing_index] = finding

    return retained, suppressed
