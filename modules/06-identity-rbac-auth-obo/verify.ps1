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
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'foundryProjectResourceId',
    'principalId',
    'roles',
    'oboToolboxName',
    'oboConnectionName'
)

Write-Section 'RBAC verification'
$az = Get-Command az -ErrorAction SilentlyContinue
if (-not $az) {
    Write-Host 'Azure CLI not found. Install Azure CLI and sign in to list live role assignments.' -ForegroundColor Yellow
}
else {
    try {
        $scopes = [System.Collections.Generic.HashSet[string]]::new()
        [void]$scopes.Add([string]$config.foundryProjectResourceId)
        foreach ($role in @($config.roles)) {
            if ($role.scopeResourceId) {
                [void]$scopes.Add([string]$role.scopeResourceId)
            }
        }

        foreach ($scope in $scopes) {
            Write-Host "Scope: $scope" -ForegroundColor Cyan
            $roleAssignments = az role assignment list `
                --scope $scope `
                --assignee-object-id $config.principalId `
                --all `
                --query "[].{Role:roleDefinitionName, Scope:scope, PrincipalType:principalType}" `
                -o table

            if ($LASTEXITCODE -ne 0) {
                throw 'az role assignment list returned a non-zero exit code.'
            }

            if ([string]::IsNullOrWhiteSpace($roleAssignments)) {
                Write-Host 'No matching assignments were found for this principal and scope.' -ForegroundColor Yellow
            }
            else {
                Write-Host $roleAssignments
            }
        }
    }
    catch {
        Write-Host "Best-effort RBAC verification could not complete: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Section 'OBO toolbox / connection verification'
$python = Get-PythonCommand
$verifyScript = Join-Path $PSScriptRoot 'src\provision_obo_toolbox.py'
& $python $verifyScript --config $ConfigPath --action verify
if ($LASTEXITCODE -ne 0) {
    throw "OBO asset verification failed with exit code $LASTEXITCODE."
}
