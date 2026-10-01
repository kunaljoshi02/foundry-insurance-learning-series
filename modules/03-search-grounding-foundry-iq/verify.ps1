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
    'searchServiceName',
    'searchIndexName',
    'agentName',
    'searchConnectionName'
))

$python = Get-PythonCommand
$buildScript = Join-Path $PSScriptRoot 'src\build_search_index.py'
$connectScript = Join-Path $PSScriptRoot 'src\connect_search_to_agent.py'

Write-Section 'Checking Search index'
& $python $buildScript --config $ConfigPath --action verify
if ($LASTEXITCODE -ne 0) {
    throw "Index verification failed with exit code $LASTEXITCODE."
}

Write-Section 'Checking Foundry connection and agent grounding'
& $python $connectScript --config $ConfigPath --action verify
if ($LASTEXITCODE -ne 0) {
    throw "Grounding verification failed with exit code $LASTEXITCODE."
}
