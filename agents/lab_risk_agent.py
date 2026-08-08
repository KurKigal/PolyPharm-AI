from core.localization import normalize_language
from models.schemas import Patient, RiskFinding

RENAL_SENSITIVE_MEDICATIONS = {
    "metformin",
    "furosemide",
    "ibuprofen",
    "naproxen",
    "lisinopril",
    "enalapril",
    "digoxin",
}

HEPATIC_RISK_MEDICATIONS = {
    "atorvastatin",
    "simvastatin",
    "warfarin",
    "paracetamol",
    "acetaminophen",
    "methotrexate",
}

LAB_RULE_VERSION = "1.0.0"
LAB_EVIDENCE_REFERENCE = "PolyPharm AI prototype lab rules@1.0.0"

TEXT = {
    "tr": {
        "renal_severe_title": "Ciddi böbrek fonksiyon riski",
        "renal_severe_desc": "Hastanın eGFR değeri {egfr}. Bu değer ciddi böbrek fonksiyon azalmasına işaret edebilir.",
        "renal_severe_rec": "Yeni ilaç böbrekten atılıyorsa doz ayarı, alternatif tedavi veya uzman değerlendirmesi yapılmalıdır.",
        "renal_mod_title": "Orta düzey böbrek fonksiyon riski",
        "renal_mod_desc": "Hastanın eGFR değeri {egfr}. Böbrek fonksiyonunda azalma olabilir.",
        "renal_mod_rec": "Renal doz ayarı gerekip gerekmediği ve takip sıklığı kontrol edilmelidir.",
        "hepatic_marked_title": "Belirgin karaciğer fonksiyon riski",
        "hepatic_marked_desc": "AST: {ast}, ALT: {alt}. Karaciğer enzimleri belirgin yüksek görünüyor.",
        "hepatic_marked_rec": "Hepatotoksisite riski olan ilaçlarda alternatif tedavi veya yakın takip değerlendirilmelidir.",
        "hepatic_title": "Karaciğer fonksiyon riski",
        "hepatic_desc": "AST: {ast}, ALT: {alt}. Karaciğer enzimleri yüksek görünüyor.",
        "hepatic_rec": "Karaciğerden metabolize olan ilaçlar için risk/fayda değerlendirmesi yapılmalıdır.",
        "poly_elderly_title": "Yaşlı hastada polifarmasi riski",
        "poly_elderly_desc": "Hasta {age} yaşında ve {count} mevcut ilaç kullanıyor.",
        "poly_elderly_rec": "Tedavi listesi gereklilik, doz, tedavi süresi ve potansiyel advers olaylar açısından gözden geçirilmelidir.",
        "poly_title": "Çoklu ilaç kullanımı riski",
        "poly_desc": "Hastanın mevcut ilaç sayısı {count}.",
        "poly_rec": "İlaç listesinde mükerrerlik ve gereksiz tedaviler kontrol edilmelidir.",
    },
    "en": {
        "renal_severe_title": "Severe renal function risk",
        "renal_severe_desc": "The patient's eGFR is {egfr}. This may indicate severe reduction in renal function.",
        "renal_severe_rec": "If the new medication is renally cleared, assess dose adjustment, an alternative, or specialist review.",
        "renal_mod_title": "Moderate renal function risk",
        "renal_mod_desc": "The patient's eGFR is {egfr}. Renal function may be reduced.",
        "renal_mod_rec": "Review whether renal dose adjustment is required and determine an appropriate monitoring interval.",
        "hepatic_marked_title": "Marked hepatic function risk",
        "hepatic_marked_desc": "AST: {ast}, ALT: {alt}. Liver enzymes appear markedly elevated.",
        "hepatic_marked_rec": "For medications with hepatotoxic potential, assess alternatives or closer monitoring.",
        "hepatic_title": "Hepatic function risk",
        "hepatic_desc": "AST: {ast}, ALT: {alt}. Liver enzymes appear elevated.",
        "hepatic_rec": "Assess benefit-risk for medications primarily metabolized by the liver.",
        "poly_elderly_title": "Polypharmacy risk in an older adult",
        "poly_elderly_desc": "The patient is {age} years old and currently uses {count} medications.",
        "poly_elderly_rec": "Review the medication list for indication, dose, duration, and potential adverse events.",
        "poly_title": "Multiple-medication use risk",
        "poly_desc": "The patient currently uses {count} medications.",
        "poly_rec": "Review the medication list for duplication and potentially unnecessary therapy.",
    },
}


def _normalize(value: str) -> str:
    return value.lower().strip()


def _lab_finding(
    *,
    title: str,
    severity: str,
    description: str,
    recommendation: str,
    category: str,
    rule_id: str,
    dedupe_key: str,
) -> RiskFinding:
    return RiskFinding(
        title=title,
        severity=severity,
        description=description,
        recommendation=recommendation,
        category=category,
        evidence_type="prototype_rule",
        source="Rule-based clinical prototype logic",
        agent="LabRiskAgent",
        rule_id=rule_id,
        rule_version=LAB_RULE_VERSION,
        evidence_reference=LAB_EVIDENCE_REFERENCE,
        dedupe_key=dedupe_key,
    )


class LabRiskAgent:
    def analyze(
        self,
        patient: Patient,
        new_medication: str,
        language: str = "tr",
    ) -> list[RiskFinding]:
        lang = normalize_language(language)
        tx = TEXT[lang]
        new_med = _normalize(
            new_medication
        )

        findings: list[RiskFinding] = []
        findings.extend(
            self._renal_findings(
                patient.lab_values.egfr,
                new_med,
                tx,
            )
        )
        findings.extend(
            self._hepatic_findings(
                patient.lab_values.ast,
                patient.lab_values.alt,
                new_med,
                tx,
            )
        )
        findings.extend(
            self._polypharmacy_findings(
                patient,
                tx,
            )
        )
        return findings

    def _renal_findings(
        self,
        egfr: float,
        new_medication: str,
        tx: dict[str, str],
    ) -> list[RiskFinding]:
        renal_sensitive = new_medication in RENAL_SENSITIVE_MEDICATIONS

        if egfr < 30:
            return [
                _lab_finding(
                    title=tx["renal_severe_title"],
                    severity="high" if renal_sensitive else "medium",
                    description=tx["renal_severe_desc"].format(
                        egfr=egfr
                    ),
                    recommendation=tx["renal_severe_rec"],
                    category="renal",
                    rule_id="LAB-RENAL-SEVERE",
                    dedupe_key="lab:renal:severe",
                )
            ]

        if egfr < 60:
            return [
                _lab_finding(
                    title=tx["renal_mod_title"],
                    severity="medium" if renal_sensitive else "low",
                    description=tx["renal_mod_desc"].format(
                        egfr=egfr
                    ),
                    recommendation=tx["renal_mod_rec"],
                    category="renal",
                    rule_id="LAB-RENAL-MODERATE",
                    dedupe_key="lab:renal:moderate",
                )
            ]

        return []

    def _hepatic_findings(
        self,
        ast: float,
        alt: float,
        new_medication: str,
        tx: dict[str, str],
    ) -> list[RiskFinding]:
        hepatic_sensitive = new_medication in HEPATIC_RISK_MEDICATIONS

        if ast > 120 or alt > 120:
            return [
                _lab_finding(
                    title=tx["hepatic_marked_title"],
                    severity="high" if hepatic_sensitive else "medium",
                    description=tx["hepatic_marked_desc"].format(
                        ast=ast,
                        alt=alt,
                    ),
                    recommendation=tx["hepatic_marked_rec"],
                    category="hepatic",
                    rule_id="LAB-HEPATIC-MARKED",
                    dedupe_key="lab:hepatic:marked",
                )
            ]

        if ast > 80 or alt > 80:
            return [
                _lab_finding(
                    title=tx["hepatic_title"],
                    severity="medium",
                    description=tx["hepatic_desc"].format(
                        ast=ast,
                        alt=alt,
                    ),
                    recommendation=tx["hepatic_rec"],
                    category="hepatic",
                    rule_id="LAB-HEPATIC-ELEVATED",
                    dedupe_key="lab:hepatic:elevated",
                )
            ]

        return []

    def _polypharmacy_findings(
        self,
        patient: Patient,
        tx: dict[str, str],
    ) -> list[RiskFinding]:
        count = len(
            patient.current_medications
        )

        if patient.age >= 65 and count >= 5:
            return [
                _lab_finding(
                    title=tx["poly_elderly_title"],
                    severity="medium",
                    description=tx["poly_elderly_desc"].format(
                        age=patient.age,
                        count=count,
                    ),
                    recommendation=tx["poly_elderly_rec"],
                    category="polypharmacy",
                    rule_id="LAB-POLYPHARMACY-OLDER-ADULT",
                    dedupe_key="lab:polypharmacy:older-adult",
                )
            ]

        if count >= 8:
            return [
                _lab_finding(
                    title=tx["poly_title"],
                    severity="medium",
                    description=tx["poly_desc"].format(
                        count=count
                    ),
                    recommendation=tx["poly_rec"],
                    category="polypharmacy",
                    rule_id="LAB-POLYPHARMACY-COUNT",
                    dedupe_key="lab:polypharmacy:count",
                )
            ]

        return []
