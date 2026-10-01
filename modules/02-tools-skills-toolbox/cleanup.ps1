#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [switch]$DetachFromAgent
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
    'chatModelDeploymentName',
    'agentName',
    'toolboxName',
    'toolboxVersion',
    'skills'
)

if (-not $WhatIfPreference) {
    Write-Section 'Confirmation'
    if (-not (Confirm-Destructive -ResourceName $config.toolboxName -Prompt "Type '$($config.toolboxName)' to confirm cleanup")) {
        throw 'Cleanup cancelled by user.'
    }
}

$python = Get-PythonCommand
$cleanupScript = Join-Path $PSScriptRoot 'src\cleanup_toolbox.py'
$cleanupArgs = @($cleanupScript, '--config', $ConfigPath)
if ($DetachFromAgent) { $cleanupArgs += '--detach-agent' }
if ($WhatIfPreference) { $cleanupArgs += '--what-if' }

Write-Section 'Removing module-owned Skills and toolbox'
if ($PSCmdlet.ShouldProcess($config.toolboxName, 'Detach toolbox (optional) and delete module-created assets')) {
    & $python @cleanupArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Cleanup failed with exit code $LASTEXITCODE."
    }
}
