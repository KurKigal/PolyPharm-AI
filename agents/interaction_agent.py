from pathlib import Path

from core.localization import localize_value, normalize_language
from models.schemas import Patient, RiskFinding
from providers.drug_data_service import DrugDataService
from providers.local_json_provider import LocalJsonInteractionProvider


def _normalize_drug_name(value: str) -> str:
    return value.lower().strip()


def _pair_key(drug_a: str, drug_b: str) -> str:
    pair = sorted(
        (
            _normalize_drug_name(drug_a),
            _normalize_drug_name(drug_b),
        )
    )
    return f"ddi:curated:{pair[0]}|{pair[1]}"


class InteractionAgent:
    """Check curated drug-drug interaction rules with RxNorm alias expansion."""

    def __init__(
        self,
        rules_provider: LocalJsonInteractionProvider | None = None,
        drug_service: DrugDataService | None = None,
        data_path: Path | None = None,
    ):
        self.rules_provider = rules_provider or LocalJsonInteractionProvider(
            data_path
        )
        self.drug_service = drug_service

    def _aliases(self, drug_name: str) -> set[str]:
        aliases = {
            _normalize_drug_name(
                drug_name
            )
        }

        if self.drug_service is not None:
            aliases.update(
                self.drug_service.resolve_to_ingredients(
                    drug_name
                )
            )

        return {
            alias
            for alias in aliases
            if alias
        }

    def analyze(
        self,
        patient: Patient,
        new_medication: str,
        language: str = "tr",
    ) -> list[RiskFinding]:
        lang = normalize_language(language)

        current_aliases: set[str] = set()
        for medication in patient.current_medications:
            if medication.strip():
                current_aliases.update(
                    self._aliases(
                        medication
                    )
                )

        new_aliases = self._aliases(
            new_medication
        )

        findings: list[RiskFinding] = []
        matched_rules: set[str] = set()

        for item in self.rules_provider.get_interaction_rules():
            drug_a = _normalize_drug_name(
                item.get(
                    "drug_a",
                    "",
                )
            )
            drug_b = _normalize_drug_name(
                item.get(
                    "drug_b",
                    "",
                )
            )

            if not drug_a or not drug_b:
                continue

            rule_id = str(
                item.get(
                    "rule_id",
                    f"DDI-{drug_a}-{drug_b}",
                )
            )

            if rule_id in matched_rules:
                continue

            exists = (
                drug_a in new_aliases
                and drug_b in current_aliases
            ) or (
                drug_b in new_aliases
                and drug_a in current_aliases
            )

            if not exists:
                continue

            matched_rules.add(
                rule_id
            )

            title = (
                f"{item['drug_a']} - {item['drug_b']} interaction"
                if lang == "en"
                else f"{item['drug_a']} - {item['drug_b']} etkileşimi"
            )

            description = localize_value(
                item.get(
                    "description"
                ),
                lang,
                fallback=(
                    "An interaction rule was found for this medication combination."
                    if lang == "en"
                    else "Bu ilaç kombinasyonu için etkileşim kuralı bulundu."
                ),
            )
            recommendation = localize_value(
                item.get(
                    "recommendation"
                ),
                lang,
                fallback=(
                    "Reassess the combination in clinical context."
                    if lang == "en"
                    else "Kombinasyonu klinik bağlamda yeniden değerlendirin."
                ),
            )

            findings.append(
                RiskFinding(
                    title=title,
                    severity=item.get(
                        "severity",
                        "medium",
                    ),
                    description=description,
                    recommendation=recommendation,
                    category=item.get(
                        "category",
                        "drug_interaction",
                    ),
                    evidence_type=item.get(
                        "evidence_type",
                        "curated_rule",
                    ),
                    source=item.get(
                        "source",
                        "Curated interaction database",
                    ),
                    agent="InteractionAgent",
                    rule_id=rule_id,
                    rule_version=item.get(
                        "rule_version"
                    ),
                    evidence_reference=item.get(
                        "evidence_reference",
                        self.rules_provider.evidence_reference,
                    ),
                    dedupe_key=_pair_key(
                        drug_a,
                        drug_b,
                    ),
                )
            )

        return findings
