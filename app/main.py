import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

st.set_page_config(
    page_title="PolyPharm AI",
    page_icon="💊",
    layout="wide",
)

from app.components.analysis_results import render_analysis_results, render_idle_note
from app.components.header import render_header
from app.components.patient_summary import render_patient_summary
from app.components.prescription_input import render_prescription_input
from app.components.sidebar import render_language_selector, render_sidebar
from app.i18n import Translator
from app.runtime import (
    DATA_DIR,
    build_patient,
    get_orchestrator,
    get_rxnorm_provider,
    load_json_file,
)
from app.styles.theme import inject_theme
from models.schemas import PrescriptionRequest

LOGGER = logging.getLogger(__name__)


def main() -> None:
    inject_theme()

    language = render_language_selector()
    t = Translator(language)

    sample_patients = load_json_file(DATA_DIR / "sample_patients.json")
    interaction_rules = load_json_file(DATA_DIR / "demo_interactions.json")
    rxnorm = get_rxnorm_provider()

    render_header(t)

    sidebar = render_sidebar(t, sample_patients, rxnorm)
    new_medication = render_prescription_input(t, interaction_rules, rxnorm)
    render_patient_summary(sidebar, rxnorm, t)

    if not st.button(t("actions.analyze"), type="primary"):
        render_idle_note(t)
        return

    try:
        patient = build_patient(
            age=sidebar.age,
            gender=sidebar.gender,
            current_medications=sidebar.current_medications,
            egfr=sidebar.egfr,
            creatinine=sidebar.creatinine,
            ast=sidebar.ast,
            alt=sidebar.alt,
        )
        request = PrescriptionRequest(
            patient=patient,
            new_medication=new_medication,
        )
        orchestrator = get_orchestrator(
            sidebar.use_openfda,
            sidebar.use_ai_summary,
        )

        with st.spinner(t("analysis.spinner")):
            result = orchestrator.analyze(request, language=language)
    except Exception:
        LOGGER.exception("Prescription safety analysis failed")
        st.error(t("analysis.error"))
        st.caption(t("analysis.error_hint"))
        st.stop()

    render_analysis_results(
        result,
        t=t,
        use_ai_summary=sidebar.use_ai_summary,
    )


main()
