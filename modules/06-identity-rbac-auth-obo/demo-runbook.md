# Module 6 demo runbook — Identity, RBAC, auth & OBO

This runbook is **portal-first** and uses optional Bicep/PowerShell/Python helpers only as an
accelerator. It assumes the shared public foundation already exists.

## Demo goals

By the end of the demo, the audience should see:

1. a learner identity with least-privilege Foundry-related roles
2. an **isolated OBO toolbox + connection**
3. an interactive-user invocation path that succeeds
4. an application/service-principal path that fails predictably

## Prerequisites

- Shared [`../../foundation/`](../../foundation/) deployment is already in place
- You can open the Foundry project in the portal
- You have a learner/user object ID for RBAC assignment
- You have a downstream MCP or similar user-profile endpoint that accepts a delegated user token
- Optional local tools if you want the script path:
  - Azure CLI
  - PowerShell 7+
  - Python 3.10+
  - `azure-identity`
  - `azure-ai-projects`

## Part 1 - Set the story

Tell the room:

- "Our underwriting-risk-summarizer can use search, tools, and memory already."
- "Now we want one tool call to honor the **actual underwriter's permissions**."
- "That is why we isolate an OBO toolbox from the platform-managed-identity path."

## Part 2 - Review identities in the portal

1. Open the Foundry account and project from the shared foundation.
2. Show that the account and project have **system-assigned managed identities**.
3. If you have hosted agents from earlier modules, explain that hosted agents also run with a
   platform-managed identity for non-interactive service access.
4. Emphasize that none of those identities are the same as the human caller's interactive sign-in.

## Part 3 - Assign least-privilege roles

### Portal path

1. Open the Foundry project's **Access control (IAM)** blade.
2. Add role assignments for the learner's identity using only the roles needed for the demo:
   - **Azure AI User** at the project scope
   - **Azure AI Project Manager** only if the learner must edit project assets live
3. If your demo also needs a Search-backed tool or connected cognitive resource, assign:
   - **Search Index Data Reader** at the specific Search scope
   - **Cognitive Services User** only at the connected resource scope
4. Call out the rule: **broad scope last, narrow scope first**.

### Optional Bicep/script path

1. Copy `config.example.json` to `config.json`.
2. Fill in placeholders only with your own sandbox values.
3. Preview changes:

```powershell
.\deploy.ps1 -WhatIf
```

4. Apply when ready:

```powershell
.\deploy.ps1
```

5. Explain that `infra/rbac.bicep` loops over the configured roles and reuses the shared
   `../../shared/bicep/rbac-assignment.bicep` module.

## Part 4 - Configure the isolated OBO connection

### Portal concept

1. In the Foundry project, create a **remote MCP / user-delegated** style connection for the
   downstream profile/authority endpoint.
2. Use the **user token forwarding** / **UserEntraToken-style** option, not managed identity.
3. Provide the correct **audience/resource URI** required by that upstream endpoint.
4. Save the connection with a name dedicated to this module's OBO path.

### Why isolate it?

Use this talking point:

> "If the user token is missing, only the OBO path should fail. We do not want a missing delegated
> token to poison the shared managed-identity tools used by the rest of the insurance workflow."

## Part 5 - Create the isolated OBO toolbox

1. Create a toolbox that contains **only** the user-delegated connection (and any tightly related
   OBO-only tools).
2. Do **not** mix it into the shared managed-identity toolbox from other sessions.
3. Optionally use the module script, which creates or updates:
   - the OBO connection definition
   - the OBO toolbox version that references that connection

```powershell
python .\src\provision_obo_toolbox.py --config .\config.json --action ensure
```

4. If you want a preview without writes:

```powershell
python .\src\provision_obo_toolbox.py --config .\config.json --action ensure --what-if
```

## Part 6 - Worked success example: interactive signed-in user

Use the portal or another end-user-authenticated client.

### What to do

1. Sign in interactively as a human user.
2. Invoke the underwriting-risk-summarizer scenario that uses the OBO-only tool path.
3. Ask it to perform a profile / authority / user-context check before returning its recommendation.

### What to expect

- the request reaches the isolated OBO toolbox
- the downstream service sees the **user's permissions**
- the tool call succeeds if that user is allowed to access the target data
- the result is explained as user-scoped, not service-scoped

## Part 7 - Worked failure example: application identity

Now contrast with a non-interactive path.

### What to do

1. Attempt the same OBO-dependent call from a service-principal or other application-only path.
2. Do **not** supply an interactive user session or delegated user token.

### What to expect

- the request fails predictably
- expected error style:
  - **signed-in user required**
  - **no user token available for on-behalf-of exchange**
  - equivalent wording that indicates the delegated-user precondition was not met

### Teaching point

This is the correct behavior. Nothing is "broken" — the identity model is preventing a user-scoped
tool from running without an actual signed-in user.

## Part 8 - Offline predictor demo

Before any live call, show the offline classifier:

```powershell
python .\src\auth_context.py --interactive --has-user-token --principal-type User
python .\src\auth_context.py --principal-type ServicePrincipal
```

Expected result:

- the interactive user case predicts **success**
- the service-principal case predicts **failure** with a reason explaining the missing user context

## Part 9 - Read-only verification

Run:

```powershell
.\verify.ps1
```

Use the output to show:

- which RBAC assignments are present for this module's configured scopes
- that the OBO connection exists
- that the isolated OBO toolbox exists
- that verification does **not** attempt any live token exchange

## Q&A prompts

- When should I prefer managed identity?
- When do I need OBO instead?
- Why not put both paths in one toolbox?
- What fails first when OBO is misapplied?

## Wrap-up

Close with:

- managed identity is the right default for **automation**
- OBO is the right choice for **user-scoped authorization**
- the reliable pre-check is: **interactive user + delegated user token + user principal**
