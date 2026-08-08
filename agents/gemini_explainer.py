"""Optional Gemini explanation layer for structured PolyPharm AI findings."""

import os

from core.localization import gender_label, normalize_language, risk_level_label
from models.schemas import DrugInfo, Patient, RiskFinding

DEFAULT_MODEL = "gemini-3.1-flash-lite"

SYSTEM_INSTRUCTIONS = {
    "tr": (
        "Sen bir klinik eczacılık asistanısın. Bir karar destek prototipi için reçete güvenlik analizini özetliyorsun. Kurallar:\n"
        "- Türkçe yaz, en fazla 200 kelime.\n- Teşhis koyma, tedavi önerme; yalnızca riskleri açıkla ve hekimin değerlendirmesi gereken noktaları vurgula.\n"
        "- Verilen bulguların dışına çıkma, yeni risk uydurma.\n- Net başlıksız akıcı 2-3 paragraf yaz.\n"
        "- Sonuna tek cümlelik 'bu çıktı hekim kararının yerine geçmez' uyarısı ekle."
    ),
    "en": (
        "You are a clinical-pharmacy assistant summarizing a prescription-safety analysis for a decision-support prototype. Rules:\n"
        "- Write in English, maximum 200 words.\n- Do not diagnose or prescribe treatment; explain only the supplied risks and what requires clinician review.\n"
        "- Do not invent risks beyond the provided findings.\n- Write 2-3 concise paragraphs without headings.\n"
        "- End with one sentence stating that this output does not replace clinician judgement."
    ),
}


class GeminiExplainer:
    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL, client=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model
        self._client = client

    @property
    def available(self) -> bool:
        return bool(self.api_key) or self._client is not None

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_summary(self, patient: Patient, new_medication: str, findings: list[RiskFinding], safety_score: int, risk_level: str, drug_info: DrugInfo | None = None, language: str = "tr") -> str | None:
        if not self.available:
            return None
        lang = normalize_language(language)
        prompt = self._build_prompt(patient, new_medication, findings, safety_score, risk_level, drug_info, lang)
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=prompt,
                config={"system_instruction": SYSTEM_INSTRUCTIONS[lang], "temperature": 0.3},
            )
            text = (response.text or "").strip()
        except Exception:
            return None
        return text or None

    def _build_prompt(self, patient: Patient, new_medication: str, findings: list[RiskFinding], safety_score: int, risk_level: str, drug_info: DrugInfo | None, language: str) -> str:
        if language == "en":
            lines = [
                "Prescription safety analysis data:",
                f"- Patient: {patient.age} years old, {gender_label(patient.gender, 'en')}",
                f"- Current medications: {', '.join(patient.current_medications) or 'none'}",
                f"- Laboratory: eGFR {patient.lab_values.egfr}, creatinine {patient.lab_values.creatinine}, AST {patient.lab_values.ast}, ALT {patient.lab_values.alt}",
                f"- Proposed new medication: {new_medication}",
                f"- Safety score: {safety_score}/100, risk level: {risk_level_label(risk_level, 'en')}",
            ]
            if drug_info is not None:
                if drug_info.normalized_name:
                    lines.append(f"- RxNorm match: {drug_info.normalized_name} (active ingredient: {', '.join(drug_info.ingredients) or 'unknown'})")
                if drug_info.boxed_warning:
                    lines.append(f"- openFDA boxed warning: {drug_info.boxed_warning}")
                if drug_info.drug_interactions:
                    lines.append(f"- openFDA interaction text: {drug_info.drug_interactions}")
            if findings:
                lines.append("- Structured findings:")
                lines.extend(f"  * [{f.severity}] {f.title}: {f.description}" for f in findings)
            else:
                lines.append("- No structured findings.")
            lines.append("\nBased only on these data, write a short clinical review summary for a clinician.")
            return "\n".join(lines)

        lines = [
            "Reçete güvenlik analizi verileri:",
            f"- Hasta: {patient.age} yaşında, {gender_label(patient.gender, 'tr')}",
            f"- Mevcut ilaçlar: {', '.join(patient.current_medications) or 'yok'}",
            f"- Laboratuvar: eGFR {patient.lab_values.egfr}, kreatinin {patient.lab_values.creatinine}, AST {patient.lab_values.ast}, ALT {patient.lab_values.alt}",
            f"- Yeni yazılmak istenen ilaç: {new_medication}",
            f"- Güvenlik skoru: {safety_score}/100, risk seviyesi: {risk_level_label(risk_level, 'tr')}",
        ]
        if drug_info is not None:
            if drug_info.normalized_name:
                lines.append(f"- RxNorm eşleşmesi: {drug_info.normalized_name} (etken madde: {', '.join(drug_info.ingredients) or 'bilinmiyor'})")
            if drug_info.boxed_warning:
                lines.append(f"- openFDA kutulu uyarı (İngilizce): {drug_info.boxed_warning}")
            if drug_info.drug_interactions:
                lines.append(f"- openFDA etkileşim metni (İngilizce): {drug_info.drug_interactions}")
        if findings:
            lines.append("- Kural tabanlı bulgular:")
            lines.extend(f"  * [{f.severity}] {f.title}: {f.description}" for f in findings)
        else:
            lines.append("- Kural tabanlı bulgu yok.")
        lines.append("\nBu verilere dayanarak hekim için kısa bir klinik değerlendirme özeti yaz.")
        return "\n".join(lines)
