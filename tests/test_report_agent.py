from agents.report_agent import ReportAgent
from agents.scoring_agent import ScoringAgent
from models.schemas import DrugInfo, RiskFinding


def finding(
    severity: str,
    language: str = "tr",
) -> RiskFinding:
    if language == "en":
        return RiskFinding(
            title="Test finding",
            severity=severity,
            description="Description",
            recommendation="Recommendation",
            source="Test source",
            agent="TestAgent",
        )

    return RiskFinding(
        title="Test bulgusu",
        severity=severity,
        description="Açıklama",
        recommendation="Öneri",
        source="Test kaynağı",
        agent="TestAgent",
    )


def test_summary_without_findings_is_localized():
    agent = ReportAgent()

    assert "risk bulunmadı" in agent.generate_summary(
        [],
        risk_level="low",
        language="tr",
    ).lower()

    assert "no explicit risk" in agent.generate_summary(
        [],
        risk_level="low",
        language="en",
    ).lower()


def test_summary_prioritizes_high_findings():
    summary = ReportAgent().generate_summary(
        [
            finding("high"),
            finding("medium"),
        ],
        risk_level="high",
        language="en",
    )

    assert "high-priority" in summary.lower()


def test_markdown_report_english_contains_score_breakdown_drug_info_and_ai_summary(
    healthy_patient,
):
    finding_en = finding(
        "medium",
        "en",
    )
    safety_score, _, score_breakdown = ScoringAgent().calculate_score(
        [finding_en]
    )

    drug_info = DrugInfo(
        query_name="Coumadin",
        normalized_name="Coumadin",
        rxcui="202421",
        is_brand=True,
        ingredients=["warfarin"],
        source="RxNorm (local)",
    )

    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient,
        new_medication="Coumadin",
        safety_score=safety_score,
        risk_level="medium",
        findings=[finding_en],
        summary="Summary",
        drug_info=drug_info,
        ai_summary="AI evaluation text",
        score_breakdown=score_breakdown,
        language="en",
    )

    assert "Drug Information (External Sources)" in report
    assert "202421" in report
    assert "AI-Assisted Evaluation" in report
    assert "Moderate Risk" in report

    assert "## Score Breakdown" in report
    assert "Starting score: **100**" in report
    assert "Total penalty: **-20**" in report
    assert "| Test finding | medium | -20 | Test source | TestAgent |" in report


def test_markdown_report_turkish_contains_score_breakdown_without_optional_sections(
    healthy_patient,
):
    safety_score, _, score_breakdown = ScoringAgent().calculate_score([])

    report = ReportAgent().generate_markdown_report(
        patient=healthy_patient,
        new_medication="aspirin",
        safety_score=safety_score,
        risk_level="low",
        findings=[],
        summary="Özet",
        score_breakdown=score_breakdown,
        language="tr",
    )

    assert "İlaç Bilgisi" not in report
    assert "Yapay Zeka Değerlendirmesi" not in report
    assert "Belirgin bir risk bulgusu tespit edilmedi." in report
    assert "Düşük Risk" in report

    assert "## Skor Dökümü" in report
    assert "Başlangıç skoru: **100**" in report
    assert "Skor kesintisi uygulanmadı." in report
