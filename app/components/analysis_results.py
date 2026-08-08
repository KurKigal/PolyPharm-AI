from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from app.components.common import esc
from app.i18n import Translator, risk_level_key, risk_level_label
from models.schemas import AnalysisResult

SEVERITY_META = {
    "critical": {"dot": "#C92A2A", "tint": "#FFF0F0", "ink": "#A61E1E"},
    "high": {"dot": "#E8590C", "tint": "#FFF4EC", "ink": "#C2410C"},
    "medium": {"dot": "#E67700", "tint": "#FFF8E1", "ink": "#9A6700"},
    "low": {"dot": "#1971C2", "tint": "#EDF5FF", "ink": "#1971C2"},
}

RISK_LEVEL_META = {
    "low": {"ink": "#2B8A3E", "tint": "#EBFBEE"},
    "medium": {"ink": "#9A6700", "tint": "#FFF8E1"},
    "high": {"ink": "#C2410C", "tint": "#FFF4EC"},
    "critical": {"ink": "#A61E1E", "tint": "#FFF0F0"},
}

ECG_PATH = (
    "M0,26 L90,26 L104,26 L112,8 L122,42 L132,26 L240,26 L254,26 "
    "L262,10 L272,40 L282,26 L400,26 L414,26 L422,8 L432,42 L442,26 "
    "L560,26 L574,26 L582,12 L592,38 L602,26 L720,26"
)


def render_analysis_results(
    result: AnalysisResult,
    *,
    t: Translator,
    use_ai_summary: bool,
) -> None:
    risk_key = risk_level_key(result.risk_level)
    risk_meta = RISK_LEVEL_META.get(
        risk_key,
        RISK_LEVEL_META["medium"],
    )
    score_color = risk_meta["ink"]

    st.markdown(
        f"""
<div class="pp-hero pp-fade">
  <div class="pp-eyebrow">{esc(t("analysis.result"))}</div>
  <div class="pp-hero-row">
    <div>
      <div class="pp-score" style="color:{score_color}">{result.safety_score}<small>/100</small></div>
      <div style="color:var(--pp-muted);font-size:.82rem;margin-top:.2rem">{esc(t("analysis.safety_score"))}</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:.5rem">
      <span class="pp-pill" style="background:{risk_meta['tint']};color:{risk_meta['ink']}">{esc(risk_level_label(result.risk_level, t))}</span>
      <span class="pp-chip">{esc(t("analysis.finding_count", count=len(result.findings)))}</span>
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
        [
            t("tabs.summary"),
            t("tabs.findings"),
            t("tabs.drug_info"),
            t("tabs.raw"),
        ]
    )

    with tab_summary:
        _render_summary(
            result,
            t,
            use_ai_summary,
        )

    with tab_findings:
        _render_findings(
            result,
            t,
        )

    with tab_drug:
        _render_drug_info(
            result,
            t,
        )

    with tab_raw:
        st.json(result.model_dump())

    st.write("")
    st.download_button(
        label=t("actions.download_report"),
        data=result.markdown_report,
        file_name=f"polypharm_ai_report_{t.language}.md",
        mime="text/markdown",
    )


def render_idle_note(t: Translator) -> None:
    st.markdown(
        (
            '<div class="pp-note pp-fade" style="animation-delay:.26s">'
            f'🩺 {esc(t("analysis.idle"))}</div>'
        ),
        unsafe_allow_html=True,
    )


def severity_badge(
    severity: str,
    t: Translator,
) -> str:
    icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵",
    }
    label = (
        t(f"severity.{severity}")
        if severity in SEVERITY_META
        else severity
    )
    return f"{icons.get(severity, '')} {label}".strip()


def severity_pill(
    severity: str,
    t: Translator,
) -> str:
    meta = SEVERITY_META.get(
        severity,
        SEVERITY_META["low"],
    )
    label = (
        t(f"severity.{severity}")
        if severity in SEVERITY_META
        else severity
    )

    return (
        f'<span class="pp-pill" style="background:{meta["tint"]};color:{meta["ink"]}">'
        f"{esc(label)}</span>"
    )


def _render_summary(
    result: AnalysisResult,
    t: Translator,
    use_ai_summary: bool,
) -> None:
    st.markdown(
        f"""
<div class="pp-card pp-fade">
  <div class="pp-eyebrow">{esc(t("analysis.rule_summary"))}</div>
  <p style="margin:.2rem 0;font-size:.95rem">{esc(result.recommendation_summary)}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    _render_score_breakdown(
        result,
        t,
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
  <div class="pp-eyebrow">🤖 {esc(t("analysis.ai_evaluation"))}</div>
  {paragraphs}
  <div class="pp-meta" style="font-size:.78rem;color:var(--pp-muted);margin-top:.6rem">
    {esc(t("analysis.ai_model_note", model=result.ai_model or t("common.unknown")))}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    elif use_ai_summary:
        st.caption(
            t("analysis.ai_unavailable")
        )


def _render_score_breakdown(
    result: AnalysisResult,
    t: Translator,
) -> None:
    breakdown = result.score_breakdown

    with st.expander(
        t("score_breakdown.title")
    ):
        col_start, col_penalty, col_raw, col_final = st.columns(4)

        col_start.metric(
            t("score_breakdown.starting_score"),
            breakdown.starting_score,
        )
        col_penalty.metric(
            t("score_breakdown.total_penalty"),
            f"-{breakdown.total_penalty}" if breakdown.total_penalty else "0",
        )
        col_raw.metric(
            t("score_breakdown.raw_score"),
            breakdown.raw_score,
        )
        col_final.metric(
            t("score_breakdown.final_score"),
            f"{breakdown.final_score}/100",
        )

        if breakdown.contributions:
            contribution_df = pd.DataFrame(
                [
                    {
                        t("score_breakdown.columns.finding"): contribution.title,
                        t("score_breakdown.columns.severity"): severity_badge(
                            contribution.severity,
                            t,
                        ),
                        t("score_breakdown.columns.penalty"): (
                            f"-{contribution.penalty}"
                            if contribution.penalty
                            else "0"
                        ),
                        t("score_breakdown.columns.source"): contribution.source,
                        t("score_breakdown.columns.agent"): contribution.agent,
                    }
                    for contribution in breakdown.contributions
                ]
            )

            st.dataframe(
                contribution_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption(
                t("score_breakdown.no_penalties")
            )

        st.caption(
            t("score_breakdown.disclaimer")
        )


def _render_findings(
    result: AnalysisResult,
    t: Translator,
) -> None:
    if not result.findings:
        st.markdown(
            f'<div class="pp-clear pp-fade">✅ {esc(t("findings.none"))}</div>',
            unsafe_allow_html=True,
        )
        return

    for index, finding in enumerate(result.findings):
        meta = SEVERITY_META.get(
            finding.severity,
            SEVERITY_META["low"],
        )

        st.markdown(
            f"""
<div class="pp-finding pp-fade" style="--accent:{meta['dot']};animation-delay:{index * 0.07:.2f}s">
  <div class="pp-finding-head">{severity_pill(finding.severity, t)}
    <span class="pp-finding-title">{esc(finding.title)}</span></div>
  <p>{esc(finding.description)}</p>
  <p><strong>{esc(t("findings.recommendation"))}:</strong> {esc(finding.recommendation)}</p>
  <div class="pp-meta">{esc(t("findings.source"))}: {esc(finding.source)} · {esc(t("findings.agent"))}: {esc(finding.agent)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with st.expander(
        t("findings.table_view")
    ):
        findings_df = pd.DataFrame(
            [
                {
                    t("findings.columns.severity"): severity_badge(
                        finding.severity,
                        t,
                    ),
                    t("findings.columns.title"): finding.title,
                    t("findings.columns.description"): finding.description,
                    t("findings.columns.recommendation"): finding.recommendation,
                    t("findings.columns.agent"): finding.agent,
                    t("findings.columns.source"): finding.source,
                }
                for finding in result.findings
            ]
        )

        st.dataframe(
            findings_df,
            use_container_width=True,
            hide_index=True,
        )


def _render_drug_info(
    result: AnalysisResult,
    t: Translator,
) -> None:
    drug_info = result.new_drug_info

    if drug_info is None:
        st.write(
            t("drug_info.unavailable")
        )
        return

    rows = [
        (
            f'<div class="pp-kv"><span class="k">{esc(t("drug_info.query"))}</span>'
            f'<span class="v">{esc(drug_info.query_name)}</span></div>'
        ),
        (
            f'<div class="pp-kv"><span class="k">{esc(t("drug_info.source"))}</span>'
            f'<span class="v">{esc(drug_info.source)}</span></div>'
        ),
    ]

    if drug_info.normalized_name:
        rows.append(
            f'<div class="pp-kv"><span class="k">{esc(t("drug_info.rxnorm_match"))}</span>'
            f'<span class="v">{esc(drug_info.normalized_name)} '
            f'<span class="pp-mono" style="color:var(--pp-muted);font-size:.8rem">'
            f"(RXCUI {esc(drug_info.rxcui)})</span></span></div>"
        )

        if drug_info.ingredients:
            rows.append(
                f'<div class="pp-kv"><span class="k">{esc(t("drug_info.ingredients"))}</span>'
                f'<span class="v">{esc(", ".join(drug_info.ingredients))}</span></div>'
            )

    st.markdown(
        (
            f'<div class="pp-card pp-fade"><div class="pp-eyebrow">'
            f'{esc(t("drug_info.card_title"))}</div>'
            + "".join(rows)
            + "</div>"
        ),
        unsafe_allow_html=True,
    )

    if drug_info.openfda_found:
        if drug_info.boxed_warning:
            meta = SEVERITY_META["critical"]
            st.markdown(
                f"""
<div class="pp-finding pp-fade" style="--accent:{meta['dot']};margin-top:.8rem">
  <div class="pp-finding-head">{severity_pill('critical', t)}
    <span class="pp-finding-title">{esc(t("drug_info.boxed_warning"))}</span></div>
  <p>{esc(drug_info.boxed_warning)}</p>
</div>
""",
                unsafe_allow_html=True,
            )

        if drug_info.warnings:
            with st.expander(
                t("drug_info.warnings")
            ):
                st.write(
                    drug_info.warnings
                )

        if drug_info.drug_interactions:
            with st.expander(
                t("drug_info.interactions")
            ):
                st.write(
                    drug_info.drug_interactions
                )

        if drug_info.indications:
            with st.expander(
                t("drug_info.indications")
            ):
                st.write(
                    drug_info.indications
                )
    else:
        st.caption(
            t("drug_info.openfda_missing")
        )
