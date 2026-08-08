# v1.0.0 Portfolio Release Guide

`v1.0.0` is an **engineering / portfolio prototype release**, not a clinical product release.

## Verify

```powershell
python -m pip install -r requirements-dev.txt
python scripts/verify.py
```

Expected gates:

- Ruff
- targeted mypy
- pytest + coverage
- 42-case synthetic evaluation

## Verify Docker

```powershell
docker build -t polypharm-ai:v1.0.0 .
docker run --rm -p 8501:8501 polypharm-ai:v1.0.0
```

Check `http://localhost:8501`.

Verify both languages, offline deterministic analysis, score breakdown, Markdown
download, and provenance in raw output.

## Review Secrets

```powershell
git status
git ls-files .env
```

`.env` must not be tracked. Review the repo for API keys, tokens, private URLs,
real patient data, and local credentials.

## Licensing Checkpoint

Before adding an open-source license, confirm you have rights to license all
relevant repository content, including any earlier contributor-authored code.

## Recommended Screenshots

1. English result
2. Turkish result
3. "Why this score?" breakdown
4. provenance-rich finding
5. synthetic evaluation terminal output

## Final Commit

```powershell
git add .
git commit -m "docs: prepare PolyPharm AI v1.0.0 portfolio release"
git push origin main
```

Wait for CI to be green.

## Tag

```powershell
git tag -a v1.0.0 -m "PolyPharm AI v1.0.0"
git push origin v1.0.0
```

## Suggested GitHub Release

Title:

```text
PolyPharm AI v1.0.0 — Explainable Prescription Safety Prototype
```

Body:

```text
PolyPharm AI v1.0.0 is the first portfolio release of the project.

Highlights:
- deterministic drug-interaction and laboratory-risk pipeline
- RxNorm normalization and optional openFDA enrichment
- explainable versioned safety scoring
- rule/evidence provenance and conservative deduplication
- bilingual English/Turkish reports and UI
- optional Gemini explanation layer
- 42-case deterministic synthetic evaluation suite
- Dockerized runtime and CI quality gates

Synthetic baseline:
- 42/42 cases passed
- 39/39 expected rules detected
- 100% risk-level agreement
- 100% score-range agreement

Important: these are synthetic software-regression metrics, not clinical
validation results. The project is not a medical device and must not be used
for real patient care.
```

## Portfolio Framing

Good claims:

- built an explainable deterministic decision-support prototype
- implemented rule provenance and versioned score attribution
- designed an offline synthetic evaluation pipeline
- separated generative explanation from deterministic risk logic
- containerized the application and added CI quality gates

Avoid claims such as "100% medically accurate", "detects all interactions", or
"clinically validated".
