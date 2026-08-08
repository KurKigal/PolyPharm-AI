from __future__ import annotations

import streamlit as st

from app.components.common import esc
from app.components.sidebar import SidebarState
from app.i18n import Translator, gender_label
from providers.rxnorm_provider import RxNormProvider


def render_patient_summary(
    state: SidebarState,
    rxnorm: RxNormProvider,
    t: Translator,
) -> None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
<div class="pp-card pp-fade" style="animation-delay:.05s">
  <div class="pp-eyebrow">{esc(t("patient_summary.patient_info"))}</div>
  <div class="pp-kv"><span class="k">{esc(t("sidebar.age"))}</span><span class="v pp-mono">{esc(state.age)}</span></div>
  <div class="pp-kv"><span class="k">{esc(t("sidebar.gender"))}</span><span class="v">{esc(gender_label(state.gender, t))}</span></div>
  <div class="pp-kv"><span class="k">{esc(t("patient_summary.medication_count"))}</span><span class="v pp-mono">{len(state.current_medications)}</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        meds_html = _render_medication_rows(state.current_medications, rxnorm, t)
        st.markdown(
            f"""
<div class="pp-card pp-fade" style="animation-delay:.12s">
  <div class="pp-eyebrow">{esc(t("patient_summary.current_medications"))}</div>
  {meds_html}
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
<div class="pp-card pp-fade" style="animation-delay:.19s">
  <div class="pp-eyebrow">{esc(t("patient_summary.lab_values"))}</div>
  <div class="pp-kv"><span class="k">eGFR</span><span class="v pp-mono">{esc(state.egfr)}</span></div>
  <div class="pp-kv"><span class="k">{esc(t("sidebar.creatinine"))}</span><span class="v pp-mono">{esc(state.creatinine)}</span></div>
  <div class="pp-kv"><span class="k">AST</span><span class="v pp-mono">{esc(state.ast)}</span></div>
  <div class="pp-kv"><span class="k">ALT</span><span class="v pp-mono">{esc(state.alt)}</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")


def _render_medication_rows(
    medications: list[str],
    rxnorm: RxNormProvider,
    t: Translator,
) -> str:
    if not medications:
        return f'<div class="pp-med">{esc(t("patient_summary.no_medications"))}</div>'

    rows = []
    for medication in medications:
        ingredient_chip = ""
        if rxnorm.available:
            lookup = rxnorm.lookup(medication)
            if lookup is not None and lookup.is_brand and lookup.ingredients:
                ingredient_chip = (
                    f'<span class="ing">→ {esc(", ".join(lookup.ingredients))}</span>'
                )
        rows.append(f'<div class="pp-med">{esc(medication)} {ingredient_chip}</div>')

    return "".join(rows)
