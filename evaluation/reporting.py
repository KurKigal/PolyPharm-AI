from __future__ import annotations

from evaluation.models import EvaluationDataset, EvaluationSummary


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def summary_to_markdown(
    dataset: EvaluationDataset,
    summary: EvaluationSummary,
) -> str:
    lines = [
        "# PolyPharm AI Synthetic Evaluation Report",
        "",
        (
            "> This is a software regression/behavioral evaluation over "
            "synthetic cases. It is **not clinical validation** and does not "
            "measure real-world diagnostic or prescribing accuracy."
        ),
        "",
        "## Evaluation Metadata",
        "",
        f"- Dataset: `{summary.dataset_id}@{summary.dataset_version}`",
        f"- Scoring policy: `{summary.scoring_policy_version}`",
        f"- Cases: **{summary.total_cases}**",
        f"- Clinical ground truth: **{dataset.clinical_ground_truth}**",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Case pass rate | {_percent(summary.case_pass_rate)} |",
        f"| Expected-rule recall | {_percent(summary.expected_rule_recall)} |",
        f"| Risk-level agreement | {_percent(summary.risk_level_accuracy)} |",
        f"| Score-range agreement | {_percent(summary.score_range_accuracy)} |",
        f"| Unexpected findings | {summary.unexpected_finding_count} |",
        f"| Duplicate findings suppressed | {summary.duplicates_suppressed} |",
        "",
        "## Limitations",
        "",
        dataset.limitations,
        "",
    ]

    failures = [
        case
        for case in summary.cases
        if not case.passed
    ]

    lines.extend(
        [
            "## Failed Cases",
            "",
        ]
    )

    if not failures:
        lines.append("All synthetic evaluation cases passed.")
    else:
        lines.extend(
            [
                "| Case | Missing rules | Unexpected findings | Risk | Score |",
                "|---|---|---|---|---|",
            ]
        )

        for case in failures:
            expected_score = (
                f"{case.expected_score_min}-{case.expected_score_max}"
                if case.expected_score_min is not None
                else "-"
            )
            risk = (
                f"{case.expected_risk_level} → {case.actual_risk_level}"
                if case.expected_risk_level is not None
                else case.actual_risk_level
            )

            lines.append(
                "| "
                + " | ".join(
                    [
                        case.case_id,
                        ", ".join(case.missing_rule_ids) or "-",
                        ", ".join(case.unexpected_findings) or "-",
                        risk,
                        f"{expected_score} → {case.actual_score}",
                    ]
                )
                + " |"
            )

    lines.append("")
    return "\n".join(lines)
