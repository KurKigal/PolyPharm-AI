from agents.interaction_agent import InteractionAgent
from agents.lab_risk_agent import LabRiskAgent
from providers.local_json_provider import LocalJsonInteractionProvider


def test_lab_finding_has_rule_provenance(healthy_patient):
    patient = healthy_patient.model_copy(
        update={
            "lab_values": healthy_patient.lab_values.model_copy(
                update={
                    "egfr": 45,
                }
            )
        }
    )

    finding = LabRiskAgent().analyze(
        patient,
        new_medication="metformin",
        language="en",
    )[0]

    assert finding.category == "renal"
    assert finding.evidence_type == "prototype_rule"
    assert finding.rule_id == "LAB-RENAL-MODERATE"
    assert finding.rule_version == "1.0.0"
    assert finding.evidence_reference


def test_curated_interaction_has_dataset_provenance(
    tmp_path,
    healthy_patient,
):
    import json

    rules_path = tmp_path / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "drug_a": "warfarin",
                    "drug_b": "aspirin",
                    "severity": "high",
                    "description": {
                        "en": "Bleeding risk",
                        "tr": "Kanama riski",
                    },
                    "recommendation": {
                        "en": "Review therapy",
                        "tr": "Tedaviyi değerlendir",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    healthy_patient.current_medications = [
        "warfarin"
    ]

    agent = InteractionAgent(
        rules_provider=LocalJsonInteractionProvider(
            rules_path
        )
    )

    finding = agent.analyze(
        healthy_patient,
        new_medication="aspirin",
        language="en",
    )[0]

    assert finding.category == "drug_interaction"
    assert finding.evidence_type == "curated_rule"
    assert finding.rule_id == "DDI-aspirin-warfarin"
    assert finding.rule_version == "1.0.0"
    assert finding.evidence_reference == "polypharm-curated-ddi@1.0.0"
    assert finding.dedupe_key == "ddi:curated:aspirin|warfarin"
