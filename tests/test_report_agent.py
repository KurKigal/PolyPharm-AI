from agents.report_agent import ReportAgent
from models.schemas import DrugInfo, RiskFinding


def finding(severity: str, language: str = "tr") -> RiskFinding:
    if language == "en":
        return RiskFinding(title="Test finding", severity=severity, description="Description", recommendation="Recommendation")
    return RiskFinding(title="Test bulgusu", severity=severity, description="Açıklama", recommendation="Öneri")


def test_summary_without_findings_is_localized():
    agent = ReportAgent()
    assert "risk bulunmadı" in agent.generate_summary([], risk_level="low", language="tr").lower()
    assert "no explicit risk" in agent.generate_summary([], risk_level="low", language="en").lower()


def test_summary_prioritizes_high_findings():
    summary = ReportAgent().generate_summary([finding("high"), finding("medium")], risk_level="high", language="en")
    assert "high-priority" in summary.lower()


def test_markdown_report_english_contains_drug_info_and_ai_summary(healthy_patient):
    drug_info = DrugInfo(query_name="Coumadin", normalized_name="Coumadin", rxcui="202421", is_brand=True, ingredients=["warfarin"], source="RxNorm (local)")
    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient, new_medication="Coumadin", safety_score=65, risk_level="medium",
        findings=[finding("medium", "en")], summary="Summary", drug_info=drug_info,
        ai_summary="AI evaluation text", language="en",
    )
    assert "Drug Information (External Sources)" in report
    assert "202421" in report
    assert "AI-Assisted Evaluation" in report
    assert "Moderate Risk" in report


def test_markdown_report_turkish_without_optional_sections(healthy_patient):
    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient, new_medication="aspirin", safety_score=100, risk_level="low",
        findings=[], summary="Özet", language="tr",
    )
    assert "İlaç Bilgisi" not in report
    assert "Yapay Zeka Değerlendirmesi" not in report
    assert "Belirgin bir risk bulgusu tespit edilmedi." in report
    assert "Düşük Risk" in report
