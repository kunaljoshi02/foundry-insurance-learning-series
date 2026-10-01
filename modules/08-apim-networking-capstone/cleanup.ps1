#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [switch]$EnableEnterpriseOverlay,
    [string]$EnterpriseOverlayConfirmation,
    [switch]$ExecuteOperatorCommands,
    [string]$ResourceGroupName = '<resource-group-name>',
    [string]$CourseTag = 'foundry-insurance-learning-series',
    [string]$ModuleTag = '08-apim-networking-capstone'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Test-IsPlaceholder {
    param([string]$Value)
    return (-not [string]::IsNullOrWhiteSpace($Value)) -and ($Value.StartsWith('<') -and $Value.EndsWith('>'))
}

Write-Section 'Module 08 cleanup guidance'
Write-Host 'This module creates no cloud resources by default.' -ForegroundColor Green
Write-Host 'Cleanup is therefore informational unless you explicitly enabled and applied the enterprise overlay in your own environment.' -ForegroundColor Yellow

if (-not $EnableEnterpriseOverlay) {
    Write-Host ''
    Write-Host 'Enterprise overlay cleanup is OFF by default. Nothing to do.' -ForegroundColor Green
    Write-Host 'To review a private-networking teardown plan, re-run with -EnableEnterpriseOverlay and the typed confirmation string.' -ForegroundColor Yellow
    return
}

if ($EnterpriseOverlayConfirmation -ne 'yes-enable-enterprise-overlay') {
    throw "Enterprise overlay cleanup requested. Re-run with -EnterpriseOverlayConfirmation yes-enable-enterprise-overlay to unlock the plan."
}

Write-Section 'Enterprise overlay teardown plan'
Write-Host "Scoped resource group: $ResourceGroupName"
Write-Host "Expected tags: course=$CourseTag, module=$ModuleTag"
Write-Host ''
Write-Host 'Suggested review-first sequence:' -ForegroundColor Cyan
Write-Host "az resource list --resource-group `"$ResourceGroupName`" --tag course=$CourseTag --query ""[?tags.module=='$ModuleTag'].{name:name,type:type}"""
Write-Host "az group delete --name `"$ResourceGroupName`" --yes --no-wait"

if (-not $ExecuteOperatorCommands) {
    Write-Host ''
    Write-Host 'Preview only. Pass -ExecuteOperatorCommands to run your own teardown commands after review.' -ForegroundColor Yellow
    return
}

if (Test-IsPlaceholder -Value $ResourceGroupName) {
    throw 'Replace the placeholder ResourceGroupName before executing any operator cleanup command.'
}

$az = Get-Command az -ErrorAction SilentlyContinue
if (-not $az) {
    throw 'Azure CLI (az) is not installed. Re-run without -ExecuteOperatorCommands to keep this as a printed plan.'
}

if (-not (Confirm-Destructive -ResourceName 'yes-enable-enterprise-overlay' -Prompt 'Type yes-enable-enterprise-overlay to confirm enterprise overlay cleanup')) {
    throw 'Cleanup cancelled because the confirmation text did not match.'
}

if ($PSCmdlet.ShouldProcess($ResourceGroupName, 'Delete enterprise overlay resources in the specified resource group after tag review')) {
    & $az.Source resource list --resource-group $ResourceGroupName --tag "course=$CourseTag"
    & $az.Source group delete --name $ResourceGroupName --yes --no-wait
}
