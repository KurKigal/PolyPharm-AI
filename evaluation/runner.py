from __future__ import annotations

import argparse
import json
from pathlib import Path

from agents.orchestrator import Orchestrator
from core.scoring_policy import DEFAULT_SCORING_POLICY
from evaluation.metrics import evaluate_case, summarize_evaluation
from evaluation.models import (
    CaseEvaluation,
    EvaluationDataset,
)
from evaluation.reporting import summary_to_markdown
from models.schemas import PrescriptionRequest, RiskFinding, ScoreBreakdown

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = PROJECT_ROOT / "evaluation" / "cases.json"


def _preflight() -> None:
    required_finding_fields = {
        "category",
        "evidence_type",
        "rule_id",
        "rule_version",
        "evidence_reference",
        "dedupe_key",
    }
    missing_finding_fields = (
        required_finding_fields
        - set(RiskFinding.model_fields)
    )

    required_breakdown_fields = {
        "policy_version",
        "duplicates_suppressed",
        "category_penalties",
    }
    missing_breakdown_fields = (
        required_breakdown_fields
        - set(ScoreBreakdown.model_fields)
    )

    if missing_finding_fields or missing_breakdown_fields:
        missing = sorted(
            missing_finding_fields
            | missing_breakdown_fields
        )
        raise RuntimeError(
            "Stage 5 requires the Stage 4 provenance/scoring schema. "
            f"Missing fields: {', '.join(missing)}"
        )


def load_dataset(
    path: Path = DEFAULT_CASES_PATH,
) -> EvaluationDataset:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )
    return EvaluationDataset.model_validate(
        payload
    )


def run_evaluation(
    dataset: EvaluationDataset,
) -> tuple:
    _preflight()

    orchestrator = Orchestrator(
        use_openfda=False,
        use_ai_summary=False,
    )

    case_results: list[CaseEvaluation] = []

    for case in dataset.cases:
        try:
            result = orchestrator.analyze(
                PrescriptionRequest(
                    patient=case.patient,
                    new_medication=case.new_medication,
                ),
                language=case.language,
            )

            case_results.append(
                evaluate_case(
                    case,
                    result,
                )
            )
        except Exception as exc:
            case_results.append(
                CaseEvaluation(
                    case_id=case.id,
                    passed=False,
                    expected_rule_ids=case.expected_rule_ids,
                    actual_rule_ids=[],
                    matched_rule_ids=[],
                    missing_rule_ids=case.expected_rule_ids,
                    unexpected_findings=[],
                    expected_risk_level=case.expected_risk_level,
                    actual_risk_level="critical",
                    expected_score_min=(
                        case.expected_score.min
                        if case.expected_score
                        else None
                    ),
                    expected_score_max=(
                        case.expected_score.max
                        if case.expected_score
                        else None
                    ),
                    actual_score=0,
                    risk_level_match=False,
                    score_match=False,
                    finding_expectations_match=False,
                    execution_error=f"{type(exc).__name__}: {exc}",
                )
            )

    summary = summarize_evaluation(
        dataset_id=dataset.dataset_id,
        dataset_version=dataset.dataset_version,
        scoring_policy_version=DEFAULT_SCORING_POLICY.version,
        cases=case_results,
    )

    return summary, case_results


def _print_summary(summary) -> None:
    print()
    print("PolyPharm AI synthetic evaluation")
    print("=" * 36)
    print(
        f"Dataset: {summary.dataset_id}@{summary.dataset_version}"
    )
    print(
        f"Scoring policy: {summary.scoring_policy_version}"
    )
    print(
        f"Cases: {summary.passed_cases}/{summary.total_cases} passed "
        f"({summary.case_pass_rate * 100:.1f}%)"
    )
    print(
        "Expected-rule recall: "
        f"{summary.expected_rule_recall * 100:.1f}% "
        f"({summary.matched_rule_count}/{summary.expected_rule_count})"
    )
    print(
        "Risk-level agreement: "
        f"{summary.risk_level_accuracy * 100:.1f}%"
    )
    print(
        "Score-range agreement: "
        f"{summary.score_range_accuracy * 100:.1f}%"
    )
    print(
        f"Unexpected findings: {summary.unexpected_finding_count}"
    )
    print(
        f"Duplicates suppressed: {summary.duplicates_suppressed}"
    )

    failures = [
        case
        for case in summary.cases
        if not case.passed
    ]

    if failures:
        print()
        print("Failed cases")
        print("-" * 36)

        for case in failures:
            print(
                f"- {case.case_id}: "
                f"missing={case.missing_rule_ids}, "
                f"unexpected={case.unexpected_findings}, "
                f"risk={case.expected_risk_level}->{case.actual_risk_level}, "
                f"score={case.expected_score_min}-{case.expected_score_max}"
                f"->{case.actual_score}"
            )
            if case.execution_error:
                print(
                    f"  error={case.execution_error}"
                )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the deterministic PolyPharm AI synthetic evaluation suite."
        )
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to the synthetic evaluation dataset.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON result output path.",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Optional Markdown report output path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any evaluation case fails.",
    )
    args = parser.parse_args()

    dataset = load_dataset(
        args.cases
    )
    summary, _ = run_evaluation(
        dataset
    )

    _print_summary(
        summary
    )

    if args.output is not None:
        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.output.write_text(
            json.dumps(
                summary.model_dump(),
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if args.markdown is not None:
        args.markdown.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.markdown.write_text(
            summary_to_markdown(
                dataset,
                summary,
            ),
            encoding="utf-8",
        )

    if args.strict and summary.failed_cases:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
