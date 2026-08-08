# Methodology

## Scope

PolyPharm AI is an engineering/research prototype. The methodology prioritizes
reproducibility and traceability over claims of clinical completeness.

## Medication Normalization

Medication names may be resolved through a local RxNorm-backed provider to
improve matching between brands, generic names, ingredients, and curated rules.

Normalization is a matching aid, not proof of safety or risk.

## Curated DDI Rules

Each local interaction rule receives governance metadata:

- stable `rule_id`,
- `rule_version`,
- category,
- evidence type,
- dataset reference.

Current dataset identity:

```text
polypharm-curated-ddi@1.0.0
```

The dataset is intentionally limited.

## Laboratory / Polypharmacy Rules

Simplified prototype rules generate findings from eGFR, AST/ALT, medication
count, and age plus medication count. These are marked as `prototype_rule`,
not clinically validated dosing rules.

## openFDA Enrichment

When enabled, openFDA can contribute boxed-warning and interaction-label
context. Official excerpts remain in their source language.

## Provenance

Each `RiskFinding` can preserve:

```text
category
evidence_type
source
agent
rule_id
rule_version
evidence_reference
dedupe_key
```

## Duplicate Handling

Only findings intentionally sharing the same logical `dedupe_key` are collapsed.
The more severe duplicate is retained. Independent evidence sources are not
silently merged merely because they concern the same medication pair.

## Scoring

| Severity | Base penalty |
|---|---:|
| critical | 50 |
| high | 35 |
| medium | 20 |
| low | 10 |

The score begins at 100 and is floored at 0. Critical findings force canonical
risk level `critical`.

The score is deterministic and explainable but **not clinically calibrated**.

Category caps are supported by the engine but disabled by default to avoid
inventing false clinical precision without an evaluation basis.

## Generative AI

Gemini is optional and does not determine rule matches, severity, risk level, or
safety score. It explains already-computed structured findings.

## Localization

User-facing output supports English and Turkish while canonical values remain
language-independent:

```text
risk: low / medium / high / critical
gender: female / male / other
severity: low / medium / high / critical
```

## Evaluation

The synthetic suite runs with external integrations disabled for reproducibility.
It tests expected rules, score ranges, risk levels, and unexpected findings.

It is not clinical ground truth or medical-device validation.
