import pytest

from agents.gemini_explainer import GeminiExplainer
from agents.orchestrator import Orchestrator
from models.schemas import DrugInfo, PrescriptionRequest
from providers.rxnorm_provider import DEFAULT_DB_PATH


def make_orchestrator(**kwargs) -> Orchestrator:
    kwargs.setdefault("use_openfda", False)
    kwargs.setdefault("use_ai_summary", False)
    return Orchestrator(**kwargs)


def test_low_risk_patient_scores_high(healthy_patient):
    result = make_orchestrator().analyze(
        PrescriptionRequest(
            patient=healthy_patient,
            new_medication="loratadine",
        ),
        language="en",
    )

    assert result.safety_score >= 85
    assert result.risk_level == "low"
    assert result.score_breakdown.final_score == result.safety_score
    assert result.ai_summary is None


def test_high_risk_patient_aggregates_findings_and_score_provenance(
    high_risk_patient,
):
    result = make_orchestrator().analyze(
        PrescriptionRequest(
            patient=high_risk_patient,
            new_medication="aspirin",
        ),
        language="en",
    )

    agents = {
        finding.agent
        for finding in result.findings
    }

    assert "InteractionAgent" in agents
    assert "LabRiskAgent" in agents
    assert result.safety_score < 60

    assert any(
        "risk" in finding.title.lower()
        or "interaction" in finding.title.lower()
        for finding in result.findings
    )

    assert len(result.score_breakdown.contributions) == len(result.findings)
    assert result.score_breakdown.final_score == result.safety_score

    for index, contribution in enumerate(
        result.score_breakdown.contributions
    ):
        finding = result.findings[index]
        assert contribution.finding_index == index
        assert contribution.title == finding.title
        assert contribution.severity == finding.severity
        assert contribution.source == finding.source
        assert contribution.agent == finding.agent


def test_findings_sorted_by_severity(high_risk_patient):
    result = make_orchestrator().analyze(
        PrescriptionRequest(
            patient=high_risk_patient,
            new_medication="aspirin",
        )
    )

    order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    severities = [
        order[finding.severity]
        for finding in result.findings
    ]

    assert severities == sorted(severities)


def test_report_is_localized_to_selected_language(high_risk_patient):
    request = PrescriptionRequest(
        patient=high_risk_patient,
        new_medication="aspirin",
    )

    en = make_orchestrator().analyze(
        request,
        language="en",
    )
    tr = make_orchestrator().analyze(
        request,
        language="tr",
    )

    assert "Prescription Safety Report" in en.markdown_report
    assert "Score Breakdown" in en.markdown_report

    assert "Reçete Güvenlik Raporu" in tr.markdown_report
    assert "Skor Dökümü" in tr.markdown_report


@pytest.mark.skipif(
    not DEFAULT_DB_PATH.exists(),
    reason="rxnorm.db not built",
)
def test_drug_info_populated_from_rxnorm(healthy_patient):
    result = make_orchestrator().analyze(
        PrescriptionRequest(
            patient=healthy_patient,
            new_medication="Coumadin",
        )
    )

    assert result.new_drug_info is not None
    assert result.new_drug_info.ingredients == ["warfarin"]


def test_boxed_warning_localizes(healthy_patient):
    orchestrator = make_orchestrator()

    drug_info = DrugInfo(
        query_name="warfarin",
        openfda_found=True,
        boxed_warning="WARNING: bleeding risk",
    )

    en = orchestrator._openfda_findings(
        drug_info,
        language="en",
    )
    tr = orchestrator._openfda_findings(
        drug_info,
        language="tr",
    )

    assert en[0].severity == "high"
    assert "boxed warning" in en[0].title.lower()
    assert "kutulu uyarı" in tr[0].title.lower()


def test_ai_summary_receives_language(healthy_patient):
    class FakeExplainer(GeminiExplainer):
        def __init__(self):
            super().__init__(api_key="fake")
            self.model = "fake-model"
            self.language = None

        def generate_summary(self, **kwargs):
            self.language = kwargs["language"]
            return "AI summary"

    explainer = FakeExplainer()

    orchestrator = Orchestrator(
        use_openfda=False,
        use_ai_summary=True,
        gemini_explainer=explainer,
    )

    result = orchestrator.analyze(
        PrescriptionRequest(
            patient=healthy_patient,
            new_medication="aspirin",
        ),
        language="en",
    )

    assert explainer.language == "en"
    assert result.ai_summary == "AI summary"
    assert result.ai_model == "fake-model"
