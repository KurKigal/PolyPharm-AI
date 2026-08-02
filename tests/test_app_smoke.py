from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app" / "main.py"


def start_app(monkeypatch) -> AppTest:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENFDA_API_KEY", raising=False)
    app = AppTest.from_file(str(APP_PATH), default_timeout=15)
    app.run()
    return app


def test_app_starts_without_errors(monkeypatch):
    app = start_app(monkeypatch)

    assert not app.exception
    assert app.button[0].label == "Analiz Et"


def test_offline_analysis_flow(monkeypatch):
    app = start_app(monkeypatch)
    openfda_toggle = next(
        toggle for toggle in app.toggle if toggle.label == "openFDA etiket verisi"
    )

    openfda_toggle.set_value(False)
    app.button[0].click().run()

    assert not app.exception
    assert len(app.tabs) == 4
    assert app.get("download_button")[0].label == "Markdown raporu indir"
