#Requires -Version 7.0
<#
.SYNOPSIS
    Removes the shared public Foundry foundation resource group.

.DESCRIPTION
    Deletes ONLY the resource group created by deploy.ps1, and only after verifying it carries
    the `course=foundry-insurance-learning-series` tag this curriculum applies to everything it
    creates. Requires an explicit -Confirm (or typed 'yes' at the prompt); supports -WhatIf.

.PARAMETER ResourceGroupName
    Resource group to remove.

.EXAMPLE
    ./cleanup.ps1 -ResourceGroupName rg-foundry-learning -WhatIf
.EXAMPLE
    ./cleanup.ps1 -ResourceGroupName rg-foundry-learning -Confirm:$false  # non-interactive, use with care
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory = $true)][string]$ResourceGroupName
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI ('az') is required."
}

$rg = az group show --name $ResourceGroupName 2>$null | ConvertFrom-Json
if (-not $rg) {
    Write-Host "Resource group '$ResourceGroupName' does not exist — nothing to do." -ForegroundColor Yellow
    return
}

$courseTag = $rg.tags.course
if ($courseTag -ne 'foundry-insurance-learning-series') {
    throw "Refusing to delete '$ResourceGroupName': missing/mismatched 'course' tag (found '$courseTag'). This script only removes resource groups it recognizes as course-owned."
}

Write-Host "About to permanently delete resource group '$ResourceGroupName' (tag course=$courseTag)." -ForegroundColor Red
Write-Host "This removes the Foundry account, project, model deployment, and RBAC assignments created by deploy.ps1."

if ($PSCmdlet.ShouldProcess($ResourceGroupName, "Delete resource group")) {
    $typed = Read-Host "Type the resource group name to confirm deletion"
    if ($typed -ne $ResourceGroupName) {
        Write-Host "Confirmation text did not match. Aborting." -ForegroundColor Yellow
        return
    }
    az group delete --name $ResourceGroupName --yes --no-wait
    Write-Host "Deletion requested (async). Check 'az group show --name $ResourceGroupName' for status." -ForegroundColor Green
}
