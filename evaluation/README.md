# PolyPharm AI Synthetic Evaluation

This directory contains a deterministic software evaluation suite for the
PolyPharm AI prototype.

## What this evaluates

The suite checks whether the current implementation behaves consistently with
the project's documented prototype rules:

- curated drug-drug interaction detection,
- renal-risk rules,
- hepatic-risk rules,
- polypharmacy rules,
- expected scoring-policy behavior,
- expected risk-level behavior,
- unexpected deterministic findings.

The default suite runs with:

- `openFDA = disabled`
- `Gemini = disabled`

This makes the evaluation repeatable and independent of network/API behavior.

## What this does NOT evaluate

This suite is **not clinical validation**.

The expected labels are derived from the project's current prototype rule set.
A 100% result means the software matches those documented expectations; it does
not prove medical correctness, diagnostic accuracy, prescribing safety, or
medical-device performance.

## Dataset

`cases.json` currently contains:

- all curated DDI rules as positive controls,
- negative-control medication pairs,
- renal cases,
- hepatic cases,
- polypharmacy cases,
- a combined multi-signal case.

## Run

```powershell
python scripts/run_evaluation.py --strict
```

Generate local result artifacts:

```powershell
python scripts/run_evaluation.py `
  --strict `
  --output evaluation/results/latest.json `
  --markdown evaluation/results/latest.md
```

The `latest.*` outputs are intentionally ignored by Git. Once a result is
reviewed and considered a useful project baseline, copy it to a versioned file
such as:

```text
evaluation/results/baseline-v1.0.0.json
evaluation/results/baseline-v1.0.0.md
```

and commit that versioned baseline.

## Primary metrics

- **Case pass rate** — percentage of cases satisfying all configured expectations.
- **Expected-rule recall** — expected rule IDs detected by the engine.
- **Risk-level agreement** — agreement with expected prototype risk levels.
- **Score-range agreement** — scores falling inside configured expected ranges.
- **Unexpected findings** — deterministic findings not declared by the case.

These metrics are regression/behavioral engineering metrics, not clinical
performance metrics.
