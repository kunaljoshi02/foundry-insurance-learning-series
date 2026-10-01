# Instructor guide

## Audience

Mixed: business/insurance stakeholders (claims, underwriting, coverage SMEs) and developers/platform
engineers. Each module's `README.md` states whether a section is portal-visible (everyone) or
code-level (developer-led, business-observed).

## Delivery format

- 8 sessions, one module each, ~60–90 minutes per session (slides ~20 min, demo ~25 min, lab
  ~20–30 min, Q&A buffer).
- Deliver in order — each module explicitly assumes the agent/asset state left by the previous one
  (see each `README.md`'s "relationship to prior modules" section).
- Use `slides.md` as the presenter deck (one slide per `---`-delimited section); render with any
  Markdown-to-slides tool or present directly from a Markdown viewer.

## Model demo guide index

Use each `model-demo-guide.md` as the canonical lesson-specific performance: it identifies the
opening slides, exact insurance input, observable result, intentional boundary, audience questions,
recovery, and reset. The adjacent `demo-runbook.md` remains the detailed portal/CLI procedure and
the `lab.md` is for learner practice.

| Session | Instructor exemplar |
| --- | --- |
| 1 | [Foundations and first claims agent](../modules/01-foundations-first-agent/model-demo-guide.md) |
| 2 | [Tools, Skills and toolbox](../modules/02-tools-skills-toolbox/model-demo-guide.md) |
| 3 | [Search grounding and Foundry IQ](../modules/03-search-grounding-foundry-iq/model-demo-guide.md) |
| 4 | [Hosted agents and orchestration](../modules/04-hosted-agents-orchestration/model-demo-guide.md) |
| 5 | [Managed Memory and privacy](../modules/05-managed-memory-privacy/model-demo-guide.md) |
| 6 | [Identity, RBAC, authentication and OBO](../modules/06-identity-rbac-auth-obo/model-demo-guide.md) |
| 7 | [Observability, evaluation, trust and safety](../modules/07-observability-evaluation-trust-safety/model-demo-guide.md) |
| 8 | [APIM, networking and operating the capstone](../modules/08-apim-networking-capstone/model-demo-guide.md) |

## Before the course starts

1. Walk through `course/prerequisites.md` with participants at least a week ahead.
2. Deploy the shared foundation (`foundation/README.md`) into a sandbox subscription — do this
   once, ahead of Module 1, so Module 1 starts from a working project rather than spending time on
   infrastructure.
3. Run `tests/run-all-validation.ps1` to confirm the repository checkout is clean before presenting.

## Per-module flow

1. Open with `slides.md`'s agenda slide.
2. Walk the architecture diagram in `README.md`.
3. Use `model-demo-guide.md` for its 5–10 minute slide-linked context and timed live exemplar;
   consult `demo-runbook.md` for detailed portal/CLI steps. Use module scripts only where the
   guide marks a code-level or pre-staged segment; do not imply that a code-level capability is
   available as a portal click.
4. Assign `lab.md` as a hands-on exercise; circulate while the group works through its "done when"
   checklist.
5. Close with the "next-module teaser" slide and any noted limitation callouts from
   `docs/known-limitations.md` relevant to that module.

## Facilitation notes by module

- **Module 1–3 (prompt agents, tools/skills, grounding):** fully portal-doable; lean into live
  portal clicking for the non-developer audience.
- **Module 4 (hosted agents/A2A):** code-heavy. Pre-run the module's unit tests before class and
  show the test output live — the `HostedAgentNotSupported` detection is the single most important
  concept in the curriculum; don't rush it.
- **Module 5 (Memory):** emphasize the privacy angle as much as the recall demo — show the purge
  flow, not just the "it remembers you" moment.
- **Module 6 (identity/RBAC/OBO):** keep the least-privilege RBAC portion business-relevant
  ("why we don't just grant Owner"); the OBO interactive-user limitation is a good discussion
  prompt for platform teams.
- **Module 7 (observability/evaluation/trust&safety):** run the offline evaluator live — it is
  fast and 100% safe to execute in front of the room.
- **Module 8 (capstone):** use `verify.ps1 -RunAllModuleVerifications` as the big finish — a single
  command that reports health across the whole curriculum. Clearly flag the enterprise overlay as
  optional/disabled-by-default and do not enable it live.

## Troubleshooting

See `course/troubleshooting.md` for common per-module issues and `docs/known-limitations.md` for
behavior that is expected rather than a bug.
