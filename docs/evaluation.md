# Evaluation

## Purpose

The evaluation framework tests whether the deterministic implementation behaves
consistently with the project's documented synthetic expectations.

It does **not** measure clinical accuracy.

## Dataset

```text
polypharm-synthetic-evaluation@1.0.0
```

The suite contains **42 synthetic cases**:

- 29 curated DDI positive controls,
- 5 negative controls,
- renal cases,
- hepatic cases,
- polypharmacy cases,
- one combined multi-signal case.

openFDA and Gemini are disabled during deterministic evaluation.

## Latest Reviewed Baseline

Local run recorded on **2026-08-08**:

```text
Dataset: polypharm-synthetic-evaluation@1.0.0
Scoring policy: 1.1.0
Cases: 42/42 passed (100.0%)
Expected-rule recall: 100.0% (39/39)
Risk-level agreement: 100.0%
Score-range agreement: 100.0%
Unexpected findings: 0
Duplicates suppressed: 0
```

Automated test suite at the corresponding development milestone:

```text
74 passed
```

## Metric Meaning

- **Case pass rate:** all configured expectations for a case pass.
- **Expected-rule recall:** matched project-defined expected rule IDs / expected IDs.
- **Risk-level agreement:** engine canonical risk equals configured synthetic expectation.
- **Score-range agreement:** calculated score falls inside the configured range.
- **Unexpected findings:** deterministic findings not declared by a strict case.

These are regression/behavioral engineering metrics, not clinical sensitivity,
specificity, or diagnostic accuracy.

## Run

```bash
python scripts/run_evaluation.py --strict
```

Generate local artifacts:

```powershell
python scripts/run_evaluation.py `
  --strict `
  --output evaluation/results/latest.json `
  --markdown evaluation/results/latest.md
```

## Future Work

Research-grade evaluation would require independent evidence such as
expert-reviewed annotation, externally sourced references, larger negative
controls, ontology/class cases, normalization edge cases, calibration studies,
and properly governed real-world or retrospective data.
