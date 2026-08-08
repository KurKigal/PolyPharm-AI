# Changelog

## [1.0.0] - 2026-08-08

### Added

- modular Streamlit architecture
- English / Turkish localization
- canonical language-independent domain values
- bilingual deterministic findings and reporting
- optional bilingual Gemini explanation
- explainable score attribution
- finding category/evidence metadata
- rule IDs, versions, and evidence references
- conservative duplicate suppression
- versioned scoring policy
- 42-case deterministic synthetic evaluation
- Ruff, mypy, coverage, and pre-commit configuration
- Docker / Docker Compose runtime
- GitHub Actions quality, evaluation, and container gates
- release-quality architecture, methodology, evaluation, and limitation docs

### Baseline

```text
42/42 cases passed
39/39 expected rules detected
100.0% risk-level agreement
100.0% score-range agreement
0 unexpected findings
```

These are synthetic software-regression metrics, not clinical validation.

### Safety

This release remains an educational/research engineering prototype and is not
intended for diagnosis, prescribing, treatment decisions, or real patient care.
