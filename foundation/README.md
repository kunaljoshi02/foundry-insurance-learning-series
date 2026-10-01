# Foundation

The shared, **public** Microsoft Foundry base that every module in this curriculum builds on
additively. One Bicep template deploys:

- An Azure AI Foundry account (`Microsoft.CognitiveServices/accounts`, kind `AIServices`),
  `publicNetworkAccess = Enabled` (this is intentionally the public learning foundation — the
  private-networking variant is covered as an explicitly gated, disabled-by-default overlay in
  [`modules/08-apim-networking-capstone/enterprise-overlay/`](../modules/08-apim-networking-capstone/enterprise-overlay/)).
- One Foundry **project** under that account.
- A configurable **chat model deployment** (default `gpt-4o-mini`; override via parameters).
- Base RBAC: **Azure AI User** on the project for a learner/operator principal.

## Files

| File | Purpose |
| --- | --- |
| `bicep/main.bicep` | Self-contained template (account + project + model + RBAC + outputs) |
| `bicep/main.bicepparam` | Placeholder parameters — copy and fill in your own values |
| `scripts/preflight.ps1` | **Read-only** checks: az/azd/pwsh/python, login, subscription, provider registration, region/model sanity |
| `scripts/deploy.ps1` | Idempotent deploy wrapper with `-DryRun` (what-if) support |
| `scripts/cleanup.ps1` | Tag-gated, confirmation-required teardown of the foundation resource group |

## Usage (not executed by this repository)

```powershell
# 1. Read-only checks — safe to run anytime.
./foundation/scripts/preflight.ps1 -Location eastus2 -ChatModelName gpt-4o-mini

# 2. Copy and edit the parameters file with your own values (never commit real values).
Copy-Item foundation/bicep/main.bicepparam foundation/bicep/main.local.bicepparam

# 3. Preview changes (no resources are created or modified).
./foundation/scripts/deploy.ps1 -ResourceGroupName rg-foundry-learning -Location eastus2 `
    -ParametersFile foundation/bicep/main.local.bicepparam -DryRun

# 4. Deploy for real, when you're ready, in your own sandbox subscription.
./foundation/scripts/deploy.ps1 -ResourceGroupName rg-foundry-learning -Location eastus2 `
    -ParametersFile foundation/bicep/main.local.bicepparam

# 5. Tear down when done.
./foundation/scripts/cleanup.ps1 -ResourceGroupName rg-foundry-learning
```

> This repository's own automation and CI never run `az deployment`, `azd provision/deploy`, or
> any live Foundry call. All validation (see `tests/`) is offline: syntax, schema, and static
> checks only.

## Reference

- [Azure AI Foundry overview](https://learn.microsoft.com/azure/ai-foundry/what-is-azure-ai-foundry)
- [Create a Foundry resource (Bicep/ARM)](https://learn.microsoft.com/azure/ai-foundry/how-to/create-resource-template)
- [Model catalog and regions](https://learn.microsoft.com/azure/ai-foundry/concepts/models)
- [Azure AI Foundry RBAC built-in roles](https://learn.microsoft.com/azure/ai-foundry/concepts/rbac-azure-ai-foundry)
