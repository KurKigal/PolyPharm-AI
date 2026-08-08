from pathlib import Path

from evaluation.runner import load_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_evaluation_dataset_is_valid_and_nonclinical():
    dataset = load_dataset(
        PROJECT_ROOT / "evaluation" / "cases.json"
    )

    assert dataset.dataset_id == "polypharm-synthetic-evaluation"
    assert dataset.dataset_version == "1.0.0"
    assert dataset.clinical_ground_truth is False
    assert len(dataset.cases) >= 40


def test_case_ids_are_unique():
    dataset = load_dataset()

    ids = [
        case.id
        for case in dataset.cases
    ]

    assert len(ids) == len(set(ids))


def test_all_curated_ddi_rules_have_positive_control_cases():
    dataset = load_dataset()

    ddi_cases = [
        case
        for case in dataset.cases
        if "ddi" in case.tags
    ]

    assert len(ddi_cases) == 29

    for case in ddi_cases:
        assert len(case.expected_rule_ids) == 1
        assert case.expected_rule_ids[0].startswith("DDI-")


def test_all_cases_have_score_and_risk_expectations():
    dataset = load_dataset()

    for case in dataset.cases:
        assert case.expected_risk_level is not None
        assert case.expected_score is not None
