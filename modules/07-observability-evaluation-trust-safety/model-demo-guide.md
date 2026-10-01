# Module 07 — Instructor model demo: observability, evaluation, and trust

**Performance length:** 6-minute slide context + 8-minute live exemplar · **Slides:** [slides 1–17](slides.md) · **Mode:** offline-first

## Outcome and audience promise

Show three distinct operating questions with runnable evidence: tracing asks what happened, evaluation asks whether routing matched expected behavior, and lightweight safety checks flag patterns requiring review. Learners see a reproducible scorecard and why deterministic checks are signals—not a production decision engine.

Business participants can read the claim routes and safety signals; developers can inspect authoring-time OpenTelemetry instrumentation, a plain-JSON dataset, and deterministic helpers. This demo does not require Azure, Application Insights, or a live model.

## Readiness and staging

- **Pre-stage:** Python 3.10+ and the repository checkout. Run from this module folder; no `config.json` is required for the offline path.
- **Pre-existing artifact:** `artifacts/scorecard.json` is a 12-case scorecard snapshot and may be stale. Do not call it a live result unless you have just rerun the evaluator.
- **Optional, not in the exemplar:** connect an exporter to Application Insights, run an explicit `--live` router, deploy an agent, or change the dataset/rules. The current evaluator defaults to the local deterministic router.
- **Synthetic only:** do not attach raw claim/customer data, identifiers, access tokens, or secrets to spans or test records.

## Exact navigation and assets

1. Open the local `modules\07-observability-evaluation-trust-safety` folder in the editor. Start at [`src/otel_setup.py`](src/otel_setup.py), then open [`eval/triage-eval-dataset.json`](eval/triage-eval-dataset.json), [`src/evaluator.py`](src/evaluator.py), and [`src/safety_checks.py`](src/safety_checks.py).
2. Run the command-line steps below from the module folder. The visible output is the terminal summary; this module does not promise a portal trace view.
3. Optional cloud context only: use the configured Application Insights resource in Azure portal to inspect telemetry if the exporter is already wired and spans have arrived. No live exporter is configured by this demo; an empty portal view is not evidence that the local evaluator failed.
4. Reference [`demo-runbook.md`](demo-runbook.md), [`lab.md`](lab.md), and [`docs/known-limitations.md`](../../docs/known-limitations.md) for optional live mode and verified telemetry/networking caveats.

## Context setting — 6 minutes, separate from the live demo

Use this segment to align the room on operational evidence before opening code or running commands. It is not counted in the 8-minute live exemplar below.

| Time | Slides | Context beat |
| --- | --- | --- |
| 0:00–2:00 | [1–4](slides.md) | Frame the shift from “can it answer?” to “can we operate and measure it?” Contrast trace (what happened), evaluation (did it meet expectation), and safety review (does it need intervention). Preview the trace points worth instrumenting. |
| 2:00–4:00 | [5–9](slides.md) | Explain provider, service naming, spans, and conditional export. Distinguish instrumentation in authored code from successful telemetry ingestion. Present the sanitized field notes as environment-specific verified observations, not tasks for learners to reproduce. |
| 4:00–6:00 | [10–17](slides.md) | Introduce the offline dataset and scorecard as a repeatable optimization loop. Preview citation, fraud-escalation, and protected-class checks; state that these are narrow, deterministic signals rather than full model evaluation or production safety controls. Transition the audience toward the capstone's operating controls. |

## Minute-by-minute live exemplar

| Time | Slide(s) | Instructor action and narration |
| --- | --- | --- |
| 0:00–1:00 | [1–2](slides.md) | Set the operating question: a successful-looking answer can still be unobservable, misrouted, or unsafe. Distinguish trace, evaluation, and safety review. |
| 1:00–2:00 | [3–6](slides.md) | Show `configure_otel`, `start_agent_run_span`, and `@instrument_tool_call` in `src/otel_setup.py`. Instrumentation is authored in the code path; the Azure Monitor exporter is optional. Warn against sensitive span attributes. |
| 2:00–4:00 | [11–12, 14](slides.md) | Open the dataset and run the offline evaluator. Read total/pass/fail/rate aloud, then explain that each case has a human-readable description and expected route. |
| 4:00–6:00 | [13–14](slides.md) | Run the three safety examples below. Ask the audience to interpret a fraud flag as human review, protected-class wording as a review flag, and missing citation as a citation check—not an automatic denial. |
| 6:00–7:00 | [8–9](slides.md) | State one field note: telemetry can remain empty because exporter/network ingestion is not end-to-end. Separate that from agent behavior and mention APIM token metrics require explicit metric emission. |
| 7:00–8:00 | [15–17](slides.md) | Choose the narrowest layer to improve, rerun the same dataset after changes, and transition to Module 08's gateway and operational controls. |

## Copy/paste synthetic inputs

**Run the deterministic offline evaluator**

```powershell
python .\src\evaluator.py --threshold 0.85
```

In the checked-in dataset at this reference point, the visible summary is **12 total, 12 passed, 0 failed, 100.00%**. This is an offline keyword router's score on these 12 cases—not a model quality measurement or a promise that changed data will score the same.

**Run the deterministic trust/safety checks**

```powershell
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('src').resolve())); import safety_checks as s; print('fraud:', s.check_fraud_signal_keywords('The claimant changed the story twice and submitted altered receipts.')); print('protected:', s.check_protected_class_language('Decline because the driver is elderly.')); print('citation missing:', s.requires_citation('The loss is excluded under the policy.')); print('citation present:', s.requires_citation('The loss is excluded under Clause HO-12.'))"
```

Expected results: `['altered_receipts', 'story_shift']`, `['age']`, `True`, `False`.

## Expected visible evidence and narration

- The evaluator prints `Mode: offline`, dataset path, case count, pass/fail, and pass rate. It writes no scorecard unless `--output` is supplied.
- Safety helpers return category labels or a Boolean; `requires_citation` returns true when a coverage-style assertion has no clause-like citation.
- `configure_otel()` can run without cloud export. The helper creates spans when OTel packages exist; without exporter configuration it does not promise that spans appear in Application Insights.
- Narrate: “The scorecard tests the specified route against this dataset. It does not evaluate policy correctness, fairness, or production risk by itself.”

## Intentional contrast and boundary

**Contrast:** tracing explains execution; evaluation compares outputs with expectations; deterministic safety checks identify patterns for review. Passing one does not imply passing the others.

**Boundary:** the built-in evaluator is a rule-based, offline keyword classifier, not a generative model evaluation or production claims decision. The safety helpers are deliberately narrow regex/keyword checks; they are not Azure AI Content Safety, fraud adjudication, or a complete protected-class detector. OTel export depends on packages, connection configuration, identity, and network ingestion. See [OpenTelemetry in Application Insights](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable), [Foundry evaluations](https://learn.microsoft.com/azure/foundry/how-to/evaluate-generative-ai-app), and [Azure AI Content Safety](https://learn.microsoft.com/azure/ai-services/content-safety/overview).

## Audience questions

- What does the trace tell you that the scorecard cannot?
- Can a case pass routing and still fail a safety check?
- Why should a coverage conclusion cite a clause?
- Which failure should block a release, and which should trigger human review?
- What sensitive attributes should never be added to telemetry?

## Troubleshooting and backup evidence

- **Command cannot find files:** confirm the current directory is `modules\07-observability-evaluation-trust-safety`; relative paths are intentional.
- **Pass rate differs:** read the dataset path in the output, inspect expected vs. actual routes, and remember this is the deterministic baseline. Do not modify a test case live to force a pass.
- **No Application Insights traces:** expected in this offline demo. Check whether an exporter was configured and whether network ingestion is allowed; correct RBAC alone is not sufficient.
- **Safety result differs:** compare the exact phrase with the patterns in `src/safety_checks.py`; the checks match specific terms and do not understand intent.
- **Backup evidence:** `tests/test_evaluator.py`, `tests/test_safety_checks.py`, and the checked-in scorecard snapshot provide offline references. Label the snapshot as historical until rerun. `verify.ps1` also runs the offline evaluator but writes `artifacts/scorecard.json`, so prefer the command above during this presentation.

## Security, governance, and reset

All examples are fictional. Never export raw prompts, policy numbers, claimant details, or credentials as span attributes; prefer low-cardinality operational metadata. Live mode is opt-in and requires an explicitly supplied router; do not invoke it during this exemplar. The command above creates no output artifact, and the safety check is read-only. No Azure resources are created or changed.

## Transition

“We can now inspect behavior, measure expected routes, and flag review signals. The final module places model traffic behind a governed gateway and turns operating assumptions into a verifiable contract.”
