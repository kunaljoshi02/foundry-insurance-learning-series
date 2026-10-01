# Module 06 — Instructor model demo: identity, least privilege, and OBO

**Performance length:** 6-minute slide context + 8-minute live exemplar · **Slides:** [slides 1–14](slides.md) · **Mode:** inspect prepared access; prove the rule offline

## Outcome and audience promise

Make the identity choice tangible in the underwriting-risk-summarizer story: routine service access belongs to managed identity, while a tool that must honor the underwriter's own authority needs an interactive user's delegated token. Learners should be able to predict the OBO precondition and explain why isolation and least privilege matter.

The business audience gets the “whose authority?” decision; developers/platform engineers see a deterministic classifier and the separate connection/toolbox pattern. This exemplar does not create RBAC assignments, connections, or live tokens.

## Readiness and staging

- **Pre-stage:** shared public Foundry project. If showing portal state, have project roles and the OBO-only connection/toolbox already configured by an authorized operator.
- **Live-ready boundary:** the module does not include a generic downstream profile service. A real OBO success requires a configured user-delegated connection, an endpoint that accepts that token/audience, and an interactive authenticated client. Do not imply the local classifier performs an exchange.
- **Optional actions, not demo defaults:** role assignment through the portal/Bicep, provisioning the remote-tool connection/toolbox, or testing a real delegated call. These change access or cloud state; use the [runbook](demo-runbook.md) only in an approved sandbox.
- **Have ready:** Python 3.10+ for the offline classifier. Azure CLI / SDK packages are only needed for optional setup or the read-only verification script.

## Exact navigation and assets

1. In `https://ai.azure.com`, select the prepared project. To inspect roles, open the project resource in Azure portal: **Access control (IAM) → Role assignments** and filter by the training principal. This is inspection only; do not add a role during the exemplar.
2. If prepared assets are exposed in the Foundry project's connection/toolbox view, identify the OBO connection's `UserEntraToken` auth type and the dedicated toolbox that references only that connection. Exact labels can differ; use the implementation as authority rather than assuming a universal portal label.
3. Local assets: [`src/auth_context.py`](src/auth_context.py) and [`tests/test_auth_context.py`](tests/test_auth_context.py) (offline rule), [`infra/rbac.bicep`](infra/rbac.bicep) plus the [shared role module](../../shared/bicep/rbac-assignment.bicep) (optional RBAC accelerator), and [`src/provision_obo_toolbox.py`](src/provision_obo_toolbox.py) (connection/toolbox lifecycle).

## Context setting — 6 minutes, separate from the live demo

Use this segment to establish the identity vocabulary and authorization decision before running the offline classifier. It is not counted in the 8-minute live exemplar below.

| Time | Slides | Context beat |
| --- | --- | --- |
| 0:00–2:00 | [1–4](slides.md) | Introduce the underwriting-risk-summarizer's authority-sensitive lookup. Distinguish Foundry account/project/hosted-agent managed identities from the signed-in human; ask whether each workflow should act as the platform or the person. |
| 2:00–4:00 | [5–8](slides.md) | Explain least privilege through the example roles and narrow scopes, then introduce OBO as delegated user authorization. Explain why the OBO-only connection and toolbox are isolated from shared managed-identity tools. |
| 4:00–6:00 | [9–14](slides.md) | Trace the two architecture paths and set the verified precondition: interactive user + delegated token + `User` principal. Preview the offline classifier and tell learners that it predicts the precondition; it does not obtain tokens, assign RBAC, or call a downstream endpoint. |

## Minute-by-minute live exemplar

| Time | Slide(s) | Instructor action and narration |
| --- | --- | --- |
| 0:00–1:00 | [1–4](slides.md) | Ask: “Should this lookup run as the platform or as the person?” Separate account/project/hosted-agent managed identities from the human caller. |
| 1:00–2:00 | [5–6](slides.md) | If ready, show the project's IAM role assignments for the training principal. Point to the narrowest useful scope and explain why `Azure AI Project Manager` is only for people editing project assets. Make no assignment changes. |
| 2:00–3:00 | [7–9](slides.md) | Show the pre-staged OBO connection/toolbox if present. Trace: interactive caller → delegated token → isolated connection → downstream authorization as the user. State that the course has no generic endpoint to invoke from this screen. |
| 3:00–5:00 | [10–11, 13](slides.md) | Run the two local classifier commands below from the module folder. Compare the JSON `will_succeed` value and reason. Explain that this is a pre-check, not a token request. |
| 5:00–6:00 | [8, 12](slides.md) | Contrast an isolated user-delegated toolbox with the shared managed-identity path. The failure boundary is intentional: no interactive user token means no OBO exchange. |
| 6:00–7:00 | [5–6, 10](slides.md) | Invite the room to choose the minimal role and scope for reading a grounding index. Explain optional resource-specific roles; omit unused roles rather than assigning all example roles. |
| 7:00–8:00 | [14](slides.md) | Recap the three-part predicate and transition to Module 07: instrument and evaluate the behavior rather than trusting an invisible tool call. |

## Copy/paste synthetic inputs

**Predict an interactive human user with a delegated token**

```powershell
python .\src\auth_context.py --interactive --has-user-token --principal-type User
```

Expected JSON: `"will_succeed": true`; reason says the interactive signed-in user and delegated token are present.

**Predict a background application identity**

```powershell
python .\src\auth_context.py --principal-type ServicePrincipal
```

Expected JSON: `"will_succeed": false`; reason says a service principal does not provide the required interactive delegated user token.

**Insurance prompt for a pre-provisioned client only**

```text
For a synthetic training scenario, check whether the signed-in underwriter may read their own authority profile before summarizing this hypothetical storm-damage claim. Do not return another user's profile, do not make an approval decision, and report an authorization failure without retrying as a shared service identity.
```

Only use that prompt if the downstream profile tool is intentionally pre-provisioned for the demo. No real person, account, policy, or claim identifiers.

## Expected visible evidence and narration

- The first local output reports `will_succeed: true`; the second reports `false` with the reason. Those outcomes are encoded in the classifier and covered by tests.
- If portal assets were pre-staged, visible evidence is a dedicated OBO connection and isolated toolbox, not a successful live exchange. If an authenticated live client is separately prepared, describe its result as environment-specific.
- Narrate: “RBAC on the agent identity cannot manufacture the human's delegated token. Isolation makes the missing-user-token failure local to the OBO path.”

## Intentional contrast and boundary

**Contrast:** managed identity is appropriate for non-interactive service-to-service access; OBO exists to honor the interactive user's downstream permissions. They are complementary, not interchangeable.

**Verified limitation:** OBO requires an interactive signed-in human user, a delegated user token, and a `User` principal. It should fail for application-only/service-principal or headless background execution even if the service identity has RBAC. Role names/scopes and project IAM views can vary with resource model; follow the current [Foundry RBAC Learn article](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-azure-ai-foundry), [Azure built-in roles](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles), and [OBO flow documentation](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow).

## Audience questions

- Which actions are service-scoped, and which must honor the user's own access?
- Why is a project manager role not a default learner role?
- What exact facts must be true before an OBO call can succeed?
- Why keep the OBO connection out of the shared managed-identity toolbox?

## Troubleshooting and backup evidence

- **Classifier says false for the first example:** check every flag, especially `--interactive`, `--has-user-token`, and `--principal-type User`; run `python -m unittest discover -s tests -p "test_*.py"` to check the local contract.
- **No connection/toolbox in the portal:** it was not pre-provisioned. Do not create one during the instructor performance; use the implementation and slide architecture as the backup.
- **Live OBO reports signed-in user required / no token:** this is the expected boundary for a non-interactive caller. Do not retry with a broader service identity or claim the classifier already tested the endpoint.
- **RBAC view is empty:** confirm the selected training principal and scope; Azure role assignments can take time to propagate. Use the role list in `infra/rbac.bicep` as reference, not proof of an assignment.
- **Backup evidence:** `src/auth_context.py` produces JSON without Azure connectivity; `tests/test_auth_context.py` covers interactive success and missing-token/non-interactive/service-principal failures. `verify.ps1` checks configured assignments and named OBO assets but is not a live token-exchange test.

## Security, governance, and reset

Use a disposable sandbox and synthetic profile data only. Never paste a real bearer token, client secret, user profile, or claim identifier into prompts or logs. Treat role assignments, connection creation, toolbox versioning, and cleanup as authorized operator actions—not classroom clicks. For reset, stop after the local classifier; do not remove roles or delete the OBO assets. No deployment or resource mutation is part of this exemplar.

## Transition

“We have separated service identity from user authority. Module 07 adds observability and repeatable evaluation so we can see what the system did and test whether it behaved acceptably.”
