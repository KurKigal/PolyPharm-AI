"""Local JSON interaction rule provider.

The provider normalizes rule-governance metadata so existing rule files remain
backward compatible while the application gains stable IDs and versioned
provenance.
"""

import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES_PATH = PROJECT_ROOT / "data" / "demo_interactions.json"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "data" / "rule_manifest.json"

DEFAULT_DATASET_ID = "polypharm-curated-ddi"
DEFAULT_DATASET_VERSION = "1.0.0"
DEFAULT_RULE_VERSION = "1.0.0"


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "unknown"


def _derived_rule_id(drug_a: str, drug_b: str) -> str:
    pair = sorted((_slug(drug_a), _slug(drug_b)))
    return f"DDI-{pair[0]}-{pair[1]}"


class LocalJsonInteractionProvider:
    def __init__(
        self,
        data_path: Path | None = None,
        manifest_path: Path | None = None,
    ):
        self.data_path = data_path or DEFAULT_RULES_PATH
        self.manifest_path = (
            manifest_path
            if manifest_path is not None
            else (
                DEFAULT_MANIFEST_PATH
                if self.data_path == DEFAULT_RULES_PATH
                else None
            )
        )

        self._rules: list[dict[str, Any]] | None = None
        self._manifest: dict[str, Any] | None = None

    @property
    def dataset_id(self) -> str:
        return str(
            self.get_manifest().get(
                "dataset_id",
                DEFAULT_DATASET_ID,
            )
        )

    @property
    def dataset_version(self) -> str:
        return str(
            self.get_manifest().get(
                "dataset_version",
                DEFAULT_DATASET_VERSION,
            )
        )

    @property
    def evidence_reference(self) -> str:
        return f"{self.dataset_id}@{self.dataset_version}"

    def get_manifest(self) -> dict[str, Any]:
        if self._manifest is not None:
            return self._manifest

        if self.manifest_path is None or not self.manifest_path.exists():
            self._manifest = {
                "dataset_id": DEFAULT_DATASET_ID,
                "dataset_version": DEFAULT_DATASET_VERSION,
                "rule_schema_version": DEFAULT_RULE_VERSION,
                "status": "prototype",
            }
            return self._manifest

        with self.manifest_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError(
                "rule_manifest.json must contain a JSON object."
            )

        self._manifest = payload
        return self._manifest

    def get_interaction_rules(self) -> list[dict[str, Any]]:
        if self._rules is None:
            self._rules = self._load_rules()
        return self._rules

    def _load_rules(self) -> list[dict[str, Any]]:
        if not self.data_path.exists():
            return []

        with self.data_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError(
                "demo_interactions.json must contain a list of interaction rules."
            )

        return [
            self._normalize_rule(item)
            for item in payload
        ]

    def _normalize_rule(
        self,
        item: Any,
    ) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise ValueError(
                "Each interaction rule must be a JSON object."
            )

        drug_a = str(item.get("drug_a", "")).strip()
        drug_b = str(item.get("drug_b", "")).strip()

        normalized = dict(item)
        normalized.setdefault(
            "rule_id",
            _derived_rule_id(
                drug_a,
                drug_b,
            ),
        )
        normalized.setdefault(
            "rule_version",
            DEFAULT_RULE_VERSION,
        )
        normalized.setdefault(
            "category",
            "drug_interaction",
        )
        normalized.setdefault(
            "evidence_type",
            "curated_rule",
        )
        normalized.setdefault(
            "source",
            "Curated interaction rule",
        )
        normalized.setdefault(
            "evidence_reference",
            self.evidence_reference,
        )

        return normalized
