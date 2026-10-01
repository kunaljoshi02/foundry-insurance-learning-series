#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json')
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Get-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }

    $python3 = Get-Command python3 -ErrorAction SilentlyContinue
    if ($python3) { return $python3.Source }

    throw 'Python was not found on PATH.'
}

function Get-AzCommand {
    $az = Get-Command az -ErrorAction SilentlyContinue
    if (-not $az) {
        throw 'Azure CLI (az) was not found on PATH.'
    }
    return $az.Source
}

Write-Section 'Validating configuration'
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'searchServiceName',
    'searchIndexName',
    'agentName',
    'searchConnectionName',
    'resourceGroupName',
    'subscriptionId'
)

if (-not $WhatIfPreference) {
    Write-Section 'Confirmation'
    if (-not (Confirm-Destructive -ResourceName $config.searchServiceName -Prompt "Type '$($config.searchServiceName)' to confirm cleanup")) {
        throw 'Cleanup cancelled by user.'
    }
}

$python = Get-PythonCommand
$az = Get-AzCommand
$connectScript = Join-Path $PSScriptRoot 'src\connect_search_to_agent.py'

Write-Section 'Inspecting Search service ownership tags'
$serviceJson = & $az search service show --subscription $config.subscriptionId --resource-group $config.resourceGroupName --name $config.searchServiceName --output json
if ($LASTEXITCODE -ne 0) {
    throw "Unable to read Search service '$($config.searchServiceName)'."
}
$service = $serviceJson | ConvertFrom-Json
Assert-CourseTag -Resource $service
if ($service.tags.module -ne '03-search-grounding-foundry-iq') {
    throw "Refusing to delete resource '$($service.name)': unexpected module tag '$($service.tags.module)'."
}

Write-Section 'Detaching grounding tool and removing the module Search connection'
$detachArgs = @($connectScript, '--config', $ConfigPath, '--action', 'detach', '--delete-connection')
if ($WhatIfPreference) { $detachArgs += '--what-if' }
if ($PSCmdlet.ShouldProcess($config.agentName, 'Detach Azure AI Search grounding from the agent')) {
    & $python @detachArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Detaching grounding failed with exit code $LASTEXITCODE."
    }
}

Write-Section 'Deleting the Search service (and its index)'
if ($PSCmdlet.ShouldProcess($config.searchServiceName, 'Delete module-owned Azure AI Search service')) {
    & $az search service delete --subscription $config.subscriptionId --resource-group $config.resourceGroupName --name $config.searchServiceName --yes
    if ($LASTEXITCODE -ne 0) {
        throw "Search service deletion failed with exit code $LASTEXITCODE."
    }
}

Write-Host "`nCleanup complete." -ForegroundColor Green
