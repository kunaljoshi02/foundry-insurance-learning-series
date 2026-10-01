#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true)]
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
    'chatModelDeploymentName',
    'searchServiceName',
    'searchIndexName',
    'agentName',
    'resourceGroupName',
    'location',
    'subscriptionId'
)

$python = Get-PythonCommand
$az = Get-AzCommand
$templatePath = Join-Path $PSScriptRoot 'infra\search.bicep'
$buildScript = Join-Path $PSScriptRoot 'src\build_search_index.py'
$connectScript = Join-Path $PSScriptRoot 'src\connect_search_to_agent.py'
$tagsJson = ($config.tags | ConvertTo-Json -Compress)
if ([string]::IsNullOrWhiteSpace($tagsJson) -or $tagsJson -eq 'null') {
    $tagsJson = '{"course":"foundry-insurance-learning-series","module":"03-search-grounding-foundry-iq"}'
}

Write-Section 'Ensuring Azure AI Search service'
$deploymentArgs = @(
    'deployment', 'group',
    ($WhatIfPreference ? 'what-if' : 'create'),
    '--subscription', $config.subscriptionId,
    '--resource-group', $config.resourceGroupName,
    '--template-file', $templatePath,
    '--parameters',
    "searchServiceName=$($config.searchServiceName)",
    "location=$($config.location)",
    "tags=$tagsJson"
)

if ($PSCmdlet.ShouldProcess($config.searchServiceName, 'Provision/update module Search service')) {
    & $az @deploymentArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Search service deployment step failed with exit code $LASTEXITCODE."
    }
}

Write-Section 'Building or refreshing the Search index'
$buildArgs = @($buildScript, '--config', $ConfigPath, '--action', 'ensure')
if ($WhatIfPreference) { $buildArgs += '--what-if' }
if ($PSCmdlet.ShouldProcess($config.searchIndexName, 'Create/update index and upload policy documents')) {
    & $python @buildArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Index build step failed with exit code $LASTEXITCODE."
    }
}

Write-Section 'Connecting Search to the agent'
$connectArgs = @($connectScript, '--config', $ConfigPath, '--action', 'ensure')
if ($WhatIfPreference) { $connectArgs += '--what-if' }
if ($PSCmdlet.ShouldProcess($config.agentName, 'Attach Azure AI Search grounding to the policy-coverage-advisor agent')) {
    & $python @connectArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Agent grounding step failed with exit code $LASTEXITCODE."
    }
}

Write-Host "`nDone." -ForegroundColor Green
