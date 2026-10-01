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

## Before the course starts

1. Walk through `course/prerequisites.md` with participants at least a week ahead.
2. Deploy the shared foundation (`foundation/README.md`) into a sandbox subscription — do this
   once, ahead of Module 1, so Module 1 starts from a working project rather than spending time on
   infrastructure.
3. Run `tests/run-all-validation.ps1` to confirm the repository checkout is clean before presenting.

## Per-module flow

1. Open with `slides.md`'s agenda slide.
2. Walk the architecture diagram in `README.md`.
3. Run `demo-runbook.md` live (portal-first; fall back to the module's `deploy.ps1`/`verify.ps1`
   only to save time, and say so explicitly — the point is that the portal path works too).
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
