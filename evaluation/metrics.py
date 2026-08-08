from __future__ import annotations

from collections.abc import Iterable

from evaluation.models import (
    CaseEvaluation,
    EvaluationCase,
    EvaluationSummary,
)
from models.schemas import AnalysisResult


def _finding_token(finding) -> str:
    if finding.rule_id:
        return finding.rule_id

    return (
        f"{finding.agent}:{finding.category}:"
        f"{finding.title.strip()}"
    )


def evaluate_case(
    case: EvaluationCase,
    result: AnalysisResult,
) -> CaseEvaluation:
    expected_rule_ids = list(
        dict.fromkeys(case.expected_rule_ids)
    )

    actual_tokens = [
        _finding_token(finding)
        for finding in result.findings
    ]
    actual_rule_ids = [
        finding.rule_id
        for finding in result.findings
        if finding.rule_id
    ]

    expected_set = set(expected_rule_ids)
    actual_rule_set = set(actual_rule_ids)

    matched = sorted(
        expected_set & actual_rule_set
    )
    missing = sorted(
        expected_set - actual_rule_set
    )

    unexpected = sorted(
        token
        for token in actual_tokens
        if token not in expected_set
    )

    finding_expectations_match = (
        not missing
        and (
            case.allow_unexpected_findings
            or not unexpected
        )
    )

    risk_match = (
        case.expected_risk_level is None
        or result.risk_level == case.expected_risk_level
    )

    if case.expected_score is None:
        score_match = True
        score_min = None
        score_max = None
    else:
        score_min = case.expected_score.min
        score_max = case.expected_score.max
        score_match = (
            score_min
            <= result.safety_score
            <= score_max
        )

    passed = (
        finding_expectations_match
        and risk_match
        and score_match
    )

    return CaseEvaluation(
        case_id=case.id,
        passed=passed,
        expected_rule_ids=expected_rule_ids,
        actual_rule_ids=actual_rule_ids,
        matched_rule_ids=matched,
        missing_rule_ids=missing,
        unexpected_findings=unexpected,
        expected_risk_level=case.expected_risk_level,
        actual_risk_level=result.risk_level,
        expected_score_min=score_min,
        expected_score_max=score_max,
        actual_score=result.safety_score,
        risk_level_match=risk_match,
        score_match=score_match,
        finding_expectations_match=finding_expectations_match,
        duplicates_suppressed=result.score_breakdown.duplicates_suppressed,
    )


def summarize_evaluation(
    *,
    dataset_id: str,
    dataset_version: str,
    scoring_policy_version: str,
    cases: Iterable[CaseEvaluation],
) -> EvaluationSummary:
    case_results = list(cases)

    total_cases = len(case_results)
    passed_cases = sum(
        case.passed
        for case in case_results
    )
    failed_cases = total_cases - passed_cases

    expected_rule_count = sum(
        len(case.expected_rule_ids)
        for case in case_results
    )
    matched_rule_count = sum(
        len(case.matched_rule_ids)
        for case in case_results
    )

    risk_cases = sum(
        case.expected_risk_level is not None
        for case in case_results
    )
    risk_matches = sum(
        case.expected_risk_level is not None
        and case.risk_level_match
        for case in case_results
    )

    score_cases = sum(
        case.expected_score_min is not None
        for case in case_results
    )
    score_matches = sum(
        case.expected_score_min is not None
        and case.score_match
        for case in case_results
    )

    unexpected_finding_count = sum(
        len(case.unexpected_findings)
        for case in case_results
    )
    duplicates_suppressed = sum(
        case.duplicates_suppressed
        for case in case_results
    )

    return EvaluationSummary(
        dataset_id=dataset_id,
        dataset_version=dataset_version,
        scoring_policy_version=scoring_policy_version,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_cases,
        case_pass_rate=(
            passed_cases / total_cases
            if total_cases
            else 1.0
        ),
        expected_rule_count=expected_rule_count,
        matched_rule_count=matched_rule_count,
        expected_rule_recall=(
            matched_rule_count / expected_rule_count
            if expected_rule_count
            else 1.0
        ),
        risk_level_cases=risk_cases,
        risk_level_matches=risk_matches,
        risk_level_accuracy=(
            risk_matches / risk_cases
            if risk_cases
            else 1.0
        ),
        score_expectation_cases=score_cases,
        score_matches=score_matches,
        score_range_accuracy=(
            score_matches / score_cases
            if score_cases
            else 1.0
        ),
        unexpected_finding_count=unexpected_finding_count,
        duplicates_suppressed=duplicates_suppressed,
        cases=case_results,
    )
