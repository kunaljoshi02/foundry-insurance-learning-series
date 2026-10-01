[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [string]$PythonExecutable = 'python'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

Write-Section "Loading module configuration"
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'chatModelDeploymentName',
    'agentName',
    'agentInstructionsFile'
)

$scriptPath = Join-Path $PSScriptRoot 'src\create_prompt_agent.py'
if (-not (Test-Path $scriptPath)) {
    throw "Expected script not found: $scriptPath"
}

$instructionsPath = Join-Path $PSScriptRoot $config.agentInstructionsFile
if (-not (Test-Path $instructionsPath)) {
    throw "Agent instructions file not found: $instructionsPath"
}

$commandArgs = @(
    $scriptPath,
    '--action', 'ensure',
    '--config', $ConfigPath,
    '--instructions-file', $instructionsPath
)

if ($WhatIfPreference) {
    $commandArgs += '--what-if'
}

Write-Section "Deploying prompt agent"
Write-Host "Agent name: $($config.agentName)"
Write-Host "Model deployment: $($config.chatModelDeploymentName)"
Write-Host "Foundry endpoint: $($config.foundryEndpoint)"

if ($PSCmdlet.ShouldProcess($config.agentName, 'Create or update the module prompt agent')) {
    & $PythonExecutable @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Prompt agent creation failed with exit code $LASTEXITCODE."
    }
}
elseif ($WhatIfPreference) {
    & $PythonExecutable @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Prompt agent WhatIf preview failed with exit code $LASTEXITCODE."
    }
}
