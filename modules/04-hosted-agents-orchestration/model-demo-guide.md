# Module 04 — Instructor model + live demo guide

**Run time:** 12–17 minutes total: a separate 5–7-minute slide-linked context segment plus a distinct 7–10-minute live exemplar.

**Purpose:** show why an insurance workflow may split intake/routing from specialist coverage reasoning, then teach the protocol boundary that HTTP success is not JSON-RPC success. This is a short instructor context and exemplar, not a deployment manual; the [demo runbook](demo-runbook.md) has the learner-run deployment sequence.

## Outcome and audience promise

Learners can distinguish a portal-authored prompt agent from a Python hosted agent, explain the triage/adjudicator separation, and state the tested fallback rule: inspect the JSON-RPC body; fall back to hosted Responses only for `HostedAgentNotSupported`. The repository's runnable implementation is an offline teaching package, not the hosted service itself.

## Readiness and assets

- Complete Modules 01–03 for storyline context. For this short demo, Python's standard library is sufficient; the offline test is `python -m unittest discover -s tests -p "test_*.py" -v` from this module directory.
- Open the [sequence and limitation](README.md#architecture), [`a2a_client.py`](src/triage_agent/a2a_client.py), [`orchestrator.py`](src/triage_agent/orchestrator.py), [`respond.py`](src/adjudicator_stub/respond.py), and [`test_a2a_fallback.py`](tests/test_a2a_fallback.py).
- The live Azure deployment is optional and preprovisioned only if the instructor has personally deployed it. `deploy.ps1` validates config and prints `azd` commands; it does **not** invoke `az`/`azd`. The runbook's provision/deploy commands are learner-run in their own hosted-agent projects.
- If both agents are already deployed, open `https://ai.azure.com`, select the configured project, and verify the names `claims-intake-triage-agent` and `coverage-settlement-adjudicator` in the project's hosted-agent/deployment experience. Portal labels can vary; do not invent a deeper click path. The offline test is the reliable fallback evidence.

## Separate slide-linked context segment — 5–7 minutes

Deliver this framing **before** the live test or optional portal visit. This context segment is additional to the minute-by-minute live exemplar; it gives the audience the protocol and role model needed to interpret the demo.

| Context time | Slides | Context to set |
| --- | --- | --- |
| 0:00–1:30 | 1–3 | Situate Module 04 after prompt agents, Skills, and Search grounding. Contrast portal-authored prompt agents with Python/Agent Framework hosted agents without implying that this repository deploys them. |
| 1:30–3:00 | 4–6 | Introduce the triage orchestrator and adjudicator specialist. Describe separation of routing from specialist review as a design boundary, not a correctness or fairness guarantee. |
| 3:00–5:00 | 7–10 | Teach JSON-RPC `message/send`: HTTP status is transport-level; the JSON-RPC body carries application-level result/error. State the verified HostedAgentNotSupported limitation and the narrow Responses fallback; unrelated errors propagate. |
| 5:00–7:00 (optional) | 11–16 | Preview the offline tests and distinguish them from a deployed hosted runtime. Set expectations for a synthetic FNOL walkthrough and transition to Module 05's memory/privacy topic. |

**Bridge into the live demo:** “Now that we know the two roles and the body-level success contract, let's prove the fallback rule with the offline test before discussing any preprovisioned deployment.”

## Live exemplar — separate 7–10 minutes, minute by minute

| Live-demo time | Instructor action | Narration and visible evidence |
| --- | --- | --- |
| 0:00–1:00 | Show Slides 3–6 and the sequence diagram. | “Triage extracts/routes; the adjudicator owns specialist rationale. Separation makes routing and approval boundaries easier to test; it does not itself guarantee fairness or correctness.” |
| 1:00–2:00 | Show the two agent names in the project only if these deployments were already provisioned. | These are hosted assets, not created by this demo. If absent, say so plainly; use the offline implementation instead of starting an unplanned deployment. |
| 2:00–4:00 | Open `tests/test_a2a_fallback.py`; run the offline unittest command. | The tests inject a synthetic JSON-RPC response through a fake transport. They prove success does not fallback, the named hosted-agent error does, and an unrelated `Unauthorized` error propagates. They do not call Azure or prove a current live service response. |
| 4:00–5:00 | Show the synthetic response envelope below and the detection/fallback code in `a2a_client.py`. | Point to HTTP 200 as transport status and `error.data.code` as application/protocol failure. In the verified service limitation, a hosted A2A target can return HTTP 200 with `HostedAgentNotSupported`; inspect the body. |
| 5:00–7:00 | If already deployed and approved, submit the FNOL below to the triage hosted agent and inspect the returned route/agent result. Otherwise, walk the stub and expected routing in code. | The short local stub returns `auto-adjudicate`, `COVERED`, and `$7,800 after deductible and trace-and-access review` for the washing-machine example. This value is hard-coded teaching output, not a calculation, policy determination, or guaranteed live-agent result. |
| 7:00–8:00 | Show Slides 9–12 and name the negative-path rule; show the preprovisioned hosted agents if available. | Fallback is only for this verified limitation. Do not retry all errors; do not treat any HTTP 200 as success. Avoid exposing real request/claim content in logs. |
| 8:00–10:00 | Close with Slides 15–16 and audience questions. | Module 05 adds managed Memory and its identity/privacy constraints; today's agents do not establish memory or customer identity. |

### Paste-ready synthetic FNOL

```json
{
  "policy_number": "HOME-1001",
  "fnol_narrative": "A sudden washing machine hose failure caused water damage in the kitchen. Estimated damage is USD 8,200 plus USD 1,400 to locate and expose the leak. No injuries were reported and the loss was reported the same day."
}
```

### Synthetic protocol evidence

The unit test uses an injected response shaped like this (the sample's fake transport supplies the JSON body; it is not an actual portal transcript):

```json
{
  "jsonrpc": "2.0",
  "id": "synthetic-request-id",
  "error": {
    "code": -32099,
    "data": {
      "code": "HostedAgentNotSupported",
      "detail": "Use a prompt agent as the A2A target."
    }
  }
}
```

If this condition is detected, the implementation derives the hosted Responses endpoint and invokes the fallback callback. A normal JSON-RPC `result` stays on A2A; unrelated errors such as `Unauthorized` raise `A2AProtocolError` and are not hidden by fallback.

## Contrast and audience questions

**Intentional contrast:** transport-level HTTP 200 versus the JSON-RPC body's application-level error. Ask:

- What is the success signal at each layer?
- Why should `Unauthorized` not be retried as a protocol fallback?
- Which claims belong in a route label, and which require a human claims handler?

## Troubleshooting and backup evidence

- **Hosted deployments do not appear:** check that the project endpoint and signed-in identity are correct; only demonstrate preprovisioned deployments. The module script prints commands and does not create agents. Backup: run the offline unittest and show the agent names in the README architecture.
- **Offline tests fail:** from this module folder use the exact unittest command above; inspect the failing assertion and distinguish expected fallback from normal success/unrelated error. Backup: show the test cases and explain expected outcomes; do not claim they passed if they did not.
- **No live A2A trace or hosted Responses endpoint:** this module's offline fake transport does not produce live traces/endpoints. Backup: use the synthetic envelope and code path. Do not imply a portal log or live HTTP exchange exists.
- **Live call returns an unexpected error:** inspect/log safe protocol metadata and request ID, not claim narrative; propagate errors other than the verified `HostedAgentNotSupported` condition. Consult current [A2A Learn guidance](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent).

## Security, governance, transition, reset

Use the synthetic FNOL only. Never screen-share real claimant text, names, policy identifiers, claim documents, access tokens, or raw payload logs. The offline stub has keyword routing and a hard-coded settlement example; it is not an adjudication model and must not be used for real claims. Fraud/injury flags are routing examples, not findings of fraud or liability. Require licensed/human review for coverage, settlement, and sensitive cases.

**Transition:** Module 05 introduces managed Memory; verify its identity scope and public-project restriction in [known limitations](../../docs/known-limitations.md) before designing a demo.

**Reset:** no Azure resources are created by the short offline walkthrough. The unit test leaves no persistent state. If this class separately deployed Module 04, cleanup is a distinct destructive action: use only the explicitly module-specific `azdEnvironmentName`; `cleanup.ps1 -WhatIf` prints the plan, and actual `azd down --force --purge` requires `-Confirm` plus typed environment confirmation. Never select an unrelated environment.

**References:** [Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) · [Agent Framework hosting](https://learn.microsoft.com/en-us/agent-framework/get-started/hosting) · [Foundry A2A tool](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/agent-to-agent)
