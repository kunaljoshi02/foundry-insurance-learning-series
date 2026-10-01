[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

$configPath = Join-Path $PSScriptRoot 'config.json'
$config = Get-ModuleConfig -ConfigPath $configPath -RequiredKeys @(
    'foundryEndpoint',
    'triageAgentName',
    'adjudicatorAgentName'
)

Write-Section 'Module 04 verification'
Write-Host 'Read-only verification only. No resources are created, modified, or deleted.'

$az = Get-Command az -ErrorAction SilentlyContinue
if (-not $az) {
    Write-Host 'Azure CLI not found. Install Azure CLI, sign in, then rerun this script.' -ForegroundColor Yellow
    Write-Host "Expected agents: $($config.triageAgentName), $($config.adjudicatorAgentName)"
    return
}

try {
    $token = az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv 2>$null
    if (-not $token) {
        throw 'No Azure AI access token was returned. Run az login first.'
    }

    $uri = "$($config.foundryEndpoint.TrimEnd('/'))/agents?api-version=v1"
    Write-Host "Listing agent deployments from $uri"
    $response = az rest --method get --uri $uri --headers "Authorization=Bearer $token" | ConvertFrom-Json

    $agents = @($response.value)
    if (-not $agents.Count) {
        Write-Host 'No agents were returned. Verify that the project endpoint and login context are correct.' -ForegroundColor Yellow
        return
    }

    $agents |
        Select-Object name, kind, description |
        Format-Table -AutoSize

    $expected = @($config.triageAgentName, $config.adjudicatorAgentName)
    foreach ($agentName in $expected) {
        if ($agents.name -contains $agentName) {
            Write-Host "Verified: $agentName is present." -ForegroundColor Green
        }
        else {
            Write-Host "Missing from list: $agentName" -ForegroundColor Yellow
        }
    }
}
catch {
    Write-Host "Best-effort verification could not complete: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host 'Guidance: verify login context, confirm the project endpoint in config.json, then inspect Hosted agents in the Foundry portal.'
}

