import json

import pytest

from providers.local_json_provider import LocalJsonInteractionProvider


def test_loads_and_normalizes_rules_from_file(tmp_path):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "drug_a": "Warfarin",
                    "drug_b": "Aspirin",
                    "severity": "high",
                }
            ]
        ),
        encoding="utf-8",
    )

    provider = LocalJsonInteractionProvider(
        rules_path
    )
    rule = provider.get_interaction_rules()[0]

    assert rule["drug_a"] == "Warfarin"
    assert rule["drug_b"] == "Aspirin"
    assert rule["rule_id"] == "DDI-aspirin-warfarin"
    assert rule["rule_version"] == "1.0.0"
    assert rule["category"] == "drug_interaction"
    assert rule["evidence_type"] == "curated_rule"
    assert rule["evidence_reference"] == "polypharm-curated-ddi@1.0.0"


def test_missing_file_returns_empty_list(tmp_path):
    provider = LocalJsonInteractionProvider(
        tmp_path / "missing.json"
    )
    assert provider.get_interaction_rules() == []


def test_non_list_payload_raises(tmp_path):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            {
                "not": "a list",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        LocalJsonInteractionProvider(
            rules_path
        ).get_interaction_rules()


def test_non_object_rule_raises(tmp_path):
    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                "invalid",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError
    ):
        LocalJsonInteractionProvider(
            rules_path
        ).get_interaction_rules()


def test_default_project_manifest_and_rules_are_versioned():
    provider = LocalJsonInteractionProvider()
    rules = provider.get_interaction_rules()

    assert provider.dataset_id == "polypharm-curated-ddi"
    assert provider.dataset_version == "1.0.0"
    assert len(rules) >= 20

    for rule in rules:
        assert rule["drug_a"]
        assert rule["drug_b"]
        assert rule["severity"] in {
            "low",
            "medium",
            "high",
            "critical",
        }
        assert rule["rule_id"]
        assert rule["rule_version"]
        assert rule["category"] == "drug_interaction"
        assert rule["evidence_type"] == "curated_rule"
