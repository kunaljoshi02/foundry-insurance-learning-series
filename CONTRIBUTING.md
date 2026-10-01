# Contributing

Thanks for improving the Microsoft Foundry Insurance Learning Series.

## Ground rules

1. **Portal-first, mixed audience.** Use portal-visible paths where supported. For hosted-agent,
   identity, evaluation, and gateway capabilities requiring code or pre-staged infrastructure,
   distinguish the instructor's observable demonstration from the operator setup; do not invent
   portal-only workflows.
2. **No secrets, no tenant specifics.** Never commit tenant IDs, subscription IDs, resource names,
   endpoints, local paths, or keys. Use `<placeholders>` and `*.example.*` files.
3. **Idempotent, safe scripts.** `deploy.ps1` / `verify.ps1` / `cleanup.ps1` must support
   `-WhatIf`/dry-run, be safely re-runnable, and `cleanup.ps1` must only ever touch
   module-tagged resources and require `-Confirm`/typed confirmation for destructive actions.
4. **Preserve the insurance storyline.** Keep the claims-intake / coverage-adjudication narrative
   consistent across modules so the curriculum reads as one coherent build.
5. **Label preview/limitation caveats.** If a feature is in preview or has a known limitation
   (e.g., hosted-agent A2A, Memory networking, OBO), say so explicitly and link the verified
   behavior in `docs/known-limitations.md`.

## Module structure

Every `modules/NN-*/` folder must contain:

```
README.md            overview, learning objectives, architecture
slides.md            presenter slide deck (Markdown, one slide per `---`)
demo-runbook.md       step-by-step portal + CLI demo script
model-demo-guide.md   instructor's lesson-specific live exemplar and reset path
lab.md                hands-on exercise for learners
deploy.ps1            idempotent provisioning (WhatIf-capable)
verify.ps1            read-only post-deploy checks
cleanup.ps1           tear-down of module-owned resources only (confirmation required)
config.example.json   placeholder configuration
infra/                module-specific Bicep (if any)
src/                  module-specific code (agents, skills, functions)
tests/                offline validation (syntax, contract, unit)
```

## Validation before committing

Run `tests/run-all-validation.ps1` from the repo root. It performs **offline-only** checks:
PowerShell/Python syntax, JSON/YAML parsing, Bicep `az bicep build` (if the CLI is installed),
Markdown link sanity, and a tenant-specific/secret scan. It never calls `az deployment`,
`azd provision/deploy`, or live Foundry endpoints.

## Pull requests

- Keep changes scoped to one module or shared concern per PR where practical.
- Update `course/instructor-guide.md` and `course/capability-map.md` if you add/remove objectives.
- Include the validation output in the PR description.
