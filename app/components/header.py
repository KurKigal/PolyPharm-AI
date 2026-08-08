import streamlit as st

from app.components.common import esc
from app.i18n import Translator


def render_header(t: Translator) -> None:
    st.markdown(
        f"""
<div class="pp-header pp-fade">
  <div class="pp-logo">✚</div>
  <div>
    <div class="pp-title">PolyPharm AI</div>
    <div class="pp-sub">{esc(t("app.subtitle"))}</div>
  </div>
  <div class="pp-dept">{esc(t("app.department"))}</div>
</div>
<div class="pp-banner pp-fade" style="animation-delay:.08s">
  ⚕️ {esc(t("app.disclaimer"))}
</div>
""",
        unsafe_allow_html=True,
    )
