# Security Policy

## Supported use

This repository is a **learning curriculum**, not a production service. All infrastructure
templates deploy a **public**, non-production Microsoft Foundry account and project intended for
sandbox subscriptions. Do not use these assets to store real customer, policyholder, or claims
data — all sample data in `shared/test-data/` and module `data/` folders is synthetic.

## No secrets in this repository

- No tenant IDs, subscription IDs, resource names, endpoints, connection strings, API keys, or
  local file paths are committed. All examples use placeholders (`<...>`) and `.example` files.
- Every module's `config.example.json` must be copied to `config.json` (git-ignored) and filled in
  locally before running scripts.
- Run `tests/scan-secrets.ps1` (or the equivalent module validation script) before committing to
  catch accidental leakage.

## Reporting a vulnerability

If you discover a security issue in this curriculum (e.g., a script that could leak credentials,
an insecure default, or a Bicep template that over-provisions access), please open a private
security advisory on this repository rather than a public issue. Include reproduction steps and
the affected file(s). We aim to acknowledge reports within 5 business days.

For vulnerabilities in Microsoft Foundry, Azure AI Search, APIM, or other Azure services
themselves (not this curriculum's code), report them via the
[Microsoft Security Response Center](https://msrc.microsoft.com/create-report).
