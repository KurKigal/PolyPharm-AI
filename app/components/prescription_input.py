from __future__ import annotations

import streamlit as st

from app.components.common import esc
from app.i18n import Translator
from providers.rxnorm_provider import RxNormProvider


def render_prescription_input(
    t: Translator,
    interaction_rules: list[dict],
    rxnorm: RxNormProvider,
) -> str:
    available_drugs = sorted(
        {item["drug_a"] for item in interaction_rules if "drug_a" in item}
        | {item["drug_b"] for item in interaction_rules if "drug_b" in item}
        | {"metformin", "atorvastatin", "ibuprofen", "furosemide", "lisinopril"}
    )

    st.header(t("prescription.header"))

    list_option = t("prescription.mode.list")
    manual_option = t("prescription.mode.manual")
    input_mode = st.radio(
        t("prescription.mode.label"),
        [list_option, manual_option],
        horizontal=True,
    )

    if input_mode == list_option:
        return st.selectbox(
            t("prescription.new_medication"),
            available_drugs,
            index=available_drugs.index("aspirin") if "aspirin" in available_drugs else 0,
        )

    new_medication = st.text_input(
        t("prescription.new_medication"),
        value="aspirin",
        help=t("prescription.new_medication_help"),
    )

    _render_rxnorm_feedback(new_medication, rxnorm, t)
    return new_medication


def _render_rxnorm_feedback(
    new_medication: str,
    rxnorm: RxNormProvider,
    t: Translator,
) -> None:
    if not new_medication.strip() or not rxnorm.available:
        return

    lookup = rxnorm.lookup(new_medication)
    if lookup is not None:
        if lookup.is_brand:
            ingredients = ", ".join(lookup.ingredients) or t("common.unknown")
            message = t(
                "prescription.rxnorm_brand",
                name=lookup.name,
                ingredients=ingredients,
                rxcui=lookup.rxcui,
            )
        else:
            message = t(
                "prescription.rxnorm_match",
                name=lookup.name,
                rxcui=lookup.rxcui,
            )

        st.markdown(
            f'<div class="pp-note">🔎 {esc(message)}</div>',
            unsafe_allow_html=True,
        )
        return

    suggestions = rxnorm.suggest(new_medication, limit=5)
    if suggestions:
        message = t(
            "prescription.rxnorm_suggestions",
            suggestions=", ".join(suggestions),
        )
    else:
        message = t("prescription.rxnorm_no_match")

    st.markdown(
        f'<div class="pp-note warn">{esc(message)}</div>',
        unsafe_allow_html=True,
    )
