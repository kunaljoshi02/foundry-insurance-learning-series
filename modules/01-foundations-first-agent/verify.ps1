[CmdletBinding()]
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
    'agentName'
)

$scriptPath = Join-Path $PSScriptRoot 'src\create_prompt_agent.py'
if (-not (Test-Path $scriptPath)) {
    throw "Expected script not found: $scriptPath"
}

Write-Section "Verifying prompt agent"
& $PythonExecutable $scriptPath --action verify --config $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "Prompt agent verification failed with exit code $LASTEXITCODE."
}
