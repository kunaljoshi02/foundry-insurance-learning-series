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
    'chatModelDeploymentName',
    'agentName',
    'toolboxName',
    'toolboxVersion',
    'skills'
))

$python = Get-PythonCommand
$inspectScript = Join-Path $PSScriptRoot 'src\inspect_toolbox.py'

Write-Section 'Inspecting Skills, toolbox, and agent attachment'
& $python $inspectScript --config $ConfigPath --check-agent
if ($LASTEXITCODE -ne 0) {
    throw "Verification failed with exit code $LASTEXITCODE."
}
