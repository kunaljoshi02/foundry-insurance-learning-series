#Requires -Version 7.0
[CmdletBinding()]
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

Write-Section 'Validating configuration'
[void](Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'agentName',
    'memoryStoreName'
))

$python = Get-PythonCommand
$scriptPath = Join-Path $PSScriptRoot 'src\provision_memory.py'
if (-not (Test-Path $scriptPath)) {
    throw "Expected script not found: $scriptPath"
}

Write-Section 'Verifying Memory configuration'
& $python $scriptPath --action verify --config $ConfigPath
if ($LASTEXITCODE -ne 0) {
    throw "Verification failed with exit code $LASTEXITCODE."
}
