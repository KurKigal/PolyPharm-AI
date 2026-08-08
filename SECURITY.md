# Security & Responsible Use

## Sensitive Data

Do not submit real patient data, health records, credentials, API keys, or other
sensitive information to issues, pull requests, demo inputs, or repository files.

## Secrets

Local secrets belong in `.env`, which must remain untracked. `.env.example`
should contain variable names and non-secret placeholders only.

## Security Reports

Use a private repository security-reporting channel when available. Do not post
secrets, exploit credentials, or patient information publicly.

## Clinical Safety

Potentially unsafe medical-looking behavior should be reported as a prototype
limitation/bug, not as evidence that this system is approved for clinical use.

## Scope

The portfolio release is intended for educational and engineering demonstration.
No warranty of clinical suitability or healthcare regulatory compliance is provided.
