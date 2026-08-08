from datetime import datetime

from core.localization import gender_label, normalize_language, risk_level_label
from models.schemas import DrugInfo, Patient, RiskFinding, ScoreBreakdown

SUMMARY_TEXT = {
    "en": {
        "none": (
            "No explicit risk was detected. This output does not replace clinical "
            "judgement and still requires clinician review."
        ),
        "high": (
            "High-priority risk findings were detected. The prescription should be "
            "reassessed by a clinician, including dose adjustment, medication "
            "substitution, or additional monitoring where appropriate."
        ),
        "medium": (
            "Moderate-risk findings were detected. Review the medications, "
            "laboratory values, and patient profile carefully in clinical context."
        ),
        "low": (
            "Overall risk level: {risk_level}. The findings appear low priority and "
            "should still be interpreted in clinical context."
        ),
    },
    "tr": {
        "none": (
            "Belirgin bir risk bulunmadı. Yine de bu çıktı klinik karar yerine geçmez; "
            "hekim değerlendirmesi gereklidir."
        ),
        "high": (
            "Yüksek öncelikli risk bulguları tespit edildi. Reçete klinik uzman "
            "tarafından yeniden değerlendirilmeli; doz ayarı, ilaç değişimi veya ek "
            "izlem seçenekleri gözden geçirilmelidir."
        ),
        "medium": (
            "Orta düzey riskli bulgular tespit edildi. İlgili ilaçlar, laboratuvar "
            "değerleri ve hasta profili dikkate alınarak dikkatli değerlendirme "
            "yapılmalıdır."
        ),
        "low": (
            "Genel risk seviyesi: {risk_level}. Bulgular düşük öncelikli görünmektedir; "
            "klinik bağlam içinde değerlendirilmelidir."
        ),
    },
}


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def _penalty_text(value: int) -> str:
    return f"-{value}" if value else "0"


class ReportAgent:
    def generate_summary(
        self,
        findings: list[RiskFinding],
        risk_level: str,
        language: str = "tr",
    ) -> str:
        lang = normalize_language(language)
        tx = SUMMARY_TEXT[lang]

        if not findings:
            return tx["none"]

        if any(finding.severity in {"critical", "high"} for finding in findings):
            return tx["high"]

        if any(finding.severity == "medium" for finding in findings):
            return tx["medium"]

        return tx["low"].format(
            risk_level=risk_level_label(risk_level, lang)
        )

    def generate_markdown_report(
        self,
        patient: Patient,
        new_medication: str,
        safety_score: int,
        risk_level: str,
        findings: list[RiskFinding],
        summary: str,
        drug_info: DrugInfo | None = None,
        ai_summary: str | None = None,
        score_breakdown: ScoreBreakdown | None = None,
        language: str = "tr",
    ) -> str:
        lang = normalize_language(language)

        if lang == "en":
            return self._english_report(
                patient,
                new_medication,
                safety_score,
                risk_level,
                findings,
                summary,
                drug_info,
                ai_summary,
                score_breakdown,
            )

        return self._turkish_report(
            patient,
            new_medication,
            safety_score,
            risk_level,
            findings,
            summary,
            drug_info,
            ai_summary,
            score_breakdown,
        )

    def _english_report(
        self,
        patient: Patient,
        new_medication: str,
        safety_score: int,
        risk_level: str,
        findings: list[RiskFinding],
        summary: str,
        drug_info: DrugInfo | None,
        ai_summary: str | None,
        score_breakdown: ScoreBreakdown | None,
    ) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# PolyPharm AI Prescription Safety Report",
            "",
            f"**Created:** {created_at}",
            "",
            (
                "> This report is an educational decision-support prototype. "
                "It must not be used for diagnosis, prescribing, or treatment decisions."
            ),
            "",
            "## Patient Summary",
            "",
            f"- Age: {patient.age}",
            f"- Gender: {gender_label(patient.gender, 'en')}",
            (
                "- Current medications: "
                f"{', '.join(patient.current_medications) if patient.current_medications else 'None'}"
            ),
            f"- New medication: {new_medication}",
            "",
            "## Laboratory Values",
            "",
            f"- eGFR: {patient.lab_values.egfr}",
            f"- Creatinine: {patient.lab_values.creatinine}",
            f"- AST: {patient.lab_values.ast}",
            f"- ALT: {patient.lab_values.alt}",
            "",
            "## Analysis Result",
            "",
            f"- Safety score: **{safety_score}/100**",
            f"- Risk level: **{risk_level_label(risk_level, 'en')}**",
            f"- Summary: {summary}",
            "",
        ]

        if score_breakdown is not None:
            lines.extend(
                self._score_breakdown_section(
                    score_breakdown,
                    language="en",
                )
            )

        if drug_info is not None and drug_info.normalized_name:
            lines += [
                "## Drug Information (External Sources)",
                "",
                (
                    f"- RxNorm match: {drug_info.normalized_name} "
                    f"(RXCUI: {drug_info.rxcui})"
                ),
                (
                    "- Active ingredient(s): "
                    f"{', '.join(drug_info.ingredients) if drug_info.ingredients else 'Unknown'}"
                ),
                f"- Data source: {drug_info.source}",
                "",
            ]

        if ai_summary:
            lines += [
                "## AI-Assisted Evaluation",
                "",
                ai_summary,
                "",
            ]

        lines += [
            "## Risk Findings",
            "",
        ]

        if not findings:
            lines.append("No explicit risk finding was detected.")
        else:
            for index, finding in enumerate(findings, start=1):
                lines += [
                    f"### {index}. {finding.title}",
                    "",
                    f"- Severity: `{finding.severity}`",
                    f"- Description: {finding.description}",
                    f"- Recommendation: {finding.recommendation}",
                    f"- Source: {finding.source}",
                    f"- Agent: {finding.agent}",
                    f"- Category: {finding.category}",
                    f"- Evidence type: {finding.evidence_type}",
                    f"- Rule: {finding.rule_id or '-'} ({finding.rule_version or '-'})",
                    f"- Evidence reference: {finding.evidence_reference or '-'}",
                    "",
                ]

        return "\n".join(lines)

    def _turkish_report(
        self,
        patient: Patient,
        new_medication: str,
        safety_score: int,
        risk_level: str,
        findings: list[RiskFinding],
        summary: str,
        drug_info: DrugInfo | None,
        ai_summary: str | None,
        score_breakdown: ScoreBreakdown | None,
    ) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# PolyPharm AI Reçete Güvenlik Raporu",
            "",
            f"**Oluşturulma zamanı:** {created_at}",
            "",
            (
                "> Bu rapor eğitim amaçlı bir karar destek demosudur. "
                "Klinik teşhis, reçeteleme veya tedavi kararı yerine geçmez."
            ),
            "",
            "## Hasta Özeti",
            "",
            f"- Yaş: {patient.age}",
            f"- Cinsiyet: {gender_label(patient.gender, 'tr')}",
            (
                "- Mevcut ilaçlar: "
                f"{', '.join(patient.current_medications) if patient.current_medications else 'Yok'}"
            ),
            f"- Yeni ilaç: {new_medication}",
            "",
            "## Laboratuvar Değerleri",
            "",
            f"- eGFR: {patient.lab_values.egfr}",
            f"- Kreatinin: {patient.lab_values.creatinine}",
            f"- AST: {patient.lab_values.ast}",
            f"- ALT: {patient.lab_values.alt}",
            "",
            "## Analiz Sonucu",
            "",
            f"- Güvenlik skoru: **{safety_score}/100**",
            f"- Risk seviyesi: **{risk_level_label(risk_level, 'tr')}**",
            f"- Özet: {summary}",
            "",
        ]

        if score_breakdown is not None:
            lines.extend(
                self._score_breakdown_section(
                    score_breakdown,
                    language="tr",
                )
            )

        if drug_info is not None and drug_info.normalized_name:
            lines += [
                "## İlaç Bilgisi (Harici Kaynaklar)",
                "",
                (
                    f"- RxNorm eşleşmesi: {drug_info.normalized_name} "
                    f"(RXCUI: {drug_info.rxcui})"
                ),
                (
                    "- Etken madde(ler): "
                    f"{', '.join(drug_info.ingredients) if drug_info.ingredients else 'Bilinmiyor'}"
                ),
                f"- Veri kaynağı: {drug_info.source}",
                "",
            ]

        if ai_summary:
            lines += [
                "## Yapay Zeka Değerlendirmesi",
                "",
                ai_summary,
                "",
            ]

        lines += [
            "## Risk Bulguları",
            "",
        ]

        if not findings:
            lines.append("Belirgin bir risk bulgusu tespit edilmedi.")
        else:
            for index, finding in enumerate(findings, start=1):
                lines += [
                    f"### {index}. {finding.title}",
                    "",
                    f"- Şiddet: `{finding.severity}`",
                    f"- Açıklama: {finding.description}",
                    f"- Öneri: {finding.recommendation}",
                    f"- Kaynak: {finding.source}",
                    f"- Ajan: {finding.agent}",
                    f"- Kategori: {finding.category}",
                    f"- Kanıt türü: {finding.evidence_type}",
                    f"- Kural: {finding.rule_id or '-'} ({finding.rule_version or '-'})",
                    f"- Kanıt referansı: {finding.evidence_reference or '-'}",
                    "",
                ]

        return "\n".join(lines)

    def _score_breakdown_section(
        self,
        breakdown: ScoreBreakdown,
        *,
        language: str,
    ) -> list[str]:
        if language == "en":
            lines = [
                "## Score Breakdown",
                "",
                f"- Scoring policy: **{breakdown.policy_version}**",
                f"- Starting score: **{breakdown.starting_score}**",
                f"- Duplicate findings suppressed: **{breakdown.duplicates_suppressed}**",
                f"- Total penalty: **{_penalty_text(breakdown.total_penalty)}**",
                f"- Raw score: **{breakdown.raw_score}**",
                f"- Final score: **{breakdown.final_score}/100**",
                "",
            ]
            headers = (
                "Finding",
                "Severity",
                "Penalty",
                "Category",
                "Evidence",
                "Source",
                "Agent",
                "Rule",
            )
            note = (
                "> Score attribution is deterministic and explains the software rule output; "
                "it is not a clinically validated risk scale."
            )
        else:
            lines = [
                "## Skor Dökümü",
                "",
                f"- Skorlama politikası: **{breakdown.policy_version}**",
                f"- Başlangıç skoru: **{breakdown.starting_score}**",
                f"- Bastırılan mükerrer bulgu: **{breakdown.duplicates_suppressed}**",
                f"- Toplam kesinti: **{_penalty_text(breakdown.total_penalty)}**",
                f"- Ham skor: **{breakdown.raw_score}**",
                f"- Nihai skor: **{breakdown.final_score}/100**",
                "",
            ]
            headers = (
                "Bulgu",
                "Şiddet",
                "Kesinti",
                "Kategori",
                "Kanıt Türü",
                "Kaynak",
                "Ajan",
                "Kural",
            )
            note = (
                "> Skor dökümü deterministiktir ve yazılım kurallarının sonucunu açıklar; "
                "klinik olarak doğrulanmış bir risk ölçeği değildir."
            )

        if breakdown.contributions:
            lines.extend(
                [
                    (
                        f"| {headers[0]} | {headers[1]} | {headers[2]} | "
                        f"{headers[3]} | {headers[4]} | {headers[5]} | "
                        f"{headers[6]} | {headers[7]} |"
                    ),
                    "|---|---|---:|---|---|---|---|---|",
                ]
            )

            for item in breakdown.contributions:
                rule_label = (
                    f"{item.rule_id}@{item.rule_version}"
                    if item.rule_id and item.rule_version
                    else item.rule_id or "-"
                )
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            _markdown_cell(item.title),
                            _markdown_cell(item.severity),
                            _penalty_text(item.penalty),
                            _markdown_cell(item.category),
                            _markdown_cell(item.evidence_type),
                            _markdown_cell(item.source),
                            _markdown_cell(item.agent),
                            _markdown_cell(rule_label),
                        ]
                    )
                    + " |"
                )
        else:
            lines.append(
                "No score deductions were applied."
                if language == "en"
                else "Skor kesintisi uygulanmadı."
            )

        lines += [
            "",
            note,
            "",
        ]

        return lines
