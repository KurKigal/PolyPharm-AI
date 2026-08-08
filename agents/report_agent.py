from datetime import datetime

from core.localization import gender_label, normalize_language, risk_level_label
from models.schemas import DrugInfo, Patient, RiskFinding

SUMMARY_TEXT = {
    "en": {
        "none": "No explicit risk was detected. This output does not replace clinical judgement and still requires clinician review.",
        "high": "High-priority risk findings were detected. The prescription should be reassessed by a clinician, including dose adjustment, medication substitution, or additional monitoring where appropriate.",
        "medium": "Moderate-risk findings were detected. Review the medications, laboratory values, and patient profile carefully in clinical context.",
        "low": "Overall risk level: {risk_level}. The findings appear low priority and should still be interpreted in clinical context.",
    },
    "tr": {
        "none": "Belirgin bir risk bulunmadı. Yine de bu çıktı klinik karar yerine geçmez; hekim değerlendirmesi gereklidir.",
        "high": "Yüksek öncelikli risk bulguları tespit edildi. Reçete klinik uzman tarafından yeniden değerlendirilmeli; doz ayarı, ilaç değişimi veya ek izlem seçenekleri gözden geçirilmelidir.",
        "medium": "Orta düzey riskli bulgular tespit edildi. İlgili ilaçlar, laboratuvar değerleri ve hasta profili dikkate alınarak dikkatli değerlendirme yapılmalıdır.",
        "low": "Genel risk seviyesi: {risk_level}. Bulgular düşük öncelikli görünmektedir; klinik bağlam içinde değerlendirilmelidir.",
    },
}


class ReportAgent:
    def generate_summary(self, findings: list[RiskFinding], risk_level: str, language: str = "tr") -> str:
        lang = normalize_language(language)
        tx = SUMMARY_TEXT[lang]
        if not findings:
            return tx["none"]
        if any(f.severity in {"critical", "high"} for f in findings):
            return tx["high"]
        if any(f.severity == "medium" for f in findings):
            return tx["medium"]
        return tx["low"].format(risk_level=risk_level_label(risk_level, lang))

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
        language: str = "tr",
    ) -> str:
        lang = normalize_language(language)
        return self._english_report(patient, new_medication, safety_score, risk_level, findings, summary, drug_info, ai_summary) if lang == "en" else self._turkish_report(patient, new_medication, safety_score, risk_level, findings, summary, drug_info, ai_summary)

    def _english_report(self, patient, new_medication, safety_score, risk_level, findings, summary, drug_info, ai_summary) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "# PolyPharm AI Prescription Safety Report", "", f"**Created:** {created_at}", "",
            "> This report is an educational decision-support prototype. It must not be used for diagnosis, prescribing, or treatment decisions.", "",
            "## Patient Summary", "", f"- Age: {patient.age}", f"- Gender: {gender_label(patient.gender, 'en')}",
            f"- Current medications: {', '.join(patient.current_medications) if patient.current_medications else 'None'}", f"- New medication: {new_medication}", "",
            "## Laboratory Values", "", f"- eGFR: {patient.lab_values.egfr}", f"- Creatinine: {patient.lab_values.creatinine}", f"- AST: {patient.lab_values.ast}", f"- ALT: {patient.lab_values.alt}", "",
            "## Analysis Result", "", f"- Safety score: **{safety_score}/100**", f"- Risk level: **{risk_level_label(risk_level, 'en')}**", f"- Summary: {summary}", "",
        ]
        if drug_info is not None and drug_info.normalized_name:
            lines += ["## Drug Information (External Sources)", "", f"- RxNorm match: {drug_info.normalized_name} (RXCUI: {drug_info.rxcui})", f"- Active ingredient(s): {', '.join(drug_info.ingredients) if drug_info.ingredients else 'Unknown'}", f"- Data source: {drug_info.source}", ""]
        if ai_summary:
            lines += ["## AI-Assisted Evaluation", "", ai_summary, ""]
        lines += ["## Risk Findings", ""]
        if not findings:
            lines.append("No explicit risk finding was detected.")
        else:
            for index, finding in enumerate(findings, start=1):
                lines += [f"### {index}. {finding.title}", "", f"- Severity: `{finding.severity}`", f"- Description: {finding.description}", f"- Recommendation: {finding.recommendation}", f"- Source: {finding.source}", f"- Agent: {finding.agent}", ""]
        return "\n".join(lines)

    def _turkish_report(self, patient, new_medication, safety_score, risk_level, findings, summary, drug_info, ai_summary) -> str:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "# PolyPharm AI Reçete Güvenlik Raporu", "", f"**Oluşturulma zamanı:** {created_at}", "",
            "> Bu rapor eğitim amaçlı bir karar destek demosudur. Klinik teşhis, reçeteleme veya tedavi kararı yerine geçmez.", "",
            "## Hasta Özeti", "", f"- Yaş: {patient.age}", f"- Cinsiyet: {gender_label(patient.gender, 'tr')}",
            f"- Mevcut ilaçlar: {', '.join(patient.current_medications) if patient.current_medications else 'Yok'}", f"- Yeni ilaç: {new_medication}", "",
            "## Laboratuvar Değerleri", "", f"- eGFR: {patient.lab_values.egfr}", f"- Kreatinin: {patient.lab_values.creatinine}", f"- AST: {patient.lab_values.ast}", f"- ALT: {patient.lab_values.alt}", "",
            "## Analiz Sonucu", "", f"- Güvenlik skoru: **{safety_score}/100**", f"- Risk seviyesi: **{risk_level_label(risk_level, 'tr')}**", f"- Özet: {summary}", "",
        ]
        if drug_info is not None and drug_info.normalized_name:
            lines += ["## İlaç Bilgisi (Harici Kaynaklar)", "", f"- RxNorm eşleşmesi: {drug_info.normalized_name} (RXCUI: {drug_info.rxcui})", f"- Etken madde(ler): {', '.join(drug_info.ingredients) if drug_info.ingredients else 'Bilinmiyor'}", f"- Veri kaynağı: {drug_info.source}", ""]
        if ai_summary:
            lines += ["## Yapay Zeka Değerlendirmesi", "", ai_summary, ""]
        lines += ["## Risk Bulguları", ""]
        if not findings:
            lines.append("Belirgin bir risk bulgusu tespit edilmedi.")
        else:
            for index, finding in enumerate(findings, start=1):
                lines += [f"### {index}. {finding.title}", "", f"- Şiddet: `{finding.severity}`", f"- Açıklama: {finding.description}", f"- Öneri: {finding.recommendation}", f"- Kaynak: {finding.source}", f"- Ajan: {finding.agent}", ""]
        return "\n".join(lines)
