[CmdletBinding()]
param(
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

$configPath = Join-Path $PSScriptRoot 'config.json'
$config = Get-ModuleConfig -ConfigPath $configPath -RequiredKeys @(
    'foundryEndpoint',
    'azdEnvironmentName',
    'triageAgentName',
    'adjudicatorAgentName'
)

Write-Section 'Module 04 deployment guidance'
Write-Host 'This script never calls az or azd for you. It validates config.json, then prints the exact'
Write-Host 'commands a learner should run from their own hosted-agent project folders.' -ForegroundColor Yellow

$adjudicatorCommands = @(
    '# In your adjudicator hosted-agent folder',
    "azd env new $($config.azdEnvironmentName)-adj",
    "azd env set FOUNDRY_PROJECT_ENDPOINT $($config.foundryEndpoint)",
    "azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <chat-model-deployment>",
    'azd provision',
    'azd deploy'
)

$triageCommands = @(
    '# After the adjudicator is deployed and you have its A2A endpoint',
    "azd env new $($config.azdEnvironmentName)-triage",
    "azd env set FOUNDRY_PROJECT_ENDPOINT $($config.foundryEndpoint)",
    "azd env set AZURE_AI_MODEL_DEPLOYMENT_NAME <chat-model-deployment>",
    'azd env set ADJUDICATOR_A2A_URL <adjudicator-a2a-endpoint>',
    'azd provision',
    'azd deploy'
)

Write-Section 'Adjudicator commands'
$adjudicatorCommands | ForEach-Object { Write-Host $_ }

Write-Section 'Triage orchestrator commands'
$triageCommands | ForEach-Object { Write-Host $_ }

Write-Section 'Portal check'
Write-Host "Open Foundry project: $($config.foundryEndpoint)"
Write-Host "Confirm hosted agents named '$($config.adjudicatorAgentName)' and '$($config.triageAgentName)' appear in the portal."

if ($WhatIf) {
    Write-Host ''
    Write-Host 'WhatIf: plan only; no command execution attempted.' -ForegroundColor Green
}

