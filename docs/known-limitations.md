# Known limitations and verified preview behavior

This curriculum teaches several capabilities that are **preview** or have **documented
runtime quirks** as of this writing. Where this repository asserts a specific behavior (rather
than linking you to "check current docs"), that assertion was **observed against a deployed
reference build** and is called out here so you can tell verified-but-possibly-time-bound
behavior apart from stable, general guidance. Always re-verify against the current
[Microsoft Learn Azure AI Foundry Agent Service docs](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
before presenting any of these as current-state facts to a customer — preview services change
quickly.

## 1. Prompt-agent `toolbox_reference` runtime incompatibility (modules 2–3)

Some prompt-agent definitions reference a toolbox by a `toolbox_reference` field whose expected
shape has changed across API versions. If an agent fails to resolve its attached toolbox at
runtime with a not-found/incompatible-reference error, first confirm the toolbox API version used
to create the agent matches the toolbox's own API version, and recreate the reference rather than
assuming the toolbox itself is broken. Module 2's `verify.ps1` checks for this symptom explicitly.

## 2. Hosted-agent A2A returns HTTP 200 with a JSON-RPC error (module 4)

**Verified behavior:** when a *hosted* agent (Agent Framework / containerized) is targeted as an
A2A (agent-to-agent) call destination, the Foundry service responds with **HTTP 200** but the
response **body** is a JSON-RPC error envelope with an error code such as `HostedAgentNotSupported`.
**HTTP 200 does not mean the call succeeded.** Always parse and check the JSON-RPC body, not just
the status code. Module 4 implements and unit-tests a detector for this envelope plus a controlled
fallback to the hosted agent's Responses-style endpoint.

- Use a **prompt agent** (not hosted) as the A2A target if you need to demonstrate native Foundry
  A2A without the fallback path.
- Reference: [Foundry Agent Service overview](https://learn.microsoft.com/azure/foundry/agents/overview) and [Hosted agents overview](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents). The HTTP 200/error-envelope observation is specific to this repository's reference build, not a general guarantee in those pages.

## 3. Managed Memory preview: networking and identity scope (module 5)

**Verified behavior:** the managed Memory preview does not support VNet-injected projects — it
currently requires a **public** project (which is exactly the shared foundation this curriculum
uses for modules 1–7). Memory is scoped to the **signed-in Entra identity**; when a client omits an
explicit user-scope header, Foundry derives the scope from the caller's resolved token identity. Do
not design a demo that assumes Memory works inside a private/VNet-injected project, and do not
store anything beyond synthetic preference data in it (see `modules/05-managed-memory-privacy/docs/privacy-notes.md`).

- Reference: [Create and use memory in Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/memory-usage).

## 4. On-Behalf-Of (OBO) requires an interactive signed-in user (module 6)

**Verified behavior:** the OBO/user-delegated token toolbox pattern only functions when the calling
identity is an **interactive, signed-in human user**. It fails predictably for application-only
(client-credentials / service-principal) identities, because there is no user token to exchange.
Module 6's `src/auth_context.py` encodes this rule and is unit-tested against both cases.

- Reference: [Microsoft identity platform — On-Behalf-Of flow](https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow).

## 5. Private/VNet-injected portals have no public network access (module 8 overlay)

If you enable the **optional, disabled-by-default** enterprise overlay (private networking /
VNet injection) in module 8, the Foundry portal and project endpoints become reachable only from
inside the VNet (or via Bastion/jump host/private DNS). This is expected, documented behavior for
private endpoints — it is not a bug. The default public foundation used throughout modules 1–7
deliberately avoids this so the curriculum stays portal-accessible for every learner.

- Reference: [Azure AI Foundry network isolation](https://learn.microsoft.com/azure/ai-foundry/how-to/configure-private-link) and [Azure Private Link overview](https://learn.microsoft.com/azure/private-link/private-link-overview).

## 6. APIM BYOM deployment-metadata probe (module 8)

**Verified behavior:** when Foundry validates a Bring-Your-Own-Model (BYOM) connection fronted by
Azure API Management, it issues `GET {target}/deployments/{model}` **without an `api-version`
query parameter** and expects an **ARM Cognitive Services deployment resource** shape in the
response — not an OpenAI-style object. Without an APIM policy that mocks this exact shape, every
subsequent call fails with a bare `NotFound`. Module 8 ships a sanitized, generic version of this
policy plus a fully offline unit test that validates the expected response contract.

- Reference: [API Management policy reference](https://learn.microsoft.com/azure/api-management/api-management-policies) and [Configure Azure AI Foundry Models connections](https://learn.microsoft.com/azure/ai-foundry/concepts/connections). The metadata probe and response shape are reference-build observations, not a general contract established by these pages.
