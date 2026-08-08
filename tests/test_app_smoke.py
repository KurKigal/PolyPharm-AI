from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app" / "main.py"


def start_app(monkeypatch) -> AppTest:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENFDA_API_KEY", raising=False)
    app = AppTest.from_file(str(APP_PATH), default_timeout=15)
    app.run()
    return app


def find_button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def test_app_starts_without_errors_in_english(monkeypatch):
    app = start_app(monkeypatch)

    assert not app.exception
    assert find_button(app, "Analyze")


def test_language_can_switch_to_turkish(monkeypatch):
    app = start_app(monkeypatch)
    language = next(
        selectbox for selectbox in app.selectbox if selectbox.label == "Language / Dil"
    )

    language.set_value("Türkçe").run()

    assert not app.exception
    assert find_button(app, "Analiz Et")


def test_offline_analysis_flow(monkeypatch):
    app = start_app(monkeypatch)
    openfda_toggle = next(
        toggle for toggle in app.toggle if toggle.label == "openFDA label data"
    )

    openfda_toggle.set_value(False)
    find_button(app, "Analyze").click().run()

    assert not app.exception
    assert len(app.tabs) == 4
    assert app.get("download_button")[0].label == "Download Markdown report"
