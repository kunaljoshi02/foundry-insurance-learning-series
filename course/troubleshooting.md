# Troubleshooting

## Foundation / deployment

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `az deployment group create` fails with a quota/capacity error on the chat model | Region lacks quota for the requested model/SKU/capacity | Lower `chatModelCapacity` in `main.bicepparam`, or pick a different `location`/`chatModelName` combination supported by your subscription — see [model availability](https://learn.microsoft.com/azure/ai-foundry/concepts/models) |
| `preflight.ps1` reports a resource provider not registered | First use of that provider in the subscription | `az provider register --namespace Microsoft.CognitiveServices` (etc.) and re-run preflight |
| RBAC assignment step is skipped | `principalId` left empty in parameters | Fill in your own Entra object ID (`az ad signed-in-user show --query id`) |

## Module 1–3 (prompt agents / tools / grounding)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Agent can't find its toolbox | API-version mismatch between agent and toolbox creation calls | See `docs/known-limitations.md` §1 (`toolbox_reference` incompatibility) — recreate the reference |
| Grounded answers don't cite clauses | Search tool not attached, or index not populated | Re-run module 3's `deploy.ps1`, then `verify.ps1` to confirm document count > 0 |

## Module 4 (hosted agents / A2A)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A2A call "succeeds" (HTTP 200) but adjudication never happens | Hosted-agent A2A target returns a JSON-RPC `HostedAgentNotSupported` envelope, not a failed HTTP status | This is expected — see `docs/known-limitations.md` §2; confirm `src/triage_agent/a2a_client.py`'s fallback path is reached |
| Unit tests fail with import errors | Running from the wrong working directory | `cd modules/04-hosted-agents-orchestration` then `python -m unittest discover -s tests` |

## Module 5 (Memory)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Memory doesn't recall preferences in a new conversation | Project is VNet-injected, or explicit user-scope header mismatch | Memory preview requires a **public** project (the shared foundation) — see `docs/known-limitations.md` §3 |
| `verify.ps1` can't find the memory store | Wrong `agentName`/`memoryStoreName` in `config.json` | Confirm names match what `deploy.ps1` created |

## Module 6 (identity / RBAC / OBO)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| OBO tool call fails for a service-principal-driven test | Expected — OBO requires an interactive signed-in user | See `docs/known-limitations.md` §4 and `src/auth_context.py`'s `predict_obo_outcome` |
| RBAC assignment fails with `AuthorizationFailed` | Your own identity lacks `User Access Administrator` (or Owner) at the scope | Ask your subscription/resource-group owner to grant it, or have them run `infra/rbac.bicep` for you |

## Module 7 (observability / evaluation)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| App Insights shows zero rows despite agents running | Public ingestion disabled, or private-link-only ingestion endpoint | See the sanitized field notes in this module's `README.md` "verified field notes" box |
| Evaluator harness reports failures after editing the dataset | A new case's `expected.route` doesn't match the rule-based stub router's keywords | Either adjust the stub router logic in `src/evaluator.py` or the case's expected route — both are valid depending on what you're testing |

## Module 8 (APIM / capstone)

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| BYOM connection fails with a bare `NotFound` | Missing/incorrect deployment-metadata probe policy | See `docs/known-limitations.md` §6; apply `infra/apim/get-deployment-operation-policy.xml` |
| `-RunAllModuleVerifications` reports a module as failed | That module's own prerequisites (e.g., its resources) aren't deployed in your sandbox | Expected if you haven't deployed every module — the capstone check is best-effort and continues past failures |
| Enterprise overlay accidentally referenced | A script or template imports `infra/enterprise-overlay/` outside the gated switch | This should never happen by design — file an issue; the overlay must only ever be opt-in |

## General

- Run `tests/run-all-validation.ps1` — it catches syntax errors, bad JSON/YAML, and accidental
  secrets/tenant-specific strings before you spend time debugging a live resource.
- Re-check `docs/known-limitations.md` first — several "bugs" in this space are actually
  documented, expected preview behavior.
