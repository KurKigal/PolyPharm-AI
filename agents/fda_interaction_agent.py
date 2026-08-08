import re

from core.localization import normalize_language
from models.schemas import Patient, RiskFinding
from providers.drug_data_service import DrugDataService
from providers.local_json_provider import LocalJsonInteractionProvider
from providers.openfda_client import OpenFdaClient

EXCERPT_RADIUS = 220
SEVERITY_WINDOW = 160
HIGH_RISK_MARKERS = (
    "contraindicated",
    "avoid",
    "should not be used",
    "do not use",
    "serious",
    "fatal",
    "life-threatening",
    "increased risk of bleeding",
)


def _normalize(value: str) -> str:
    return value.lower().strip()


def _fda_pair_key(drug_a: str, drug_b: str) -> str:
    pair = sorted(
        (
            _normalize(drug_a),
            _normalize(drug_b),
        )
    )
    return f"ddi:fda-label:{pair[0]}|{pair[1]}"


class FdaLabelInteractionAgent:
    def __init__(
        self,
        openfda_client: OpenFdaClient,
        drug_service: DrugDataService | None = None,
        rules_provider: LocalJsonInteractionProvider | None = None,
    ):
        self.openfda_client = openfda_client
        self.drug_service = drug_service
        self.rules_provider = rules_provider or LocalJsonInteractionProvider()

    def _aliases(
        self,
        drug_name: str,
    ) -> list[str]:
        aliases = [
            _normalize(
                drug_name
            )
        ]

        if self.drug_service is not None:
            for ingredient in self.drug_service.resolve_to_ingredients(
                drug_name
            ):
                if ingredient not in aliases:
                    aliases.append(
                        ingredient
                    )

        return [
            alias
            for alias in aliases
            if alias
        ]

    def _local_rule_pairs(
        self,
    ) -> set[frozenset[str]]:
        pairs: set[frozenset[str]] = set()

        for rule in self.rules_provider.get_interaction_rules():
            a = _normalize(
                rule.get(
                    "drug_a",
                    "",
                )
            )
            b = _normalize(
                rule.get(
                    "drug_b",
                    "",
                )
            )

            if a and b:
                pairs.add(
                    frozenset(
                        (
                            a,
                            b,
                        )
                    )
                )

        return pairs

    def _label_text(
        self,
        drug_name: str,
    ) -> str | None:
        query_name = drug_name

        if self.drug_service is not None:
            ingredients = self.drug_service.resolve_to_ingredients(
                drug_name
            )
            if ingredients:
                query_name = ingredients[0]

        label = self.openfda_client.get_label(
            query_name
        )
        return (
            None
            if label is None
            else label.drug_interactions_full
        )

    def _find_mention(
        self,
        text: str,
        aliases: list[str],
    ) -> tuple[str, str, str] | None:
        for alias in aliases:
            match = re.search(
                rf"\b{re.escape(alias)}\b",
                text,
                re.IGNORECASE,
            )

            if match is None:
                continue

            window_start = max(
                0,
                match.start() - SEVERITY_WINDOW,
            )
            window = text[
                window_start : match.end() + SEVERITY_WINDOW
            ].lower()

            severity = (
                "high"
                if any(
                    marker in window
                    for marker in HIGH_RISK_MARKERS
                )
                else "medium"
            )

            start = max(
                0,
                match.start() - EXCERPT_RADIUS,
            )
            end = min(
                len(text),
                match.end() + EXCERPT_RADIUS,
            )

            excerpt = text[
                start:end
            ].strip()

            if start > 0:
                excerpt = "… " + excerpt
            if end < len(text):
                excerpt += " …"

            return (
                alias,
                severity,
                excerpt,
            )

        return None

    def analyze(
        self,
        patient: Patient,
        new_medication: str,
        language: str = "tr",
    ) -> list[RiskFinding]:
        lang = normalize_language(
            language
        )
        findings: list[RiskFinding] = []

        new_aliases = self._aliases(
            new_medication
        )
        if not new_aliases:
            return findings

        local_pairs = self._local_rule_pairs()
        reported_pairs: set[frozenset[str]] = set()
        current_meds = [
            med
            for med in patient.current_medications
            if med.strip()
        ]

        def try_report(
            label_owner: str,
            current_medication: str,
            mentioned_name: str,
            mention: tuple[str, str, str],
        ) -> None:
            matched_alias, severity, excerpt = mention
            owner_alias = self._aliases(
                label_owner
            )[0]

            pair = frozenset(
                (
                    owner_alias,
                    matched_alias,
                )
            )

            if (
                len(pair) < 2
                or pair in reported_pairs
                or pair in local_pairs
            ):
                return

            reported_pairs.add(
                pair
            )

            if lang == "en":
                title = (
                    f"{new_medication} - {current_medication} "
                    "interaction (FDA label)"
                )
                description = (
                    f"The interaction section of the FDA label for {label_owner} "
                    f"contains a warning related to {mentioned_name}: “{excerpt}”"
                )
                recommendation = (
                    "Assess the official label warning in patient context and "
                    "review dose, monitoring, or therapeutic alternatives."
                )
            else:
                title = (
                    f"{new_medication} - {current_medication} "
                    "etkileşimi (FDA prospektüsü)"
                )
                description = (
                    f"{label_owner} ilacının FDA prospektüsündeki etkileşim "
                    f"bölümünde {mentioned_name} ile ilgili uyarı bulundu: "
                    f"“{excerpt}”"
                )
                recommendation = (
                    "Resmi prospektüsteki etkileşim uyarısı hasta özelinde "
                    "değerlendirilmeli; doz, izlem veya alternatif tedavi gözden "
                    "geçirilmelidir."
                )

            findings.append(
                RiskFinding(
                    title=title,
                    severity=severity,
                    description=description,
                    recommendation=recommendation,
                    category="drug_interaction",
                    evidence_type="official_label",
                    source="openFDA drug label (drug_interactions)",
                    agent="FdaLabelInteractionAgent",
                    evidence_reference="openFDA:drug_interactions",
                    dedupe_key=_fda_pair_key(
                        new_medication,
                        current_medication,
                    ),
                )
            )

        new_text = self._label_text(
            new_medication
        )
        if new_text:
            for medication in current_meds:
                mention = self._find_mention(
                    new_text,
                    self._aliases(
                        medication
                    ),
                )
                if mention is not None:
                    try_report(
                        new_medication,
                        medication,
                        medication,
                        mention,
                    )

        for medication in current_meds:
            med_text = self._label_text(
                medication
            )
            if not med_text:
                continue

            mention = self._find_mention(
                med_text,
                new_aliases,
            )
            if mention is not None:
                try_report(
                    medication,
                    medication,
                    new_medication,
                    mention,
                )

        return findings
