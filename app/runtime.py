from __future__ import annotations

import json
import logging
from pathlib import Path

import streamlit as st

from agents.orchestrator import Orchestrator
from models.schemas import LabValues, Patient
from providers.rxnorm_provider import RxNormProvider

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
LOGGER = logging.getLogger(__name__)


@st.cache_data
def load_json_file(path: Path) -> list[dict]:
    if not path.exists():
        LOGGER.warning("Data file not found: %s", path)
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        LOGGER.exception("Could not read data file: %s", path)
        return []

    if not isinstance(payload, list):
        LOGGER.warning("Data file root is not a list: %s", path)
        return []

    return payload


@st.cache_resource
def get_rxnorm_provider() -> RxNormProvider:
    return RxNormProvider()


@st.cache_resource
def get_orchestrator(use_openfda: bool, use_ai_summary: bool) -> Orchestrator:
    """Reuse the orchestrator so provider caches survive Streamlit reruns."""
    return Orchestrator(use_openfda=use_openfda, use_ai_summary=use_ai_summary)


def build_patient(
    *,
    age: int,
    gender: str,
    current_medications: list[str],
    egfr: float,
    creatinine: float,
    ast: float,
    alt: float,
) -> Patient:
    return Patient(
        age=age,
        gender=gender,
        current_medications=current_medications,
        lab_values=LabValues(
            egfr=egfr,
            creatinine=creatinine,
            ast=ast,
            alt=alt,
        ),
    )
