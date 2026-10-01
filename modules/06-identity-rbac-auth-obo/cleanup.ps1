#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [switch]$Confirm,
    [switch]$WhatIf
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
    'foundryProjectResourceId',
    'principalId',
    'roles',
    'oboToolboxName',
    'oboConnectionName'
)

Write-Section 'Cleanup plan'
Write-Host "Toolbox to remove: $($config.oboToolboxName)"
Write-Host "Connection to remove: $($config.oboConnectionName)"
Write-Host "Principal ID to unassign: $($config.principalId)"

if (-not $WhatIf -and -not $Confirm) {
    Write-Host ''
    Write-Host 'Pass -WhatIf to preview or -Confirm to execute cleanup.' -ForegroundColor Yellow
    return
}

if ($Confirm -and -not $WhatIf) {
    if (-not (Confirm-Destructive -ResourceName $config.oboToolboxName -Prompt "Type '$($config.oboToolboxName)' to confirm module cleanup")) {
        throw 'Cleanup cancelled by user.'
    }
}

$az = Get-Command az -ErrorAction SilentlyContinue
if (-not $az -and -not $WhatIf) {
    throw 'Azure CLI was not found on PATH. Re-run with -WhatIf for a preview or install Azure CLI to execute.'
}

Write-Section 'Removing module RBAC assignments'
foreach ($role in @($config.roles)) {
    $scope = if ($role.scopeResourceId) { [string]$role.scopeResourceId } else { [string]$config.foundryProjectResourceId }
    if ($WhatIf) {
        Write-Host "[WhatIf] Would remove role '$($role.name)' for principal '$($config.principalId)' at scope '$scope'."
        continue
    }

    & $az.Source role assignment delete `
        --assignee-object-id $config.principalId `
        --role $role.name `
        --scope $scope

    if ($LASTEXITCODE -ne 0) {
        throw "Failed removing role '$($role.name)' at scope '$scope'."
    }
}

Write-Section 'Removing isolated OBO toolbox and connection'
$python = Get-PythonCommand
$cleanupScript = Join-Path $PSScriptRoot 'src\provision_obo_toolbox.py'
$toolboxArgs = @($cleanupScript, '--config', $ConfigPath, '--action', 'cleanup')
if ($WhatIf) { $toolboxArgs += '--what-if' }

& $python @toolboxArgs
if ($LASTEXITCODE -ne 0) {
    throw "OBO asset cleanup failed with exit code $LASTEXITCODE."
}

Write-Host ''
Write-Host 'Cleanup completed.' -ForegroundColor Green
