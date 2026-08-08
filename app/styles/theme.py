import streamlit as st

THEME_CSS = r"""
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
"""


def inject_theme() -> None:
    st.markdown(THEME_CSS, unsafe_allow_html=True)
