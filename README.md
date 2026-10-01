# Microsoft Foundry Insurance Learning Series

A customer-ready, **portal-first**, mixed-audience curriculum for **Microsoft Foundry Agent
Service**, told through one continuous insurance storyline: a claims-intake triage agent that
investigates FNOLs, grounds coverage decisions in policy wording, and delegates settlement
adjudication to a specialist agent.

Eight sessions build **additively** on one shared, public Foundry foundation — every module adds
capability without breaking the ones before it. The early lessons are portal-first; hosted-agent,
identity, evaluation, and gateway segments also use prepared assets or offline code demonstrations
where the capability is not a portal-only workflow.

> ⚠️ This repository never deploys, modifies, or deletes any Azure resources on its own. All
> `deploy.ps1`/`verify.ps1`/`cleanup.ps1` scripts require a human to run them explicitly, in their
> own sandbox subscription, against the shared [`foundation/`](foundation/) base.

## Curriculum

| # | Module | Focus |
| --- | --- | --- |
| 1 | [Foundations + first prompt agent](modules/01-foundations-first-agent/) | Portal tour, Foundry concepts, first prompt agent, instructions & playground testing |
| 2 | [Tools, Skills & toolbox](modules/02-tools-skills-toolbox/) | Built-in tools, versioned Skills, toolbox composition and reuse |
| 3 | [Azure AI Search grounding / Foundry IQ patterns](modules/03-search-grounding-foundry-iq/) | Index the policy-wording corpus, ground answers with citations |
| 4 | [Hosted agents + multi-agent orchestration](modules/04-hosted-agents-orchestration/) | Agent Framework hosted agents, A2A orchestration, tested `HostedAgentNotSupported` detection + Responses fallback |
| 5 | [Managed Memory + user scope/privacy](modules/05-managed-memory-privacy/) | Cross-conversation preference memory, scoped to signed-in identity, privacy controls |
| 6 | [Identity, RBAC, auth & OBO](modules/06-identity-rbac-auth-obo/) | Managed identity, least-privilege RBAC, on-behalf-of (OBO) token flow |
| 7 | [Observability, evaluation, optimization, trust & safety](modules/07-observability-evaluation-trust-safety/) | OTel tracing, evaluation datasets, content safety, grounding/fraud guardrails |
| 8 | [APIM + private networking + operate capstone](modules/08-apim-networking-capstone/) | BYOM via APIM, optional **disabled-by-default** private-networking enterprise overlay |

See [`course/capability-map.md`](course/capability-map.md) for the full objective → module → asset
matrix and [`course/instructor-guide.md`](course/instructor-guide.md) for delivery guidance.

## Instructor model demo guides

Each guide is a lesson-specific live exemplar: use its slide-linked opening, copy/paste insurance
inputs, expected evidence, recovery path, and reset steps alongside the detailed
`demo-runbook.md`. Prepare the assets and access ahead of class; the guides do not provision Azure
resources.

| Lesson | Model demo guide |
| --- | --- |
| 1 · First claims agent | [Foundations and first agent](modules/01-foundations-first-agent/model-demo-guide.md) |
| 2 · Reusable capabilities | [Tools, Skills and toolbox](modules/02-tools-skills-toolbox/model-demo-guide.md) |
| 3 · Evidence-backed coverage | [Search grounding and Foundry IQ](modules/03-search-grounding-foundry-iq/model-demo-guide.md) |
| 4 · Specialist handoff | [Hosted agents and orchestration](modules/04-hosted-agents-orchestration/model-demo-guide.md) |
| 5 · Scoped preferences | [Managed Memory and privacy](modules/05-managed-memory-privacy/model-demo-guide.md) |
| 6 · Access boundaries | [Identity, RBAC, authentication and OBO](modules/06-identity-rbac-auth-obo/model-demo-guide.md) |
| 7 · Measurable quality | [Observability, evaluation, trust and safety](modules/07-observability-evaluation-trust-safety/model-demo-guide.md) |
| 8 · Operated capstone | [APIM, networking and operations](modules/08-apim-networking-capstone/model-demo-guide.md) |

## Repository layout

```
foundation/            Shared public Bicep (Foundry account + project + model + RBAC) + preflight
modules/01..08/         One folder per session: README, slides, model demo guide, runbook, lab, scripts, infra/src/tests
shared/
  python/               Config loader, secret scanner, small reusable helpers
  powershell/           Common.ps1 (tag-gated cleanup helpers, config loader, prompts)
  bicep/                Reusable RBAC-assignment module
  schema/               JSON Schemas for module config and evaluation cases
  test-data/            Synthetic 36-clause policy-wording corpus (Contoso Home/Motor/Liability)
course/                 Instructor guide, prerequisites, capability map, troubleshooting, glossary
tests/                  Offline repo-wide validation (syntax, JSON/YAML, secret scan, Bicep build)
docs/known-limitations.md   Verified preview/limitation behavior, with Microsoft Learn citations
```

## Quick start

1. Read [`course/prerequisites.md`](course/prerequisites.md) and run
   [`foundation/scripts/preflight.ps1`](foundation/scripts/preflight.ps1) (read-only checks).
2. Deploy the shared foundation into your own sandbox subscription — see
   [`foundation/README.md`](foundation/README.md).
3. Start with [Module 1](modules/01-foundations-first-agent/README.md) and proceed in order; each
   module's `README.md` states what it assumes from prior modules.
4. Run `tests/run-all-validation.ps1` before committing any change — it is 100% offline.

## What's verified vs. what's a learning asset

Some behaviors in this curriculum (hosted-agent A2A `HostedAgentNotSupported`, managed Memory
preview networking constraints, OBO's interactive-user requirement, private-portal network access)
were observed against a deployed enterprise reference build and are called out explicitly in
[`docs/known-limitations.md`](docs/known-limitations.md) and each affected module's `README.md`.
Everything else is a from-scratch, portal-first learning asset designed for this course.

## License

[MIT](LICENSE). See [`SECURITY.md`](SECURITY.md) for the no-secrets policy and
[`CONTRIBUTING.md`](CONTRIBUTING.md) for module conventions and validation steps.
