# Architecture

## Design Goals

PolyPharm AI is structured around five engineering goals:

1. deterministic risk ownership,
2. explainability,
3. provenance,
4. failure tolerance,
5. separation of concerns.

## High-Level Architecture

```mermaid
flowchart TB
    subgraph UI["Presentation"]
        ST[Streamlit]
        I18N[Localization]
    end
    subgraph DOMAIN["Application / Domain"]
        ORCH[Orchestrator]
        IA[InteractionAgent]
        LA[LabRiskAgent]
        FA[FdaLabelInteractionAgent]
        DEDUPE[Finding Deduplication]
        SCORE[ScoringAgent]
        REPORT[ReportAgent]
        GEM[GeminiExplainer]
    end
    subgraph DATA["Providers / Data"]
        DDS[DrugDataService]
        RX[RxNorm SQLite]
        LOCAL[Curated DDI JSON]
        FDA[openFDA]
    end

    ST --> ORCH
    I18N --> ST
    ORCH --> IA
    ORCH --> LA
    ORCH --> FA
    IA --> DDS
    FA --> DDS
    DDS --> RX
    IA --> LOCAL
    DDS --> FDA
    IA --> DEDUPE
    LA --> DEDUPE
    FA --> DEDUPE
    DEDUPE --> SCORE
    SCORE --> REPORT
    SCORE --> GEM
    GEM --> REPORT
```

## Layer Responsibilities

### `app/`
Presentation, Streamlit components, localization, score-breakdown rendering,
report download.

### `agents/`
`InteractionAgent` matches curated DDI rules. `LabRiskAgent` creates simplified
renal/hepatic/polypharmacy findings. `FdaLabelInteractionAgent` scans official
label text. `ScoringAgent` owns deterministic scoring. `ReportAgent` generates
localized reports. `GeminiExplainer` is optional explanation only.
`Orchestrator` coordinates the complete workflow.

### `core/`
Finding deduplication, localization helpers, and versioned scoring policy.

### `providers/`
RxNorm, openFDA, local JSON rules, and the drug-data facade.

### `models/`
Pydantic contracts: `Patient`, `PrescriptionRequest`, `RiskFinding`,
`ScoreContribution`, `ScoreBreakdown`, and `AnalysisResult`.

### `evaluation/`
Offline deterministic behavioral/regression evaluation.

## Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit
    participant O as Orchestrator
    participant R as RxNorm
    participant A as Analysis Agents
    participant S as ScoringAgent
    participant G as Gemini
    participant P as ReportAgent

    U->>UI: Patient + medication input
    UI->>O: PrescriptionRequest
    O->>R: Normalize medication
    R-->>O: Normalized information
    O->>A: Run deterministic rules
    A-->>O: RiskFinding[]
    O->>O: Deduplicate exact logical duplicates
    O->>S: Score findings
    S-->>O: score + risk + breakdown
    opt Gemini enabled
        O->>G: Explain structured result
        G-->>O: Natural-language explanation
    end
    O->>P: Build localized report
    P-->>O: Markdown
    O-->>UI: AnalysisResult
```

## Trust Boundary

The main trust boundary separates deterministic risk logic from generative
explanation. Gemini receives structured findings after deterministic analysis;
it does not own risk decisions or scoring.

## Failure Modes

- **RxNorm unavailable:** analysis can continue with entered names; normalization quality decreases.
- **openFDA unavailable:** local rules, lab rules, scoring, and reporting continue.
- **Gemini unavailable:** deterministic output remains complete.
- **Rule absent:** no local DDI finding is produced; absence does not imply safety.

## Scoring Architecture

`ScoringPolicy` separates scoring configuration from scoring execution.
`ScoreBreakdown` records policy version, category penalties, contribution order,
base/applied penalties, provenance, and duplicate-suppression count.

## Deployment

The app can run directly, through Docker, or with Docker Compose. The container
uses a non-root user and Streamlit's `/_stcore/health` endpoint.
