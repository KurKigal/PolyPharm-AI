from agents.interaction_agent import InteractionAgent
from agents.lab_risk_agent import LabRiskAgent
from providers.local_json_provider import LocalJsonInteractionProvider


def test_lab_risk_agent_outputs_english(high_risk_patient):
    findings = LabRiskAgent().analyze(high_risk_patient, new_medication="metformin", language="en")
    assert findings
    assert any("renal" in finding.title.lower() or "polypharmacy" in finding.title.lower() for finding in findings)


def test_interaction_rule_uses_requested_language(tmp_path, healthy_patient):
    import json
    path = tmp_path / "rules.json"
    path.write_text(json.dumps([{
        "drug_a": "warfarin", "drug_b": "aspirin", "severity": "high",
        "description": {"tr": "Kanama riski", "en": "Bleeding risk"},
        "recommendation": {"tr": "INR takibi", "en": "Monitor INR"},
    }]), encoding="utf-8")
    healthy_patient.current_medications = ["warfarin"]
    agent = InteractionAgent(rules_provider=LocalJsonInteractionProvider(path))
    finding = agent.analyze(healthy_patient, "aspirin", language="en")[0]
    assert finding.description == "Bleeding risk"
    assert finding.recommendation == "Monitor INR"
    assert "interaction" in finding.title.lower()


def test_legacy_string_rules_still_work(tmp_path, healthy_patient):
    import json
    path = tmp_path / "rules.json"
    path.write_text(json.dumps([{
        "drug_a": "warfarin", "drug_b": "aspirin", "severity": "high",
        "description": "Legacy text", "recommendation": "Legacy recommendation",
    }]), encoding="utf-8")
    healthy_patient.current_medications = ["warfarin"]
    agent = InteractionAgent(rules_provider=LocalJsonInteractionProvider(path))
    finding = agent.analyze(healthy_patient, "aspirin", language="en")[0]
    assert finding.description == "Legacy text"
