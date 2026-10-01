#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [switch]$PurgeUserData,
    [string]$UserIdentity
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

if ($PurgeUserData -and [string]::IsNullOrWhiteSpace($UserIdentity)) {
    throw "When -PurgeUserData is supplied, you must also provide -UserIdentity with the exact target identity or scope."
}

if (-not $WhatIfPreference) {
    Write-Section 'Confirmation'
    if (-not (Confirm-Destructive -ResourceName $config.memoryStoreName -Prompt "Type '$($config.memoryStoreName)' to confirm Memory store cleanup")) {
        throw 'Cleanup cancelled by user.'
    }

    if ($PurgeUserData) {
        if (-not (Confirm-Destructive -ResourceName $UserIdentity -Prompt "Type the exact user identity to confirm targeted memory purge")) {
            throw 'Targeted user-memory purge cancelled by user.'
        }
    }
}

$python = Get-PythonCommand
$scriptPath = Join-Path $PSScriptRoot 'src\provision_memory.py'
if (-not (Test-Path $scriptPath)) {
    throw "Expected script not found: $scriptPath"
}

$commandArgs = @(
    $scriptPath,
    '--action', 'cleanup',
    '--config', $ConfigPath
)
if ($PurgeUserData) {
    $commandArgs += @('--purge-user-data', '--user-identity', $UserIdentity)
}
if ($WhatIfPreference) {
    $commandArgs += '--what-if'
}

Write-Section 'Detaching agent Memory and deleting the store'
if ($PurgeUserData) {
    Write-Host "Targeted user purge requested for: $UserIdentity"
}

if ($PSCmdlet.ShouldProcess($config.memoryStoreName, "Detach Memory from '$($config.agentName)' and delete module-owned Memory assets")) {
    & $python @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Cleanup failed with exit code $LASTEXITCODE."
    }
}
elseif ($WhatIfPreference) {
    & $python @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Cleanup WhatIf preview failed with exit code $LASTEXITCODE."
    }
}
