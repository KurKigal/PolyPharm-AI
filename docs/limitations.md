# Limitations & Safety Boundaries

## Clinical Status

PolyPharm AI is not a medical device and has not been validated for clinical use.

It must not be used to diagnose, prescribe, determine dose, stop/start therapy,
replace clinicians/pharmacists, or manage real patient care.

## Interaction Coverage

The curated interaction dataset is intentionally limited. Absence of a finding
does **not** mean a medication combination is safe.

## Laboratory Rules

Renal/hepatic logic is simplified prototype logic and does not include the full
clinical context required for prescribing.

## Safety Score

The score is a deterministic software heuristic. Its penalties and thresholds
have not been clinically calibrated.

## openFDA

openFDA labels are useful source material but not a complete structured
interaction database. Missing sections, wording differences, and text-scanning
false positives/negatives are possible.

## RxNorm

Normalization improves matching but does not guarantee equivalence across
formulation, strength, route, or combination products.

## Generative AI

Gemini explanations may be incorrect or incomplete. The LLM is optional and is
kept outside deterministic risk ownership.

## Evaluation

The 42-case suite is synthetic and measures regression consistency against
project-defined expectations, not clinical correctness.

## Privacy

Do not enter identifiable real-patient information into a public or third-party
demo. The project is intended for synthetic/demo data.

## Deployment

Containerization and CI show engineering deployability, not healthcare
production readiness. Real clinical deployment would require security,
governance, auditability, regulatory review, clinical validation, and incident
response work.
