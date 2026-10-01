#Requires -Version 7.0
<#
.SYNOPSIS
    Deploys the shared public Foundry foundation (account + project + chat model + RBAC).

.DESCRIPTION
    Thin, idempotent wrapper around `az deployment group create` for foundation/bicep/main.bicep.
    Supports -WhatIf (via -DryRun, since Bicep deployments use `what-if`) and is safe to re-run:
    Bicep deployments are declarative/idempotent by nature. This script does NOT run automatically
    as part of repository setup — a human must invoke it explicitly with their own parameters.

.PARAMETER ResourceGroupName
    Target resource group (created if it does not exist, unless -DryRun).

.PARAMETER Location
    Azure region for the resource group and resources.

.PARAMETER ParametersFile
    Path to a .bicepparam file. Defaults to foundation/bicep/main.bicepparam (placeholders —
    copy it and fill in your own values first).

.PARAMETER DryRun
    When set, runs `az deployment group what-if` instead of `create`. No resources are changed.

.EXAMPLE
    ./deploy.ps1 -ResourceGroupName rg-foundry-learning -Location eastus2 -DryRun
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroupName,
    [Parameter(Mandatory = $true)][string]$Location,
    [string]$ParametersFile = (Join-Path $PSScriptRoot '..\bicep\main.bicepparam'),
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI ('az') is required. Run foundation/scripts/preflight.ps1 first."
}

$bicepFile = Join-Path $PSScriptRoot '..\bicep\main.bicep'
if (-not (Test-Path $bicepFile)) { throw "Bicep template not found: $bicepFile" }
if (-not (Test-Path $ParametersFile)) { throw "Parameters file not found: $ParametersFile" }

Write-Host "== Foundry foundation deploy ==" -ForegroundColor Cyan
Write-Host "Resource group : $ResourceGroupName"
Write-Host "Location       : $Location"
Write-Host "Template       : $bicepFile"
Write-Host "Parameters     : $ParametersFile"
Write-Host "Mode           : $($DryRun ? 'what-if (no changes)' : 'create')"

if (-not $DryRun -and -not $PSCmdlet.ShouldProcess($ResourceGroupName, "Create/update resource group and deploy foundation")) {
    Write-Host "Skipped (ShouldProcess declined)." -ForegroundColor Yellow
    return
}

# Idempotent: create-if-not-exists.
$rgExists = az group exists --name $ResourceGroupName | ConvertFrom-Json
if (-not $rgExists) {
    if ($DryRun) {
        Write-Host "[WhatIf] Would create resource group '$ResourceGroupName' in '$Location'." -ForegroundColor Yellow
    }
    else {
        az group create --name $ResourceGroupName --location $Location --tags course=foundry-insurance-learning-series owner=foundation | Out-Null
    }
}
else {
    Write-Host "Resource group '$ResourceGroupName' already exists — reusing." -ForegroundColor DarkGray
}

$deploymentName = "foundation-$(Get-Date -Format 'yyyyMMddHHmmss')"

if ($DryRun) {
    az deployment group what-if `
        --resource-group $ResourceGroupName `
        --name $deploymentName `
        --template-file $bicepFile `
        --parameters $ParametersFile
}
else {
    az deployment group create `
        --resource-group $ResourceGroupName `
        --name $deploymentName `
        --template-file $bicepFile `
        --parameters $ParametersFile `
        --output table
}

Write-Host "`nDone." -ForegroundColor Green
