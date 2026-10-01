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

Write-Section 'Validating configuration'
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'agentName',
    'memoryStoreName'
)

$python = Get-PythonCommand
$scriptPath = Join-Path $PSScriptRoot 'src\provision_memory.py'
if (-not (Test-Path $scriptPath)) {
    throw "Expected script not found: $scriptPath"
}

$commandArgs = @(
    $scriptPath,
    '--action', 'ensure',
    '--config', $ConfigPath
)
if ($WhatIfPreference) {
    $commandArgs += '--what-if'
}

Write-Section 'Provisioning managed Memory'
Write-Host "Agent name: $($config.agentName)"
Write-Host "Memory store: $($config.memoryStoreName)"

if ($PSCmdlet.ShouldProcess($config.memoryStoreName, "Create or update the Memory store and attach it to '$($config.agentName)'")) {
    & $python @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Memory provisioning failed with exit code $LASTEXITCODE."
    }
}
elseif ($WhatIfPreference) {
    & $python @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Memory WhatIf preview failed with exit code $LASTEXITCODE."
    }
}

Write-Host "`nDone." -ForegroundColor Green
