import html
import json
import logging
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from agents.gemini_explainer import GeminiExplainer
from agents.orchestrator import Orchestrator
from models.schemas import LabValues, Patient, PrescriptionRequest
from providers.rxnorm_provider import RxNormProvider

DATA_DIR = PROJECT_ROOT / "data"
LOGGER = logging.getLogger(__name__)

st.set_page_config(
    page_title="PolyPharm AI",
    page_icon="💊",
    layout="wide",
)

# --- Tema: beyaz hastane paneli ---------------------------------------------

SEVERITY_META = {
    "critical": {"label": "Kritik", "dot": "#C92A2A", "tint": "#FFF0F0", "ink": "#A61E1E"},
    "high": {"label": "Yüksek", "dot": "#E8590C", "tint": "#FFF4EC", "ink": "#C2410C"},
    "medium": {"label": "Orta", "dot": "#E67700", "tint": "#FFF8E1", "ink": "#9A6700"},
    "low": {"label": "Düşük", "dot": "#1971C2", "tint": "#EDF5FF", "ink": "#1971C2"},
}

RISK_LEVEL_META = {
    "Düşük Risk": {"ink": "#2B8A3E", "tint": "#EBFBEE"},
    "Orta Risk": {"ink": "#9A6700", "tint": "#FFF8E1"},
    "Yüksek Risk": {"ink": "#C2410C", "tint": "#FFF4EC"},
    "Kritik Risk": {"ink": "#A61E1E", "tint": "#FFF0F0"},
}


def inject_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
:root {
  --pp-bg: #F4F8F9;
  --pp-surface: #FFFFFF;
  --pp-ink: #243B53;
  --pp-muted: #627D98;
  --pp-line: #DCE7EC;
  --pp-teal: #0B7285;
  --pp-teal-ink: #095C68;
  --pp-teal-soft: #E3F4F6;
  --pp-shadow: 0 1px 2px rgba(16, 42, 67, .05), 0 6px 18px rgba(16, 42, 67, .06);
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--pp-bg);
  font-family: 'IBM Plex Sans', -apple-system, 'Segoe UI', sans-serif;
  color: var(--pp-ink);
}
.block-container { max-width: 1180px; padding-top: 3rem; }
[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { font-family: 'IBM Plex Sans', sans-serif; letter-spacing: -0.01em; }

/* Kenar çubuğu: beyaz klinik panel */
[data-testid="stSidebar"] {
  background: var(--pp-surface);
  border-right: 1px solid var(--pp-line);
}
[data-testid="stSidebar"] h2 {
  font-size: .78rem; text-transform: uppercase; letter-spacing: .09em;
  color: var(--pp-teal-ink); border-bottom: 2px solid var(--pp-teal-soft);
  padding-bottom: .4rem;
}

/* Kartlar */
.pp-card {
  background: var(--pp-surface);
  border: 1px solid var(--pp-line);
  border-radius: 14px;
  box-shadow: var(--pp-shadow);
  padding: 1.1rem 1.25rem;
  height: 100%;
  transition: transform .18s ease, box-shadow .18s ease;
}
.pp-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(16,42,67,.06), 0 12px 28px rgba(16,42,67,.10);
}
.pp-eyebrow {
  font-size: .72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: var(--pp-teal);
  display: flex; align-items: center; gap: .45rem; margin-bottom: .7rem;
}
.pp-eyebrow::before {
  content: ''; width: 8px; height: 8px; border-radius: 2px; background: var(--pp-teal);
}
.pp-kv { display: flex; justify-content: space-between; gap: 1rem; padding: .3rem 0; border-bottom: 1px dashed var(--pp-line); }
.pp-kv:last-child { border-bottom: none; }
.pp-kv .k { color: var(--pp-muted); font-size: .88rem; }
.pp-kv .v { font-weight: 600; }
.pp-mono { font-family: 'IBM Plex Mono', monospace; font-variant-numeric: tabular-nums; }

/* İlaç satırları */
.pp-med { display: flex; align-items: center; gap: .5rem; padding: .28rem 0; font-size: .92rem; }
.pp-med::before { content: '💊'; font-size: .8rem; }
.pp-med .ing { color: var(--pp-teal-ink); background: var(--pp-teal-soft); border-radius: 999px; padding: .05rem .55rem; font-size: .78rem; font-weight: 600; }

/* Başlık bandı */
.pp-header {
  background: var(--pp-surface);
  border: 1px solid var(--pp-line);
  border-top: 4px solid var(--pp-teal);
  border-radius: 14px;
  box-shadow: var(--pp-shadow);
  padding: 1.1rem 1.4rem;
  display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;
}
.pp-logo {
  width: 48px; height: 48px; border-radius: 12px; flex: 0 0 auto;
  background: var(--pp-teal-soft); color: var(--pp-teal-ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; font-weight: 700;
}
.pp-title { font-size: 1.45rem; font-weight: 700; letter-spacing: -.02em; }
.pp-sub { color: var(--pp-muted); font-size: .92rem; }
.pp-dept {
  margin-left: auto; font-size: .72rem; font-weight: 700;
  letter-spacing: .1em; text-transform: uppercase;
  color: var(--pp-teal-ink); background: var(--pp-teal-soft);
  border-radius: 999px; padding: .4rem .8rem; white-space: nowrap;
}

/* Uyarı bandı */
.pp-banner {
  background: #FFF8E1; border: 1px solid #F3E2A9; border-left: 4px solid #E67700;
  color: #7A5200; border-radius: 10px; padding: .7rem 1rem; font-size: .88rem;
  margin-bottom: 1.2rem;
}

/* Bilgi notları (RxNorm geri bildirimi) */
.pp-note {
  display: inline-flex; align-items: center; gap: .45rem;
  background: var(--pp-teal-soft); color: var(--pp-teal-ink);
  border-radius: 999px; padding: .3rem .8rem; font-size: .82rem; font-weight: 500;
  margin: .2rem 0 .6rem;
}
.pp-note.warn { background: #FFF8E1; color: #9A6700; }

/* Skor kartı (monitör) */
.pp-hero {
  background: var(--pp-surface);
  border: 1px solid var(--pp-line);
  border-radius: 16px; box-shadow: var(--pp-shadow);
  padding: 1.3rem 1.5rem 1rem; margin: .4rem 0 1.1rem;
}
.pp-hero-row { display: flex; flex-wrap: wrap; align-items: center; gap: 1.4rem; }
.pp-score { font-family: 'IBM Plex Mono', monospace; font-size: 3.1rem; font-weight: 600; line-height: 1; }
.pp-score small { font-size: 1.1rem; color: var(--pp-muted); font-weight: 500; }
.pp-pill {
  display: inline-block; border-radius: 999px; padding: .3rem .85rem;
  font-size: .85rem; font-weight: 700;
}
.pp-chip {
  display: inline-block; border-radius: 999px; padding: .3rem .85rem;
  font-size: .85rem; font-weight: 600; background: var(--pp-bg);
  border: 1px solid var(--pp-line); color: var(--pp-muted);
}
.pp-bar { height: 10px; border-radius: 999px; background: #E9F1F4; overflow: hidden; margin-top: .9rem; }
.pp-bar-fill { height: 100%; border-radius: 999px; animation: pp-fill 1.1s cubic-bezier(.2,.7,.3,1) .25s both; }
@keyframes pp-fill { from { width: 0; } to { width: var(--target); } }
.pp-ecg { display: block; width: 100%; height: 44px; margin-top: .5rem; }
.pp-ecg path {
  fill: none; stroke: var(--pp-teal); stroke-width: 2; stroke-linecap: round;
  stroke-dasharray: 1600; stroke-dashoffset: 1600;
  animation: pp-draw 2.6s ease-out .2s forwards;
}
@keyframes pp-draw { to { stroke-dashoffset: 0; } }

/* Bulgu kartları */
.pp-finding {
  background: var(--pp-surface);
  border: 1px solid var(--pp-line); border-left: 5px solid var(--accent, var(--pp-teal));
  border-radius: 12px; box-shadow: var(--pp-shadow);
  padding: .95rem 1.15rem; margin-bottom: .8rem;
  transition: transform .18s ease, box-shadow .18s ease;
}
.pp-finding:hover { transform: translateX(3px); box-shadow: 0 2px 4px rgba(16,42,67,.06), 0 10px 24px rgba(16,42,67,.10); }
.pp-finding-head { display: flex; align-items: center; gap: .7rem; flex-wrap: wrap; margin-bottom: .4rem; }
.pp-finding-title { font-weight: 700; font-size: 1rem; }
.pp-finding p { margin: .25rem 0; font-size: .92rem; color: var(--pp-ink); }
.pp-finding .pp-meta { font-size: .78rem; color: var(--pp-muted); margin-top: .45rem; }

/* Boş durum / başarı kartı */
.pp-clear {
  background: #EBFBEE; border: 1px solid #C3EAC9; border-left: 5px solid #2B8A3E;
  color: #1F6B30; border-radius: 12px; padding: 1rem 1.2rem;
}

/* Giriş animasyonu */
.pp-fade { animation: pp-rise .5s ease-out both; }
@keyframes pp-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }

/* Streamlit bileşenleri */
.stButton > button[kind="primary"] {
  background: var(--pp-teal); border: none; border-radius: 10px;
  padding: .55rem 1.6rem; font-weight: 700; letter-spacing: .01em;
  box-shadow: 0 4px 12px rgba(11,114,133,.28);
  transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
}
.stButton > button[kind="primary"]:hover {
  background: var(--pp-teal-ink); transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(11,114,133,.34);
}
.stDownloadButton > button {
  border: 1.5px solid var(--pp-teal); color: var(--pp-teal-ink);
  border-radius: 10px; font-weight: 600; background: var(--pp-surface);
  transition: background .15s ease;
}
.stDownloadButton > button:hover { background: var(--pp-teal-soft); }
[data-testid="stTabs"] [role="tablist"] {
  display: inline-flex; gap: .3rem; background: var(--pp-surface);
  border: 1px solid var(--pp-line); border-radius: 12px; padding: .3rem;
  box-shadow: var(--pp-shadow);
}
[data-testid="stTab"] {
  border-radius: 9px !important; font-weight: 600; padding: .4rem .95rem;
  transition: background .15s ease, color .15s ease;
}
[data-testid="stTab"] p { color: var(--pp-muted); font-weight: 600; }
[data-testid="stTab"]:hover { background: var(--pp-bg); }
[data-testid="stTab"][aria-selected="true"] { background: var(--pp-teal-soft) !important; }
[data-testid="stTab"][aria-selected="true"] p { color: var(--pp-teal-ink) !important; }
.react-aria-SelectionIndicator { display: none !important; }
[data-testid="stExpander"] {
  background: var(--pp-surface); border: 1px solid var(--pp-line);
  border-radius: 12px; box-shadow: var(--pp-shadow);
}
[data-testid="stAlert"] { border-radius: 10px; }

@media (prefers-reduced-motion: reduce) {
  .pp-fade, .pp-bar-fill, .pp-ecg path { animation: none !important; }
  .pp-ecg path { stroke-dashoffset: 0; }
  .pp-card, .pp-finding, .stButton > button[kind="primary"] { transition: none; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def esc(value) -> str:
    return html.escape(str(value))


ECG_PATH = (
    "M0,26 L90,26 L104,26 L112,8 L122,42 L132,26 L240,26 L254,26 "
    "L262,10 L272,40 L282,26 L400,26 L414,26 L422,8 L432,42 L442,26 "
    "L560,26 L574,26 L582,12 L592,38 L602,26 L720,26"
)


inject_theme()

st.markdown(
    """
<div class="pp-header pp-fade">
  <div class="pp-logo">✚</div>
  <div>
    <div class="pp-title">PolyPharm AI</div>
    <div class="pp-sub">Akıllı İlaç Etkileşim ve Toksisite Simülatörü</div>
  </div>
  <div class="pp-dept">Reçete Güvenlik · Karar Destek</div>
</div>
<div class="pp-banner pp-fade" style="animation-delay:.08s">
  ⚕️ Bu uygulama eğitim amaçlı bir karar destek demosudur. Klinik teşhis, reçeteleme
  veya tedavi kararı için kullanılamaz.
</div>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_json_file(path: Path) -> list[dict]:
    if not path.exists():
        LOGGER.warning("Veri dosyası bulunamadı: %s", path)
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        LOGGER.exception("Veri dosyası okunamadı: %s", path)
        return []

    if not isinstance(payload, list):
        LOGGER.warning("Veri dosyasının kök değeri liste değil: %s", path)
        return []

    return payload


@st.cache_resource
def get_rxnorm_provider() -> RxNormProvider:
    return RxNormProvider()


@st.cache_resource
def get_orchestrator(use_openfda: bool, use_ai_summary: bool) -> Orchestrator:
    """Reuse the orchestrator across reruns so openFDA lookups stay cached."""
    return Orchestrator(use_openfda=use_openfda, use_ai_summary=use_ai_summary)


def build_patient_from_inputs(
    age: int,
    gender: str,
    current_medications: list[str],
    egfr: float,
    creatinine: float,
    ast: float,
    alt: float,
) -> Patient:
    return Patient(
        age=age,
        gender=gender,
        current_medications=current_medications,
        lab_values=LabValues(
            egfr=egfr,
            creatinine=creatinine,
            ast=ast,
            alt=alt,
        ),
    )


def severity_badge(severity: str) -> str:
    meta = SEVERITY_META.get(severity)
    if meta is None:
        return severity
    icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
    return f"{icons.get(severity, '')} {meta['label']}"


def severity_pill(severity: str) -> str:
    meta = SEVERITY_META.get(severity, SEVERITY_META["low"])
    return (
        f'<span class="pp-pill" style="background:{meta["tint"]};color:{meta["ink"]}">'
        f'{esc(meta["label"])}</span>'
    )


sample_patients = load_json_file(DATA_DIR / "sample_patients.json")
interaction_rules = load_json_file(DATA_DIR / "demo_interactions.json")
rxnorm = get_rxnorm_provider()

# --- Kenar çubuğu: hasta girişi ve veri kaynağı ayarları --------------------

st.sidebar.header("Hasta Seçimi")

patient_mode = st.sidebar.radio(
    "Hasta girişi",
    ["Demo hasta seç", "Manuel hasta gir"],
)

if patient_mode == "Demo hasta seç" and sample_patients:
    patient_names = [patient["name"] for patient in sample_patients]
    selected_name = st.sidebar.selectbox("Demo hasta", patient_names)

    selected_patient = next(
        patient for patient in sample_patients if patient["name"] == selected_name
    )

    age = int(selected_patient["age"])
    gender = selected_patient["gender"]
    current_medications = selected_patient["current_medications"]
    egfr = float(selected_patient["lab_values"]["egfr"])
    creatinine = float(selected_patient["lab_values"]["creatinine"])
    ast = float(selected_patient["lab_values"]["ast"])
    alt = float(selected_patient["lab_values"]["alt"])
else:
    age = st.sidebar.number_input("Yaş", min_value=0, max_value=120, value=65)
    gender = st.sidebar.selectbox("Cinsiyet", ["Kadın", "Erkek", "Diğer"])

    meds_text = st.sidebar.text_area(
        "Mevcut ilaçlar",
        value="warfarin, metformin",
        help="İlaçları virgülle ayırarak yazın. Marka adı da yazabilirsiniz (örn. Coumadin).",
    )

    current_medications = [
        medication.strip()
        for medication in meds_text.split(",")
        if medication.strip()
    ]

    egfr = st.sidebar.number_input("eGFR", min_value=0.0, max_value=150.0, value=75.0)
    creatinine = st.sidebar.number_input("Kreatinin", min_value=0.0, max_value=20.0, value=1.0)
    ast = st.sidebar.number_input("AST", min_value=0.0, max_value=1000.0, value=30.0)
    alt = st.sidebar.number_input("ALT", min_value=0.0, max_value=1000.0, value=30.0)

st.sidebar.divider()
st.sidebar.header("Veri Kaynakları")

use_openfda = st.sidebar.toggle(
    "openFDA etiket verisi",
    value=True,
    help="Yeni ilacın FDA prospektüs bilgilerini (uyarılar, etkileşim metni) çeker.",
)
use_ai_summary = st.sidebar.toggle(
    "Gemini yapay zeka özeti",
    value=GeminiExplainer().available,
    help="Bulguları Gemini ile Türkçe klinik özete dönüştürür. GEMINI_API_KEY gerektirir.",
)

if rxnorm.available:
    st.sidebar.success("RxNorm veritabanı aktif (lokal)")
else:
    st.sidebar.info(
        "RxNorm veritabanı bulunamadı. `scripts/build_rxnorm_db.py` ile "
        "üretebilirsiniz; uygulama onsuz da çalışır."
    )

# --- Yeni ilaç girişi -------------------------------------------------------

available_drugs = sorted(
    {
        item["drug_a"]
        for item in interaction_rules
        if "drug_a" in item
    }
    | {
        item["drug_b"]
        for item in interaction_rules
        if "drug_b" in item
    }
    | {"metformin", "atorvastatin", "ibuprofen", "furosemide", "lisinopril"}
)

st.header("Reçete Güvenlik Analizi")

input_mode = st.radio(
    "Yeni ilaç giriş yöntemi",
    ["Listeden seç", "Manuel yaz"],
    horizontal=True,
)

if input_mode == "Listeden seç":
    new_medication = st.selectbox(
        "Yeni yazılmak istenen ilaç",
        available_drugs,
        index=available_drugs.index("aspirin") if "aspirin" in available_drugs else 0,
    )
else:
    new_medication = st.text_input(
        "Yeni yazılmak istenen ilaç",
        value="aspirin",
        help="Etken madde veya marka adı yazabilirsiniz (örn. warfarin ya da Coumadin).",
    )

    if new_medication.strip() and rxnorm.available:
        lookup = rxnorm.lookup(new_medication)
        if lookup is not None:
            if lookup.is_brand:
                st.markdown(
                    f'<div class="pp-note">🔎 RxNorm: <strong>{esc(lookup.name)}</strong> bir marka adı — '
                    f'etken madde: <strong>{esc(", ".join(lookup.ingredients) or "bilinmiyor")}</strong> '
                    f'(RXCUI {esc(lookup.rxcui)})</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="pp-note">🔎 RxNorm: <strong>{esc(lookup.name)}</strong> '
                    f'(RXCUI {esc(lookup.rxcui)})</div>',
                    unsafe_allow_html=True,
                )
        else:
            suggestions = rxnorm.suggest(new_medication, limit=5)
            if suggestions:
                st.markdown(
                    '<div class="pp-note warn">RxNorm\'da tam eşleşme yok. Şunlardan birini mi '
                    "demek istediniz? "
                    + ", ".join(f"<strong>{esc(s)}</strong>" for s in suggestions)
                    + "</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="pp-note warn">RxNorm\'da eşleşme bulunamadı; '
                    "isim olduğu gibi kullanılacak.</div>",
                    unsafe_allow_html=True,
                )

# --- Hasta özeti kartları ---------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
<div class="pp-card pp-fade" style="animation-delay:.05s">
  <div class="pp-eyebrow">Hasta Bilgileri</div>
  <div class="pp-kv"><span class="k">Yaş</span><span class="v pp-mono">{esc(age)}</span></div>
  <div class="pp-kv"><span class="k">Cinsiyet</span><span class="v">{esc(gender)}</span></div>
  <div class="pp-kv"><span class="k">Mevcut ilaç sayısı</span><span class="v pp-mono">{len(current_medications)}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )

with col2:
    if current_medications:
        med_rows = []
        for medication in current_medications:
            ingredient_chip = ""
            if rxnorm.available:
                lookup = rxnorm.lookup(medication)
                if lookup is not None and lookup.is_brand and lookup.ingredients:
                    ingredient_chip = (
                        f'<span class="ing">→ {esc(", ".join(lookup.ingredients))}</span>'
                    )
            med_rows.append(
                f'<div class="pp-med">{esc(medication)} {ingredient_chip}</div>'
            )
        meds_html = "".join(med_rows)
    else:
        meds_html = '<div class="pp-med">Mevcut ilaç girilmedi.</div>'

    st.markdown(
        f"""
<div class="pp-card pp-fade" style="animation-delay:.12s">
  <div class="pp-eyebrow">Mevcut İlaçlar</div>
  {meds_html}
</div>
""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
<div class="pp-card pp-fade" style="animation-delay:.19s">
  <div class="pp-eyebrow">Laboratuvar Değerleri</div>
  <div class="pp-kv"><span class="k">eGFR</span><span class="v pp-mono">{esc(egfr)}</span></div>
  <div class="pp-kv"><span class="k">Kreatinin</span><span class="v pp-mono">{esc(creatinine)}</span></div>
  <div class="pp-kv"><span class="k">AST</span><span class="v pp-mono">{esc(ast)}</span></div>
  <div class="pp-kv"><span class="k">ALT</span><span class="v pp-mono">{esc(alt)}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )

st.write("")

# --- Analiz -----------------------------------------------------------------

if st.button("Analiz Et", type="primary"):
    try:
        patient = build_patient_from_inputs(
            age=age,
            gender=gender,
            current_medications=current_medications,
            egfr=egfr,
            creatinine=creatinine,
            ast=ast,
            alt=alt,
        )

        request = PrescriptionRequest(
            patient=patient,
            new_medication=new_medication,
        )

        orchestrator = get_orchestrator(use_openfda, use_ai_summary)

        with st.spinner("Analiz yapılıyor (RxNorm + openFDA + Gemini)..."):
            result = orchestrator.analyze(request)
    except Exception:
        LOGGER.exception("Reçete güvenlik analizi tamamlanamadı")
        st.error(
            "Analiz şu anda tamamlanamadı. Girdileri kontrol edip yeniden deneyin."
        )
        st.caption(
            "Sorun devam ederse harici veri kaynaklarını kapatıp çevrimdışı modu deneyin."
        )
        st.stop()

    risk_meta = RISK_LEVEL_META.get(result.risk_level, RISK_LEVEL_META["Orta Risk"])
    score_color = risk_meta["ink"]

    st.markdown(
        f"""
<div class="pp-hero pp-fade">
  <div class="pp-eyebrow">Analiz Sonucu</div>
  <div class="pp-hero-row">
    <div>
      <div class="pp-score" style="color:{score_color}">{result.safety_score}<small>/100</small></div>
      <div style="color:var(--pp-muted);font-size:.82rem;margin-top:.2rem">Güvenlik Skoru</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:.5rem">
      <span class="pp-pill" style="background:{risk_meta['tint']};color:{risk_meta['ink']}">{esc(result.risk_level)}</span>
      <span class="pp-chip">{len(result.findings)} bulgu</span>
    </div>
    <div style="flex:1;min-width:220px">
      <svg class="pp-ecg" viewBox="0 0 720 52" preserveAspectRatio="none" aria-hidden="true"><path d="{ECG_PATH}"/></svg>
      <div class="pp-bar"><div class="pp-bar-fill" style="--target:{result.safety_score}%;background:{score_color}"></div></div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    tab_summary, tab_findings, tab_drug, tab_raw = st.tabs(
        ["📋 Özet", "⚠️ Risk Bulguları", "💊 İlaç Bilgisi", "🧾 Ham Çıktı"]
    )

    with tab_summary:
        st.markdown(
            f"""
<div class="pp-card pp-fade">
  <div class="pp-eyebrow">Kural Tabanlı Özet</div>
  <p style="margin:.2rem 0;font-size:.95rem">{esc(result.recommendation_summary)}</p>
</div>
""",
            unsafe_allow_html=True,
        )

        if result.ai_summary:
            paragraphs = "".join(
                f'<p style="margin:.45rem 0;font-size:.95rem">{part}</p>'
                for part in (
                    re.sub(
                        r"\*\*(.+?)\*\*",
                        r"<strong>\1</strong>",
                        esc(paragraph.strip()),
                    )
                    for paragraph in result.ai_summary.split("\n\n")
                )
                if part
            )
            st.markdown(
                f"""
<div class="pp-card pp-fade" style="animation-delay:.1s;margin-top:.8rem">
  <div class="pp-eyebrow">🤖 Yapay Zeka Değerlendirmesi</div>
  {paragraphs}
  <div class="pp-meta" style="font-size:.78rem;color:var(--pp-muted);margin-top:.6rem">
    Model: {esc(result.ai_model)} · Bu özet bilgilendirme amaçlıdır.</div>
</div>
""",
                unsafe_allow_html=True,
            )
        elif use_ai_summary:
            st.caption(
                "Yapay zeka özeti üretilemedi (API anahtarı veya bağlantı sorunu). "
                "Kural tabanlı özet geçerlidir."
            )

    with tab_findings:
        if result.findings:
            for index, finding in enumerate(result.findings):
                meta = SEVERITY_META.get(finding.severity, SEVERITY_META["low"])
                st.markdown(
                    f"""
<div class="pp-finding pp-fade" style="--accent:{meta['dot']};animation-delay:{index * 0.07:.2f}s">
  <div class="pp-finding-head">{severity_pill(finding.severity)}
    <span class="pp-finding-title">{esc(finding.title)}</span></div>
  <p>{esc(finding.description)}</p>
  <p><strong>Öneri:</strong> {esc(finding.recommendation)}</p>
  <div class="pp-meta">Kaynak: {esc(finding.source)} · Ajan: {esc(finding.agent)}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            with st.expander("📊 Tablo görünümü"):
                findings_df = pd.DataFrame(
                    [
                        {
                            "Şiddet": severity_badge(finding.severity),
                            "Başlık": finding.title,
                            "Açıklama": finding.description,
                            "Öneri": finding.recommendation,
                            "Ajan": finding.agent,
                            "Kaynak": finding.source,
                        }
                        for finding in result.findings
                    ]
                )
                st.dataframe(findings_df, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                '<div class="pp-clear pp-fade">✅ Belirgin bir risk bulgusu tespit edilmedi.</div>',
                unsafe_allow_html=True,
            )

    with tab_drug:
        drug_info = result.new_drug_info
        if drug_info is None:
            st.write("İlaç bilgisi toplanamadı.")
        else:
            rows = [
                f'<div class="pp-kv"><span class="k">Sorgu</span><span class="v">{esc(drug_info.query_name)}</span></div>',
                f'<div class="pp-kv"><span class="k">Veri kaynağı</span><span class="v">{esc(drug_info.source)}</span></div>',
            ]
            if drug_info.normalized_name:
                rows.append(
                    f'<div class="pp-kv"><span class="k">RxNorm eşleşmesi</span>'
                    f'<span class="v">{esc(drug_info.normalized_name)} '
                    f'<span class="pp-mono" style="color:var(--pp-muted);font-size:.8rem">(RXCUI {esc(drug_info.rxcui)})</span></span></div>'
                )
                if drug_info.ingredients:
                    rows.append(
                        f'<div class="pp-kv"><span class="k">Etken madde(ler)</span>'
                        f'<span class="v">{esc(", ".join(drug_info.ingredients))}</span></div>'
                    )

            st.markdown(
                '<div class="pp-card pp-fade"><div class="pp-eyebrow">İlaç Künyesi</div>'
                + "".join(rows)
                + "</div>",
                unsafe_allow_html=True,
            )

            if drug_info.openfda_found:
                if drug_info.boxed_warning:
                    meta = SEVERITY_META["critical"]
                    st.markdown(
                        f"""
<div class="pp-finding pp-fade" style="--accent:{meta['dot']};margin-top:.8rem">
  <div class="pp-finding-head">{severity_pill('critical')}
    <span class="pp-finding-title">FDA Kutulu Uyarı</span></div>
  <p>{esc(drug_info.boxed_warning)}</p>
</div>
""",
                        unsafe_allow_html=True,
                    )
                if drug_info.warnings:
                    with st.expander("FDA Uyarılar (İngilizce)"):
                        st.write(drug_info.warnings)
                if drug_info.drug_interactions:
                    with st.expander("FDA Etkileşim Metni (İngilizce)"):
                        st.write(drug_info.drug_interactions)
                if drug_info.indications:
                    with st.expander("FDA Endikasyonlar (İngilizce)"):
                        st.write(drug_info.indications)
            else:
                st.caption("openFDA etiket verisi bulunamadı veya kapalı.")

    with tab_raw:
        st.json(result.model_dump())

    st.write("")
    st.download_button(
        label="Markdown raporu indir",
        data=result.markdown_report,
        file_name="polypharm_ai_rapor.md",
        mime="text/markdown",
    )
else:
    st.markdown(
        '<div class="pp-note pp-fade" style="animation-delay:.26s">🩺 Analizi başlatmak için '
        "hasta bilgilerini kontrol edip <strong>Analiz Et</strong> butonuna basın.</div>",
        unsafe_allow_html=True,
    )
