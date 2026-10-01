#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [switch]$ApplyPolicies,
    [switch]$ExecuteOperatorCommands,
    [switch]$EnableEnterpriseOverlay,
    [string]$EnterpriseOverlayConfirmation,
    [string]$ApimResourceGroupName = '<apim-resource-group>',
    [string]$ApimServiceName = '<apim-service-name>',
    [string]$ApimApiId = '<apim-api-id>',
    [string]$DeploymentOperationId = 'get-deployment'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Test-IsPlaceholder {
    param([string]$Value)
    return (-not [string]::IsNullOrWhiteSpace($Value)) -and ($Value.StartsWith('<') -and $Value.EndsWith('>'))
}

Write-Section 'Validating configuration'
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'apimGatewayUrl',
    'chatModelDeploymentName'
)

$effectiveOverlayState = $EnableEnterpriseOverlay.IsPresent
if ($config.ContainsKey('enableEnterpriseOverlay') -and $config.enableEnterpriseOverlay -and -not $EnableEnterpriseOverlay) {
    Write-Warning "config.json requests enableEnterpriseOverlay=true, but the script keeps the overlay OFF unless -EnableEnterpriseOverlay is passed explicitly."
}

if ($EnableEnterpriseOverlay) {
    if ($EnterpriseOverlayConfirmation -ne 'yes-enable-enterprise-overlay') {
        throw "Enterprise overlay requested. Re-run with -EnterpriseOverlayConfirmation yes-enable-enterprise-overlay to print the gated networking plan."
    }
}

$policyRoot = Join-Path $PSScriptRoot 'infra\apim'
$apiPolicyPath = Join-Path $policyRoot 'foundry-api-policy.xml'
$operationPolicyPath = Join-Path $policyRoot 'get-deployment-operation-policy.xml'
$overlayTemplatePath = Join-Path $PSScriptRoot 'infra\enterprise-overlay\private-networking.bicep'

foreach ($path in @($apiPolicyPath, $operationPolicyPath, $overlayTemplatePath)) {
    if (-not (Test-Path $path)) {
        throw "Expected file not found: $path"
    }
}

Write-Section 'Module 08 deployment guidance'
Write-Host 'This script is safe by default: it validates config.json and prints an operator plan.' -ForegroundColor Yellow
Write-Host 'No Azure or APIM command is executed unless you pass -ApplyPolicies and -ExecuteOperatorCommands together.' -ForegroundColor Yellow

Write-Section 'Resolved learning configuration'
Write-Host "Foundry endpoint: $($config.foundryEndpoint)"
Write-Host "APIM gateway URL: $($config.apimGatewayUrl)"
Write-Host "Chat model deployment: $($config.chatModelDeploymentName)"
Write-Host "Enterprise overlay enabled for this run: $effectiveOverlayState"

Write-Section 'APIM policy plan'
Write-Host "API-level policy file: $apiPolicyPath"
Write-Host "Operation-level deployment probe policy file: $operationPolicyPath"
Write-Host ''
Write-Host 'Operator sequence:' -ForegroundColor Cyan
Write-Host '  1. Import the API-level policy onto the Foundry-facing API.'
Write-Host "  2. Add or confirm an APIM operation for GET /deployments/{deploymentName}."
Write-Host "  3. Import the operation policy onto '$DeploymentOperationId'."
Write-Host '  4. Re-run this module''s local verify.ps1 before testing against any live APIM instance.'

$apiPolicyCommand = @(
    'az apim api policy update',
    "--resource-group `"$ApimResourceGroupName`"",
    "--service-name `"$ApimServiceName`"",
    "--api-id `"$ApimApiId`"",
    "--xml-file `"$apiPolicyPath`""
) -join ' '

$operationPolicyCommand = @(
    'az apim api operation policy update',
    "--resource-group `"$ApimResourceGroupName`"",
    "--service-name `"$ApimServiceName`"",
    "--api-id `"$ApimApiId`"",
    "--operation-id `"$DeploymentOperationId`"",
    "--xml-file `"$operationPolicyPath`""
) -join ' '

Write-Host ''
Write-Host 'Preview commands:' -ForegroundColor Cyan
Write-Host $apiPolicyCommand
Write-Host $operationPolicyCommand

if ($ApplyPolicies -and $ExecuteOperatorCommands) {
    foreach ($value in @($ApimResourceGroupName, $ApimServiceName, $ApimApiId)) {
        if (Test-IsPlaceholder -Value $value) {
            throw 'Real APIM identifiers are required before operator commands can run. Replace placeholder parameter values first.'
        }
    }

    $az = Get-Command az -ErrorAction SilentlyContinue
    if (-not $az) {
        throw 'Azure CLI (az) is not installed. Re-run without -ExecuteOperatorCommands to keep this as a printed plan.'
    }

    Write-Section 'Optional operator command execution'
    if ($PSCmdlet.ShouldProcess($ApimServiceName, 'Import sanitized APIM policies for the test API')) {
        & $az.Source apim api policy update --resource-group $ApimResourceGroupName --service-name $ApimServiceName --api-id $ApimApiId --xml-file $apiPolicyPath
        if ($LASTEXITCODE -ne 0) {
            throw "API policy import failed with exit code $LASTEXITCODE."
        }

        & $az.Source apim api operation policy update --resource-group $ApimResourceGroupName --service-name $ApimServiceName --api-id $ApimApiId --operation-id $DeploymentOperationId --xml-file $operationPolicyPath
        if ($LASTEXITCODE -ne 0) {
            throw "Operation policy import failed with exit code $LASTEXITCODE."
        }
    }
}
elseif ($ApplyPolicies) {
    Write-Warning 'You passed -ApplyPolicies without -ExecuteOperatorCommands. The script will continue to preview only.'
}

Write-Section 'Enterprise overlay plan'
if (-not $EnableEnterpriseOverlay) {
    Write-Host 'Enterprise overlay is OFF by default.' -ForegroundColor Green
    Write-Host 'No private-networking resources are referenced or planned in this run.'
}
else {
    Write-Host 'Enterprise overlay explicitly enabled for plan output.' -ForegroundColor Yellow
    Write-Host 'This module never silently deploys networking changes. Review the printed command below and run it manually if approved.' -ForegroundColor Yellow
    Write-Host ''
    Write-Host 'Suggested what-if command:' -ForegroundColor Cyan
    Write-Host "az deployment group what-if --template-file `"$overlayTemplatePath`" --parameters enableEnterpriseOverlay=true foundryAccountResourceId=`"<foundry-account-resource-id>`""
}

if ($WhatIfPreference) {
    Write-Host ''
    Write-Host 'WhatIf: preview complete.' -ForegroundColor Green
}
