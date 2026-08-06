<div align="center">

# PolyPharm AI

### Explainable polypharmacy risk analysis and prescription safety support

PolyPharm AI is an educational clinical decision-support prototype that
combines deterministic risk rules, RxNorm drug normalization, openFDA drug
labels and optional LLM-generated explanations.

 [Architecture](docs/architecture.md) ·
[Methodology](docs/methodology.md) · [Limitations](docs/limitations.md)

</div>

> [!WARNING]
> PolyPharm AI is a research and educational prototype.
> It is not a medical device and must not be used for diagnosis,
> prescribing, treatment decisions or real patient care.

## Overview

Polypharmacy is the concurrent use of multiple medications and is especially
common among older adults and patients with chronic conditions.

Evaluating a new prescription may require clinicians to consider:

- potential drug-drug interactions,
- kidney function,
- liver function,
- patient age,
- medication count,
- boxed warnings,
- and incomplete or conflicting drug information.

PolyPharm AI demonstrates how these signals can be collected and presented in
an explainable, modular and failure-tolerant software architecture.

The system does not replace clinical judgement. Its purpose is to explore
software engineering and AI patterns for clinical decision-support systems.

## Key Features

- Medication name normalization using a local RxNorm SQLite database
- Brand-to-ingredient resolution
- Rule-based drug-drug interaction analysis
- Kidney and liver risk screening
- Age and polypharmacy risk analysis
- openFDA drug-label and boxed-warning retrieval
- FDA label interaction scanning
- Explainable safety score
- Risk findings with severity, source and recommendation
- Optional Turkish clinical explanation generated with Google Gemini
- Offline fallback when external services are unavailable
- Markdown report export
- JSON analysis output
- Automated unit, integration and smoke tests
- GitHub Actions continuous integration

## How It Works

```mermaid
flowchart LR
    UI[Streamlit Interface]
    INPUT[Patient and Prescription Input]
    RX[RxNorm Normalization]
    RULES[Local Interaction Rules]
    LAB[Laboratory Risk Analysis]
    FDA[openFDA Drug Labels]
    SCORE[Explainable Scoring]
    REPORT[Report Generator]
    LLM[Optional Gemini Explanation]

    UI --> INPUT
    INPUT --> RX
    RX --> RULES
    INPUT --> LAB
    RX --> FDA
    RULES --> SCORE
    LAB --> SCORE
    FDA --> SCORE
    SCORE --> REPORT
    SCORE --> LLM
    LLM --> REPORT
