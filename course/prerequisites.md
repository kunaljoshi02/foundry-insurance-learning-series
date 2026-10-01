# Prerequisites

## Accounts & access

- An Azure subscription you can create resources in (sandbox/dev subscription recommended —
  this curriculum never requires production access).
- Permission to create resource groups and assign RBAC roles at the resource-group scope (or ask
  your subscription owner to pre-create a resource group and grant you **Contributor** +
  **User Access Administrator**, or simply **Owner**, on it).
- A Microsoft Entra ID you can sign into the Azure AI Foundry portal with.

## Local tooling

| Tool | Why | Check |
| --- | --- | --- |
| [Azure CLI (`az`)](https://learn.microsoft.com/cli/azure/install-azure-cli) | Deploy the foundation Bicep, read-only preflight checks | `az version` |
| [PowerShell 7+ (`pwsh`)](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) | All `deploy.ps1`/`verify.ps1`/`cleanup.ps1` scripts | `pwsh -v` |
| [Python 3.10+](https://www.python.org/downloads/) | Module `src/` scripts and offline tests | `python --version` |
| [Bicep CLI](https://learn.microsoft.com/azure/azure-resource-manager/bicep/install) (bundled with recent `az`) | Building/validating Bicep templates offline | `az bicep version` |
| [Azure Developer CLI (`azd`)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd) | Module 4's hosted-agent deployment guidance (optional, described not executed by this repo) | `azd version` |

Run `foundation/scripts/preflight.ps1` any time — it performs **read-only** checks for all of the
above plus Azure login/subscription context and resource-provider registration.

## Recommended Python packages (per-module, install only what you need)

```powershell
pip install azure-identity azure-ai-projects azure-search-documents azure-monitor-opentelemetry
```

Each module's `src/` scripts import these defensively (try/except where reasonable) so missing
packages produce a clear error rather than a traceback, and none of the **tests** in this
repository require a live Azure SDK call.

## Knowledge prerequisites

- Comfortable navigating the Azure portal; no prior Foundry experience required for modules 1–3.
- Modules 4, 6, and 8 are more code/ops-heavy (Python, Bicep, APIM policy XML) — a developer or
  platform engineer should drive the hands-on parts, with business stakeholders following the
  portal-visible outcomes.
- Basic familiarity with REST/JSON is helpful for module 4 (A2A/JSON-RPC) and module 8 (APIM
  policies), but not required to follow the narrative.

## What you will NOT need

- No production data. All sample content is a synthetic 36-clause insurance policy-wording corpus
  (`shared/test-data/policy-wordings.json`).
- No pre-existing APIM instance to *start* the curriculum — module 8 introduces APIM concepts with
  policies you can apply to any test API, and the private-networking overlay is optional and
  disabled by default.
