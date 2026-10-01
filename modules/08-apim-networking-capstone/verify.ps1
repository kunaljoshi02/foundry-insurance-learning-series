#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [string]$PythonExecutable = 'python',
    [string]$ModelName,
    [switch]$RunAllModuleVerifications
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Get-FreeTcpPort {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    $listener.Start()
    try {
        return ($listener.LocalEndpoint).Port
    }
    finally {
        $listener.Stop()
    }
}

function Get-ConfiguredModelName {
    param(
        [string]$Path,
        [string]$ExplicitModelName
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitModelName)) {
        return $ExplicitModelName
    }

    if (Test-Path $Path) {
        try {
            $config = Get-Content $Path -Raw | ConvertFrom-Json -AsHashtable
            if ($config.ContainsKey('chatModelDeploymentName') -and -not [string]::IsNullOrWhiteSpace([string]$config.chatModelDeploymentName)) {
                return [string]$config.chatModelDeploymentName
            }
        }
        catch {
            Write-Warning "config.json exists but could not be parsed. Falling back to a local default model name. $($_.Exception.Message)"
        }
    }

    return 'demo-model'
}

function Invoke-LocalProbeVerification {
    param(
        [string]$ResolvedModelName
    )

    $scriptPath = Join-Path $PSScriptRoot 'src\mock_deployment_probe_server.py'
    if (-not (Test-Path $scriptPath)) {
        throw "Expected script not found: $scriptPath"
    }

    $port = Get-FreeTcpPort
    $process = $null

    Write-Section "Starting local deployment probe mock for '$ResolvedModelName'"
    try {
        $process = Start-Process -FilePath $PythonExecutable -ArgumentList @($scriptPath, '--port', $port, '--model-name', $ResolvedModelName) -PassThru -WindowStyle Hidden
    }
    catch {
        throw "Failed to start the Python mock server with '$PythonExecutable'. $($_.Exception.Message)"
    }

    try {
        $healthUri = "http://127.0.0.1:$port/healthz"
        $probeUri = "http://127.0.0.1:$port/deployments/$ResolvedModelName"

        $ready = $false
        for ($attempt = 1; $attempt -le 20; $attempt++) {
            Start-Sleep -Milliseconds 150
            try {
                $healthResponse = Invoke-RestMethod -Method Get -Uri $healthUri
                if ($healthResponse.status -eq 'ok') {
                    $ready = $true
                    break
                }
            }
            catch {
                if ($process.HasExited) {
                    throw "The mock server exited before it became ready."
                }
            }
        }

        if (-not $ready) {
            throw 'Timed out waiting for the local mock server to become ready.'
        }

        Write-Section 'Validating the deployment probe contract'
        $response = Invoke-RestMethod -Method Get -Uri $probeUri

        if ($response.name -ne $ResolvedModelName) {
            throw "Expected deployment name '$ResolvedModelName' but received '$($response.name)'."
        }
        if ($response.type -ne 'Microsoft.CognitiveServices/accounts/deployments') {
            throw "Unexpected resource type '$($response.type)'."
        }
        if (-not $response.id) {
            throw 'Response is missing id.'
        }
        if (-not $response.properties.model.name) {
            throw 'Response is missing properties.model.name.'
        }
        if ($response.properties.model.name -ne $ResolvedModelName) {
            throw "Expected properties.model.name '$ResolvedModelName' but received '$($response.properties.model.name)'."
        }
        if (-not $response.properties.model.format) {
            throw 'Response is missing properties.model.format.'
        }
        if (-not $response.properties.model.version) {
            throw 'Response is missing properties.model.version.'
        }
        if ($response.properties.provisioningState -ne 'Succeeded') {
            throw "Expected provisioningState 'Succeeded' but received '$($response.properties.provisioningState)'."
        }

        Write-Host "Probe contract validated for model '$ResolvedModelName' at $probeUri" -ForegroundColor Green
    }
    finally {
        if ($process -and -not $process.HasExited) {
            Stop-Process -Id $process.Id
            $process.WaitForExit()
        }
    }
}

function Invoke-AllModuleVerifications {
    param(
        [string]$ResolvedModelName
    )

    $results = [System.Collections.Generic.List[object]]::new()
    $moduleRoot = Split-Path $PSScriptRoot -Parent

    Get-ChildItem -Path $moduleRoot -Directory | Sort-Object Name | ForEach-Object {
        $verifyPath = Join-Path $_.FullName 'verify.ps1'
        if (-not (Test-Path $verifyPath)) {
            $results.Add([pscustomobject]@{
                Module = $_.Name
                Status = 'Missing'
                Notes = 'No verify.ps1 file found.'
            })
            return
        }

        if ($verifyPath -eq $PSCommandPath) {
            try {
                Invoke-LocalProbeVerification -ResolvedModelName $ResolvedModelName
                $results.Add([pscustomobject]@{
                    Module = $_.Name
                    Status = 'Passed'
                    Notes = "Local deployment-probe contract passed for '$ResolvedModelName'."
                })
            }
            catch {
                $results.Add([pscustomobject]@{
                    Module = $_.Name
                    Status = 'Failed'
                    Notes = $_.Exception.Message
                })
            }
            return
        }

        try {
            & $verifyPath *>$null
            $results.Add([pscustomobject]@{
                Module = $_.Name
                Status = 'Passed'
                Notes = 'Read-only module verification completed.'
            })
        }
        catch {
            $results.Add([pscustomobject]@{
                Module = $_.Name
                Status = 'Failed'
                Notes = $_.Exception.Message
            })
        }
    }

    Write-Section 'Consolidated verification status'
    $results | Format-Table -AutoSize

    $failedCount = ($results | Where-Object { $_.Status -eq 'Failed' }).Count
    $missingCount = ($results | Where-Object { $_.Status -eq 'Missing' }).Count
    if ($failedCount -gt 0 -or $missingCount -gt 0) {
        Write-Warning "Completed best-effort sweep. Failed: $failedCount. Missing verify scripts: $missingCount."
    }
}

$resolvedModelName = Get-ConfiguredModelName -Path $ConfigPath -ExplicitModelName $ModelName

if ($RunAllModuleVerifications) {
    Invoke-AllModuleVerifications -ResolvedModelName $resolvedModelName
    return
}

Invoke-LocalProbeVerification -ResolvedModelName $resolvedModelName
