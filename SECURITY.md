# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities **privately** — do not open a public issue or PR.

Use GitHub's private reporting: the repository's **Security** tab → **Report a vulnerability**
(Private Vulnerability Reporting). This opens a confidential advisory visible only to maintainers.

When reporting, please include:

- the affected component or file path,
- steps to reproduce (or a proof of concept),
- the impact, and
- any suggested fix, if you have one.

We aim to acknowledge a report within **3 business days** and to share a remediation timeline after
triage. Please give us a reasonable window to fix the issue before any public disclosure.

## Supported versions

This project is **pre-release and under active development**. Only the `main` branch is supported —
fixes land there; there are no tagged releases yet.

| Version | Supported |
| --- | --- |
| `main` (latest) | ✅ |
| anything else | ❌ |

## Scope

**In scope:** the application code under `src/`, the CI / GitHub Actions workflow configuration, and
committed configuration and seed data.

**Out of scope:** third-party reference data mirrored into the repo, and vulnerabilities in
dependencies — report those upstream (Dependabot tracks known advisories for this repo). This is a
research/prototype system that emits *informational forecasts*; it executes no trades and is not
investment advice.
