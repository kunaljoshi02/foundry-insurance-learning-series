# Glossary

**Agent (Foundry)** — A configured combination of a model, instructions, and optionally tools/
Skills/memory that can run threads and produce responses. See *prompt agent* and *hosted agent*.

**Agent Framework** — Microsoft's open-source framework for building code-first, containerized
("hosted") agents, deployable via `azd`.

**A2A (Agent-to-Agent)** — A protocol/pattern for one agent to call another agent as a tool/peer,
typically over a JSON-RPC envelope. See `docs/known-limitations.md` §2 for the `HostedAgentNotSupported`
gotcha.

**AIServices account** — The `Microsoft.CognitiveServices/accounts` resource (kind `AIServices`)
that hosts one or more Foundry projects and model deployments.

**BYOM (Bring Your Own Model)** — Fronting a model connection through your own gateway (e.g., APIM)
instead of calling the Foundry-hosted model endpoint directly.

**Content Safety** — Azure AI service/category of checks for harmful content categories (hate,
violence, self-harm, sexual) that can be layered onto agent inputs/outputs.

**Foundry IQ** — The general pattern of retrieval-augmented grounding orchestrated by the agent
runtime (search index + agent tool), as opposed to grounding implemented entirely in application
code. Treated conceptually in module 3; always confirm current product-surface specifics against
Microsoft Learn.

**Hosted agent** — An Agent Framework agent deployed as a running service (container), as opposed
to a *prompt agent* defined declaratively in the portal/API.

**Managed Memory** — A Foundry preview feature providing durable, cross-conversation recall of
user preferences/facts, scoped to a signed-in Entra identity.

**OBO (On-Behalf-Of)** — An OAuth2 flow where a service exchanges an incoming user token for a new
token to call a downstream resource *as that user*, preserving the user's own permissions rather
than using the service's own identity.

**OTel (OpenTelemetry)** — A vendor-neutral observability standard (traces, metrics, logs) used
here to instrument agent runs and tool calls, exported to Azure Monitor/Application Insights.

**Project (Foundry)** — A child resource of an AIServices account; the unit learners work in via
the Foundry portal (agents, threads, connections live here).

**Prompt agent** — A declaratively defined agent (instructions + model + optional tools/toolbox)
created via the Foundry portal or API, without custom hosted code.

**RBAC (Role-Based Access Control)** — Azure's built-in authorization model; this curriculum uses
least-privilege built-in roles (e.g., *Azure AI User*) rather than broad roles like *Owner*.

**Skill (Foundry)** — A reusable, versioned instruction/behavior snippet (`SKILL.md`) that can be
attached to one or more agents via a toolbox.

**Toolbox** — A named, reusable bundle of tools and Skills that one or more agents reference.

**VNet injection / private networking** — Deploying Foundry resources with public network access
disabled and connectivity routed through a virtual network and private endpoints. Covered as an
explicitly gated, disabled-by-default overlay in module 8.
