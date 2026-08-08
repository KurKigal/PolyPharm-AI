from typing import Literal

from pydantic import BaseModel, Field, field_validator

Severity = Literal["low", "medium", "high", "critical"]
RiskLevel = Literal["low", "medium", "high", "critical"]
Gender = Literal["female", "male", "other"]

FindingCategory = Literal[
    "drug_interaction",
    "renal",
    "hepatic",
    "polypharmacy",
    "boxed_warning",
    "other",
]

EvidenceType = Literal[
    "curated_rule",
    "prototype_rule",
    "official_label",
    "external_data",
    "unknown",
]

_GENDER_ALIASES = {
    "female": "female",
    "woman": "female",
    "kadın": "female",
    "kadin": "female",
    "male": "male",
    "man": "male",
    "erkek": "male",
    "other": "other",
    "diğer": "other",
    "diger": "other",
}


class LabValues(BaseModel):
    """Patient laboratory values used by the rule-based analysis agents."""

    egfr: float = Field(
        ...,
        ge=0,
        le=150,
        description="Estimated Glomerular Filtration Rate",
    )
    creatinine: float = Field(
        ...,
        ge=0,
        le=20,
        description="Serum creatinine",
    )
    ast: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Aspartate aminotransferase",
    )
    alt: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Alanine aminotransferase",
    )


class Patient(BaseModel):
    age: int = Field(..., ge=0, le=120)
    gender: Gender
    current_medications: list[str] = Field(default_factory=list)
    lab_values: LabValues

    @field_validator("gender", mode="before")
    @classmethod
    def normalize_gender(cls, value: str) -> str:
        normalized = str(value).strip().lower()
        return _GENDER_ALIASES.get(normalized, normalized)

    @field_validator("current_medications")
    @classmethod
    def clean_medication_names(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for value in values:
            normalized = value.strip()
            key = normalized.lower()

            if normalized and key not in seen:
                cleaned.append(normalized)
                seen.add(key)

        return cleaned


class PrescriptionRequest(BaseModel):
    patient: Patient
    new_medication: str = Field(..., min_length=1)

    @field_validator("new_medication")
    @classmethod
    def clean_new_medication(cls, value: str) -> str:
        return value.strip()


class DrugInfo(BaseModel):
    """External data gathered for a single drug (RxNorm + openFDA)."""

    query_name: str
    normalized_name: str | None = None
    rxcui: str | None = None
    is_brand: bool = False
    ingredients: list[str] = Field(default_factory=list)
    openfda_found: bool = False
    boxed_warning: str | None = None
    warnings: str | None = None
    drug_interactions: str | None = None
    indications: str | None = None
    source: str = "unknown"


class RiskFinding(BaseModel):
    title: str
    severity: Severity
    description: str
    recommendation: str

    category: FindingCategory = "other"
    evidence_type: EvidenceType = "unknown"

    source: str = "PolyPharm AI rule"
    agent: str = "unknown"

    rule_id: str | None = None
    rule_version: str | None = None
    evidence_reference: str | None = None

    # Findings with the same explicit dedupe_key describe the same logical signal.
    # Different data sources should intentionally use different keys unless they
    # are known to be true duplicates.
    dedupe_key: str | None = None


class ScoreContribution(BaseModel):
    """A deterministic score deduction linked to one risk finding."""

    finding_index: int = Field(..., ge=0)
    severity: Severity
    category: FindingCategory

    # base_penalty is the configured severity penalty. penalty is the amount
    # actually applied after an optional category cap.
    base_penalty: int = Field(..., ge=0)
    penalty: int = Field(..., ge=0)
    capped: bool = False

    title: str
    source: str
    agent: str
    evidence_type: EvidenceType = "unknown"
    rule_id: str | None = None
    rule_version: str | None = None
    evidence_reference: str | None = None


class ScoreBreakdown(BaseModel):
    """Explainable attribution for the deterministic prescription safety score."""

    policy_version: str
    starting_score: int = Field(default=100, ge=0, le=100)
    total_penalty: int = Field(..., ge=0)
    raw_score: int
    final_score: int = Field(..., ge=0, le=100)

    duplicates_suppressed: int = Field(default=0, ge=0)
    category_penalties: dict[str, int] = Field(default_factory=dict)
    contributions: list[ScoreContribution] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    safety_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    score_breakdown: ScoreBreakdown
    findings: list[RiskFinding]
    recommendation_summary: str
    markdown_report: str
    new_drug_info: DrugInfo | None = None
    ai_summary: str | None = None
    ai_model: str | None = None
