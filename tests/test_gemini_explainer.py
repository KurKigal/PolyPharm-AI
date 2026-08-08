from agents.gemini_explainer import GeminiExplainer
from models.schemas import RiskFinding


class FakeModels:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error
        self.last_kwargs = None

    def generate_content(self, **kwargs):
        self.last_kwargs = kwargs
        if self.error:
            raise self.error
        text = self.text
        class Response:
            pass
        response = Response()
        response.text = text
        return response


class FakeClient:
    def __init__(self, text=None, error=None):
        self.models = FakeModels(text=text, error=error)


def finding(language="tr") -> RiskFinding:
    if language == "en":
        return RiskFinding(title="warfarin - aspirin interaction", severity="high", description="Bleeding risk", recommendation="Monitor INR")
    return RiskFinding(title="warfarin - aspirin etkileşimi", severity="high", description="Kanama riski", recommendation="INR takibi")


def test_not_available_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert not GeminiExplainer(api_key=None).available


def test_returns_none_when_unavailable(monkeypatch, healthy_patient):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    summary = GeminiExplainer(api_key=None).generate_summary(
        patient=healthy_patient, new_medication="aspirin", findings=[finding()], safety_score=65, risk_level="medium", language="tr"
    )
    assert summary is None


def test_generates_english_summary_with_english_prompt(healthy_patient):
    client = FakeClient(text="Summary text")
    explainer = GeminiExplainer(client=client)
    summary = explainer.generate_summary(
        patient=healthy_patient, new_medication="aspirin", findings=[finding("en")], safety_score=65, risk_level="medium", language="en"
    )
    assert summary == "Summary text"
    prompt = client.models.last_kwargs["contents"]
    instruction = client.models.last_kwargs["config"]["system_instruction"]
    assert "Prescription safety analysis data" in prompt
    assert "Moderate Risk" in prompt
    assert "Write in English" in instruction


def test_generates_turkish_summary_with_turkish_prompt(healthy_patient):
    client = FakeClient(text="Özet metni")
    explainer = GeminiExplainer(client=client)
    summary = explainer.generate_summary(
        patient=healthy_patient, new_medication="aspirin", findings=[finding()], safety_score=65, risk_level="medium", language="tr"
    )
    assert summary == "Özet metni"
    assert "Türkçe yaz" in client.models.last_kwargs["config"]["system_instruction"]


def test_api_error_returns_none(healthy_patient):
    explainer = GeminiExplainer(client=FakeClient(error=RuntimeError("quota")))
    assert explainer.generate_summary(patient=healthy_patient, new_medication="aspirin", findings=[], safety_score=100, risk_level="low", language="en") is None
