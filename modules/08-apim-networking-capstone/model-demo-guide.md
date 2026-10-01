# Module 08 — Instructor model demo: APIM, networking, and operate capstone

**Performance length:** 6-minute slide context + 8-minute live exemplar · **Slides:** [slides 1–16](slides.md) · **Mode:** local contract first; portal inspection is optional

## Outcome and audience promise

Make the APIM/BYOM contract memorable and testable: Foundry's validated deployment metadata probe is `GET /deployments/{model}` without `api-version`, and the response must resemble an ARM Cognitive Services deployment resource. Then show how an operator keeps the public learning foundation separate from an optional, explicitly gated private-networking overlay.

Business stakeholders see why a “working chat endpoint” is not the whole integration contract. Platform engineers see the sanitized policies and an offline HTTP test. No live APIM, Foundry, or networking change is required.

## Readiness and staging

- **Pre-stage:** PowerShell 7+ and Python 3.x. The default demo uses a local mock server bound to `127.0.0.1`; no Azure login or `config.json` is needed for `verify.ps1`'s local path.
- **Optional portal view:** if an APIM test service/API is already available, inspect it only. Do not apply policies or enable the enterprise overlay as part of this lesson.
- **Explicitly not part of default path:** `deploy.ps1` applies policies only when both `-ApplyPolicies` and `-ExecuteOperatorCommands` are supplied; the overlay is disabled by default and requires a separate explicit switch/confirmation even to print its plan.
- **Safety boundary:** policy XML contains placeholders. Never apply it unchanged to an API or send real credentials, tokens, or customer traffic through the mock.

## Exact navigation and assets

1. In the repository, open [`infra/apim/foundry-api-policy.xml`](infra/apim/foundry-api-policy.xml) and [`infra/apim/get-deployment-operation-policy.xml`](infra/apim/get-deployment-operation-policy.xml). Then open [`src/mock_deployment_probe_server.py`](src/mock_deployment_probe_server.py) and [`tests/test_deployment_probe_contract.py`](tests/test_deployment_probe_contract.py).
2. **Optional, only when a test APIM service and API are already pre-staged and authorized for inspection:** in Azure portal, navigate **API Management services → [pre-staged test service] → APIs → [pre-staged test API] → Design**. If that API already contains a `GET /deployments/{deploymentName}` operation and the portal presents its policy editor, inspect the existing operation policy and API-level policy without editing or saving. If these resources, operation, or controls are absent, skip portal inspection; do not create them or infer that the local mock is deployed to APIM.
3. Run the local contract check below from `modules\08-apim-networking-capstone`. The local check does not connect to the APIM portal or resource.
4. Optional references: [`docs/operate-checklist.md`](docs/operate-checklist.md), [`infra/enterprise-overlay/private-networking.bicep`](infra/enterprise-overlay/private-networking.bicep), and [known limitations](../../docs/known-limitations.md#5-privatevnet-injected-portals-have-no-public-network-access-module-8-overlay).

## Context setting — 6 minutes, separate from the live demo

Use this segment to establish the gateway and networking concepts before the local contract test. It is not counted in the 8-minute live exemplar below.

| Time | Slides | Context beat |
| --- | --- | --- |
| 0:00–2:00 | [1–4](slides.md) | Recap the course journey and frame the operator question: how do we govern model ingress without changing the public training foundation? Introduce APIM as a possible policy boundary for BYOM traffic, not a requirement for the offline lab. |
| 2:00–4:00 | [5–9](slides.md) | Trace the sample policy chain and explain the mandatory probe contract documented by this reference build: `GET /deployments/{model}`, no `api-version`, ARM-like deployment metadata. Keep this as a verified, time-bound integration observation, not a guarantee for every API surface or future version. |
| 4:00–6:00 | [10–16](slides.md) | Preview the local mock/test as the lesson's verifiable artifact. Contrast the public foundation with the separate, optional overlay; explain that private access depends on network and DNS reachability and must not be enabled live. Close context by teeing up the 8-minute contract and operating demo. |

## Minute-by-minute live exemplar

| Time | Slide(s) | Instructor action and narration |
| --- | --- | --- |
| 0:00–1:00 | [1–4](slides.md) | Frame the capstone: APIM can govern ingress, while the gateway becomes part of the BYOM contract—not just a pass-through. |
| 1:00–2:00 | [5–6](slides.md) | Open the API policy. Identify JWT validation, token limiting, explicit token metric emission, URI rewrite, and APIM managed identity to the backend. Explain that the placeholders require operator-specific values before any real use. |
| 2:00–3:00 | [7–9](slides.md) | Open the deployment-operation policy. State the exact hidden probe and expected response shape. Contrast the ARM-shaped deployment resource with an OpenAI-style chat/deployment object. |
| 3:00–5:00 | [10](slides.md) | Run `.\verify.ps1 -ModelName billing-claims-mini`. Point out that the script starts the local mock, issues a GET without a query string, checks the ARM fields, and stops the mock. |
| 5:00–6:00 | [11, 14](slides.md) | Open the operate checklist. Ask who owns tags, quota/cost review, verification, and teardown. Do not run the cross-module sweep: it can invoke module-specific verifications that need separate configuration or cloud access. |
| 6:00–7:00 | [12–13](slides.md) | Show the overlay Bicep file only. Explain it is separate from the shared foundation, disabled by default, and private portal access would require network/DNS reachability. Do not enable it. |
| 7:00–8:00 | [15–16](slides.md) | Recap modules 01–08, then ask what other “hidden contract” deserves a local test. Close the course with safe repeatability rather than more infrastructure. |

## Copy/paste synthetic inputs

**Exercise the contract with a fictional deployment name**

```powershell
.\verify.ps1 -ModelName billing-claims-mini
```

The equivalent request shape under test is:

```http
GET /deployments/billing-claims-mini
```

There is deliberately **no** `?api-version=...` query parameter.

**Inspect the response shape from the local mock**

```powershell
python .\src\mock_deployment_probe_server.py --port 8000 --model-name billing-claims-mini
```

In a second terminal, request `http://127.0.0.1:8000/deployments/billing-claims-mini`, then stop the server with `Ctrl+C`. The response should include `id`, `name`, `type: Microsoft.CognitiveServices/accounts/deployments`, `sku`, `properties.model` (format/name/version), and `properties.provisioningState: Succeeded`. Use `verify.ps1` for the complete assertion and automatic server cleanup.

## Expected visible evidence and narration

- `verify.ps1` prints that the probe contract was validated for `billing-claims-mini`. It verifies the returned resource type, IDs/model names, model format/version, and provisioning state. The implementation rejects `api-version` on this probe.
- The response is synthesized by the local mock. It proves the repository's contract test, not that a real APIM instance or Foundry BYOM connection is configured.
- Narrate: “If the gateway handles chat but omits this metadata probe, connection validation can still fail. Contract tests let us catch that before a live integration.”
- The policy file is an example template, not a deployable tenant-specific policy. The policy's token-limit behavior does not by itself imply model token telemetry; the sample explicitly includes a separate metric policy.

## Intentional contrast and boundary

**Contrast:** the public course foundation stays the default. The private-networking overlay is optional, separate, and disabled by default; a private endpoint changes where portal and project endpoints are reachable, so learners need the network path and private DNS—not just the resource.

**Verified limitation:** the reference build reports the deployment probe as `GET {target}/deployments/{model}` with no `api-version`, requiring an ARM Cognitive Services deployment shape. Treat this as a verified, time-bound behavior and recheck [Foundry connection documentation](https://learn.microsoft.com/azure/ai-foundry/how-to/connections-add) before customer guidance. For APIM policy semantics, see [APIM policies](https://learn.microsoft.com/azure/api-management/api-management-policies), [Entra token validation](https://learn.microsoft.com/azure/api-management/validate-azure-ad-token-policy), [LLM token limit](https://learn.microsoft.com/azure/api-management/llm-token-limit-policy), and [managed identity authentication](https://learn.microsoft.com/azure/api-management/authentication-managed-identity-policy).

## Audience questions

- Why does successful chat forwarding not prove a BYOM connection is valid?
- Which part of the response makes the probe ARM-shaped?
- Which APIM identity authenticates to the backend in the sample policy?
- What changes when private networking is enabled, and how will operators still reach the portal?
- Which controls are demonstrated by local tests versus only reviewed in configuration?

## Troubleshooting and backup evidence

- **Python or PowerShell unavailable:** use the policy and test files as static evidence; do not claim the mock ran. PowerShell verification requires PowerShell 7+.
- **Port/startup issue:** use `verify.ps1`, which selects an available loopback port and waits for `/healthz`; ensure local loopback connections are permitted.
- **Probe returns 400:** the local mock rejects `api-version` by design. Remove the query parameter for the deployment metadata request.
- **Probe returns 404:** check the exact fictional model name and `/deployments/{model}` path. The mock only serves the configured model name.
- **Missing ARM fields:** inspect `build_deployment_metadata_response()` and the contract tests; do not substitute an OpenAI-style response object.
- **Backup evidence:** `tests/test_deployment_probe_contract.py` validates both response shape and HTTP behavior; the operation policy lists the required shape. The checked-in tests are preferable to a live APIM experiment during class.

## Security, governance, and reset

Use only loopback and fictional model names. Do not send credentials or real claims to the mock, and do not publish the sanitized template as a ready-to-use policy: replace tenant, backend, workload, and deployment placeholders only in a separately reviewed sandbox. Keep the enterprise overlay off. `verify.ps1` stops its child process in a `finally` block; if you launched the mock manually, stop that specific terminal process with `Ctrl+C`. Do not run policy application flags or networking deployment commands during the demo.

## Transition / course close

There is no next lesson. Close by asking each team to name one ownership, verification, or cost-control practice they will carry into solution delivery.
