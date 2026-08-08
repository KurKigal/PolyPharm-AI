from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from models.schemas import Patient, RiskLevel


class ScoreExpectation(BaseModel):
    min: int = Field(..., ge=0, le=100)
    max: int = Field(..., ge=0, le=100)

    @model_validator(mode="after")
    def validate_range(self):
        if self.max < self.min:
            raise ValueError("expected score max must be >= min")
        return self


class EvaluationCase(BaseModel):
    id: str = Field(..., min_length=1)
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    language: str = "en"

    patient: Patient
    new_medication: str = Field(..., min_length=1)

    expected_rule_ids: list[str] = Field(default_factory=list)
    expected_risk_level: RiskLevel | None = None
    expected_score: ScoreExpectation | None = None

    allow_unexpected_findings: bool = False


class EvaluationDataset(BaseModel):
    dataset_id: str
    dataset_version: str
    clinical_ground_truth: bool = False
    description: str = ""
    limitations: str = ""
    cases: list[EvaluationCase]


class CaseEvaluation(BaseModel):
    case_id: str
    passed: bool

    expected_rule_ids: list[str]
    actual_rule_ids: list[str]
    matched_rule_ids: list[str]
    missing_rule_ids: list[str]
    unexpected_findings: list[str]

    expected_risk_level: RiskLevel | None = None
    actual_risk_level: RiskLevel

    expected_score_min: int | None = None
    expected_score_max: int | None = None
    actual_score: int

    risk_level_match: bool
    score_match: bool
    finding_expectations_match: bool

    duplicates_suppressed: int = 0
    execution_error: str | None = None


class EvaluationSummary(BaseModel):
    dataset_id: str
    dataset_version: str
    scoring_policy_version: str

    total_cases: int
    passed_cases: int
    failed_cases: int
    case_pass_rate: float

    expected_rule_count: int
    matched_rule_count: int
    expected_rule_recall: float

    risk_level_cases: int
    risk_level_matches: int
    risk_level_accuracy: float

    score_expectation_cases: int
    score_matches: int
    score_range_accuracy: float

    unexpected_finding_count: int
    duplicates_suppressed: int

    cases: list[CaseEvaluation]
