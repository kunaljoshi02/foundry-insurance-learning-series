#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
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

function Get-ResourceGroupFromResourceId {
    param([Parameter(Mandatory = $true)][string]$ResourceId)

    $match = [regex]::Match($ResourceId, '/resourceGroups/([^/]+)/', 'IgnoreCase')
    if (-not $match.Success) {
        throw "Could not derive the resource group name from resource ID '$ResourceId'."
    }

    return $match.Groups[1].Value
}

Write-Section 'Validating configuration'
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'foundryProjectResourceId',
    'principalId',
    'roles',
    'oboToolboxName',
    'oboConnectionName',
    'oboConnectionEndpoint',
    'oboConnectionAudience'
)

if (-not ($config.roles -is [System.Collections.IEnumerable]) -or @($config.roles).Count -eq 0) {
    throw 'config.json must contain a non-empty roles array.'
}

$resourceGroupName = Get-ResourceGroupFromResourceId -ResourceId ([string]$config.foundryProjectResourceId)
$principalType = if ($config.ContainsKey('principalType') -and $config.principalType) { [string]$config.principalType } else { 'User' }
$rolesJson = @($config.roles) | ConvertTo-Json -Compress -Depth 10
$deploymentName = 'module-06-identity-rbac-auth-obo'

$az = Get-Command az -ErrorAction SilentlyContinue
$python = Get-PythonCommand
$provisionScript = Join-Path $PSScriptRoot 'src\provision_obo_toolbox.py'
$bicepFile = Join-Path $PSScriptRoot 'infra\rbac.bicep'

Write-Section 'RBAC deployment plan'
Write-Host "Target project scope: $($config.foundryProjectResourceId)"
Write-Host "Principal ID: $($config.principalId)"
Write-Host 'Requested roles:'
@($config.roles) | ForEach-Object {
    $scopeSuffix = if ($_.scopeResourceId) { " (scope override: $($_.scopeResourceId))" } else { '' }
    Write-Host ("- " + $_.name + $scopeSuffix)
}

if (-not $az) {
    if (-not $WhatIf) {
        throw 'Azure CLI was not found on PATH. Re-run with -WhatIf for a printed plan or install Azure CLI to execute.'
    }

    Write-Host 'Azure CLI not found; showing the planned RBAC command only.' -ForegroundColor Yellow
    Write-Host "az deployment group what-if --name $deploymentName --resource-group $resourceGroupName --template-file `"$bicepFile`" --parameters foundryProjectResourceId=<...> principalId=<...> principalType=$principalType roles='<json>'"
}
else {
    $rbacArgs = @(
        'deployment', 'group', ($(if ($WhatIf) { 'what-if' } else { 'create' })),
        '--name', $deploymentName,
        '--resource-group', $resourceGroupName,
        '--template-file', $bicepFile,
        '--parameters',
        "foundryProjectResourceId=$($config.foundryProjectResourceId)",
        "principalId=$($config.principalId)",
        "principalType=$principalType",
        "roles=$rolesJson"
    )

    & $az.Source @rbacArgs
    if ($LASTEXITCODE -ne 0) {
        throw "RBAC deployment step failed with exit code $LASTEXITCODE."
    }
}

Write-Section 'Provisioning isolated OBO toolbox and connection'
$toolboxArgs = @($provisionScript, '--config', $ConfigPath, '--action', 'ensure')
if ($WhatIf) { $toolboxArgs += '--what-if' }

& $python @toolboxArgs
if ($LASTEXITCODE -ne 0) {
    throw "OBO toolbox provisioning failed with exit code $LASTEXITCODE."
}

Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
