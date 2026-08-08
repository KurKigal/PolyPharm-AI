from types import SimpleNamespace

from evaluation.metrics import evaluate_case, summarize_evaluation
from evaluation.models import EvaluationCase
from models.schemas import LabValues, Patient


def make_case() -> EvaluationCase:
    return EvaluationCase(
        id="test-case",
        patient=Patient(
            age=40,
            gender="female",
            current_medications=["warfarin"],
            lab_values=LabValues(
                egfr=95,
                creatinine=0.9,
                ast=25,
                alt=22,
            ),
        ),
        new_medication="aspirin",
        expected_rule_ids=["DDI-aspirin-warfarin"],
        expected_risk_level="medium",
        expected_score={
            "min": 65,
            "max": 65,
        },
    )


def fake_result(
    *,
    rule_ids,
    risk_level="medium",
    score=65,
):
    findings = [
        SimpleNamespace(
            rule_id=rule_id,
            agent="InteractionAgent",
            category="drug_interaction",
            title=rule_id,
        )
        for rule_id in rule_ids
    ]

    return SimpleNamespace(
        findings=findings,
        risk_level=risk_level,
        safety_score=score,
        score_breakdown=SimpleNamespace(
            duplicates_suppressed=0
        ),
    )


def test_case_passes_when_all_expectations_match():
    result = evaluate_case(
        make_case(),
        fake_result(
            rule_ids=[
                "DDI-aspirin-warfarin",
            ]
        ),
    )

    assert result.passed is True
    assert result.missing_rule_ids == []
    assert result.unexpected_findings == []


def test_unexpected_finding_fails_strict_case():
    result = evaluate_case(
        make_case(),
        fake_result(
            rule_ids=[
                "DDI-aspirin-warfarin",
                "DDI-unexpected",
            ]
        ),
    )

    assert result.passed is False
    assert result.unexpected_findings == [
        "DDI-unexpected"
    ]


def test_summary_metrics_are_aggregated():
    case = make_case()

    passed = evaluate_case(
        case,
        fake_result(
            rule_ids=[
                "DDI-aspirin-warfarin",
            ]
        ),
    )
    failed = evaluate_case(
        case.model_copy(
            update={
                "id": "failed-case",
            }
        ),
        fake_result(
            rule_ids=[],
            risk_level="low",
            score=100,
        ),
    )

    summary = summarize_evaluation(
        dataset_id="test",
        dataset_version="1.0",
        scoring_policy_version="test-policy",
        cases=[
            passed,
            failed,
        ],
    )

    assert summary.total_cases == 2
    assert summary.passed_cases == 1
    assert summary.failed_cases == 1
    assert summary.case_pass_rate == 0.5
    assert summary.expected_rule_recall == 0.5
    assert summary.risk_level_accuracy == 0.5
    assert summary.score_range_accuracy == 0.5
