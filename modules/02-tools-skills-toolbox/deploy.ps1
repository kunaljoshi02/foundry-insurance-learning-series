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
    'chatModelDeploymentName',
    'agentName',
    'toolboxName',
    'toolboxVersion',
    'skills'
)

$python = Get-PythonCommand
$provisionScript = Join-Path $PSScriptRoot 'src\provision_toolbox.py'
$attachScript = Join-Path $PSScriptRoot 'src\attach_toolbox.py'

Write-Section 'Provisioning Skills and toolbox'
$provisionArgs = @($provisionScript, '--config', $ConfigPath)
if ($WhatIfPreference) { $provisionArgs += '--what-if' }

if ($PSCmdlet.ShouldProcess($config.toolboxName, 'Provision/update module Skills and toolbox')) {
    & $python @provisionArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Provisioning failed with exit code $LASTEXITCODE."
    }
}

Write-Section 'Attaching toolbox to agent'
$attachArgs = @($attachScript, '--config', $ConfigPath)
if ($WhatIfPreference) { $attachArgs += '--what-if' }

if ($PSCmdlet.ShouldProcess($config.agentName, "Attach toolbox '$($config.toolboxName)'")) {
    & $python @attachArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Attachment failed with exit code $LASTEXITCODE."
    }
}

Write-Host "`nDone." -ForegroundColor Green
