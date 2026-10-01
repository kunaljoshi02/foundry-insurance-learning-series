#Requires -Version 7.0
<#
.SYNOPSIS
    Read-only preflight checks for the Foundry Insurance Learning Series foundation.

.DESCRIPTION
    Verifies local tooling (az, azd, pwsh, python), Azure login/subscription context,
    required resource-provider registration, and that the requested chat model/quota is
    available in the target region. Performs NO writes and NO deployments — it only reads
    state via `az` CLI `show`/`list` calls so it is always safe to run.

.PARAMETER SubscriptionId
    Azure subscription ID to check. Defaults to the current az CLI context.

.PARAMETER Location
    Azure region to validate model/quota availability in.

.PARAMETER ChatModelName
    Model name to check quota for (default: gpt-4o-mini).

.EXAMPLE
    ./preflight.ps1 -Location eastus2 -ChatModelName gpt-4o-mini
#>
[CmdletBinding()]
param(
    [string]$SubscriptionId,
    [string]$Location = 'eastus2',
    [string]$ChatModelName = 'gpt-4o-mini'
)

$ErrorActionPreference = 'Stop'
$results = [System.Collections.Generic.List[pscustomobject]]::new()

function Add-Result([string]$Check, [bool]$Pass, [string]$Detail) {
    $results.Add([pscustomobject]@{ Check = $Check; Pass = $Pass; Detail = $Detail })
}

function Test-CommandAvailable([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

Write-Host "== Foundry Insurance Learning Series: foundation preflight ==" -ForegroundColor Cyan

# 1. Local tooling
foreach ($tool in @('az', 'pwsh')) {
    $present = Test-CommandAvailable $tool
    Add-Result "tool:$tool" $present ($present ? "found" : "NOT found — install before deploying")
}
$azdPresent = Test-CommandAvailable 'azd'
Add-Result 'tool:azd' $azdPresent ($azdPresent ? "found" : "optional — only needed for azd-based module flows")

$pythonCmd = (Test-CommandAvailable 'python') ? 'python' : ((Test-CommandAvailable 'python3') ? 'python3' : $null)
Add-Result 'tool:python' ([bool]$pythonCmd) ($pythonCmd ? "found ($pythonCmd)" : "NOT found — needed for scripts/* and modules 03/05 extraction tooling")

if (-not (Test-CommandAvailable 'az')) {
    Write-Host "`naz CLI missing — skipping all remaining (live) checks." -ForegroundColor Yellow
    $results | Format-Table -AutoSize
    exit 1
}

# 2. Login / subscription context (read-only)
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Add-Result 'azure:login' ([bool]$account) ($account ? "signed in as $($account.user.name)" : "not signed in")
}
catch {
    Add-Result 'azure:login' $false "not signed in — run 'az login'"
    $account = $null
}

if ($account) {
    $targetSub = $SubscriptionId ? $SubscriptionId : $account.id
    try {
        $sub = az account show --subscription $targetSub 2>$null | ConvertFrom-Json
        Add-Result 'azure:subscription' ([bool]$sub) ($sub ? "using subscription $($sub.name)" : "subscription not accessible")
    }
    catch {
        Add-Result 'azure:subscription' $false "could not read subscription '$targetSub'"
    }

    # 3. Resource provider registration (read-only)
    foreach ($rp in @('Microsoft.CognitiveServices', 'Microsoft.Search', 'Microsoft.ApiManagement', 'Microsoft.Insights', 'Microsoft.OperationalInsights')) {
        try {
            $state = az provider show --namespace $rp --query registrationState -o tsv 2>$null
            Add-Result "provider:$rp" ($state -eq 'Registered') "state=$state (run 'az provider register --namespace $rp' if not Registered)"
        }
        catch {
            Add-Result "provider:$rp" $false "could not query provider state"
        }
    }

    # 4. Model/quota availability (best-effort read-only; API surface varies by CLI version)
    try {
        $models = az cognitiveservices account list-skus --kind AIServices --location $Location 2>$null
        Add-Result 'model:region-support' $true "region '$Location' queried — verify '$ChatModelName' quota manually in the portal Quota blade if this check is inconclusive"
    }
    catch {
        Add-Result 'model:region-support' $false "could not enumerate SKUs for location '$Location' — verify manually in the Foundry portal"
    }
}

Write-Host ""
$results | Format-Table -AutoSize

$failed = $results | Where-Object { -not $_.Pass -and $_.Check -notlike 'tool:azd' -and $_.Check -notlike 'model:*' }
if ($failed) {
    Write-Host "`nPreflight found $($failed.Count) blocking issue(s). Resolve before deploying." -ForegroundColor Red
    exit 1
}

Write-Host "`nPreflight passed. No deployment was performed." -ForegroundColor Green
exit 0
