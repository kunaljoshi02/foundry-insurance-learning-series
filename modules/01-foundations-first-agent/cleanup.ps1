[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
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

$commandArgs = @(
    $scriptPath,
    '--action', 'cleanup',
    '--config', $ConfigPath
)

if ($WhatIfPreference) {
    $commandArgs += '--what-if'
}

Write-Section "Cleaning up prompt agent"
Write-Host "Target agent: $($config.agentName)"

if (-not $WhatIfPreference) {
    if (-not (Confirm-Destructive -ResourceName $config.agentName -Prompt "Type the agent name to confirm deletion")) {
        throw "Deletion cancelled because the confirmation text did not match."
    }
}

if ($PSCmdlet.ShouldProcess($config.agentName, 'Delete the module prompt agent')) {
    & $PythonExecutable @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Prompt agent cleanup failed with exit code $LASTEXITCODE."
    }
}
elseif ($WhatIfPreference) {
    & $PythonExecutable @commandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Prompt agent WhatIf cleanup preview failed with exit code $LASTEXITCODE."
    }
}
