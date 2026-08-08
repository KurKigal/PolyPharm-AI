from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from agents.gemini_explainer import GeminiExplainer
from app.i18n import DEFAULT_LANGUAGE, Translator, gender_label
from providers.rxnorm_provider import RxNormProvider

LANGUAGE_OPTIONS = {
    "English": "en",
    "Türkçe": "tr",
}


@dataclass(frozen=True)
class SidebarState:
    age: int
    gender: str
    current_medications: list[str]
    egfr: float
    creatinine: float
    ast: float
    alt: float
    use_openfda: bool
    use_ai_summary: bool


def render_language_selector() -> str:
    labels = list(LANGUAGE_OPTIONS)
    default_label = next(
        label for label, code in LANGUAGE_OPTIONS.items() if code == DEFAULT_LANGUAGE
    )
    selected = st.sidebar.selectbox(
        "Language / Dil",
        labels,
        index=labels.index(default_label),
        key="app_language",
    )
    return LANGUAGE_OPTIONS[selected]


def render_sidebar(
    t: Translator,
    sample_patients: list[dict],
    rxnorm: RxNormProvider,
) -> SidebarState:
    st.sidebar.header(t("sidebar.patient_selection"))

    demo_option = t("sidebar.mode.demo")
    manual_option = t("sidebar.mode.manual")
    patient_mode = st.sidebar.radio(
        t("sidebar.mode.label"),
        [demo_option, manual_option],
    )

    if patient_mode == demo_option and sample_patients:
        name_key = "name_en" if t.language == "en" else "name"
        labels = [patient.get(name_key) or patient.get("name", "Demo patient") for patient in sample_patients]
        selected_label = st.sidebar.selectbox(t("sidebar.demo_patient"), labels)
        selected_index = labels.index(selected_label)
        selected_patient = sample_patients[selected_index]

        age = int(selected_patient["age"])
        gender = str(selected_patient["gender"])
        current_medications = list(selected_patient["current_medications"])
        egfr = float(selected_patient["lab_values"]["egfr"])
        creatinine = float(selected_patient["lab_values"]["creatinine"])
        ast = float(selected_patient["lab_values"]["ast"])
        alt = float(selected_patient["lab_values"]["alt"])
    else:
        age = st.sidebar.number_input(
            t("sidebar.age"), min_value=0, max_value=120, value=65
        )

        gender_keys = ["female", "male", "other"]
        gender = st.sidebar.selectbox(
            t("sidebar.gender"),
            gender_keys,
            format_func=lambda value: gender_label(value, t),
        )

        meds_text = st.sidebar.text_area(
            t("sidebar.current_medications"),
            value="warfarin, metformin",
            help=t("sidebar.current_medications_help"),
        )
        current_medications = [
            medication.strip()
            for medication in meds_text.split(",")
            if medication.strip()
        ]

        egfr = st.sidebar.number_input(
            "eGFR", min_value=0.0, max_value=150.0, value=75.0
        )
        creatinine = st.sidebar.number_input(
            t("sidebar.creatinine"), min_value=0.0, max_value=20.0, value=1.0
        )
        ast = st.sidebar.number_input(
            "AST", min_value=0.0, max_value=1000.0, value=30.0
        )
        alt = st.sidebar.number_input(
            "ALT", min_value=0.0, max_value=1000.0, value=30.0
        )

    st.sidebar.divider()
    st.sidebar.header(t("sidebar.data_sources"))

    use_openfda = st.sidebar.toggle(
        t("sidebar.openfda"),
        value=True,
        help=t("sidebar.openfda_help"),
    )
    use_ai_summary = st.sidebar.toggle(
        t("sidebar.gemini"),
        value=GeminiExplainer().available,
        help=t("sidebar.gemini_help"),
    )

    if rxnorm.available:
        st.sidebar.success(t("sidebar.rxnorm_active"))
    else:
        st.sidebar.info(t("sidebar.rxnorm_missing"))

    return SidebarState(
        age=int(age),
        gender=gender,
        current_medications=current_medications,
        egfr=float(egfr),
        creatinine=float(creatinine),
        ast=float(ast),
        alt=float(alt),
        use_openfda=bool(use_openfda),
        use_ai_summary=bool(use_ai_summary),
    )
