[CmdletBinding()]
param(
    [switch]$Confirm,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

$configPath = Join-Path $PSScriptRoot 'config.json'
$config = Get-ModuleConfig -ConfigPath $configPath -RequiredKeys @('azdEnvironmentName')
$envName = [string]$config.azdEnvironmentName

Write-Section 'Module 04 cleanup guidance'
Write-Host 'This module only supports cleanup for learners who deployed using the module-specific azd'
Write-Host 'environment name in config.json. It must not be pointed at any unrelated environment.' -ForegroundColor Yellow

$commands = @(
    "azd env select $envName",
    'azd down --force --purge'
)

if ($WhatIf -or -not $Confirm) {
    Write-Host 'Planned cleanup commands:'
    $commands | ForEach-Object { Write-Host $_ }
    if (-not $Confirm) {
        Write-Host ''
        Write-Host 'Pass -Confirm to run azd down for this module environment only.' -ForegroundColor Yellow
    }
    return
}

$azd = Get-Command azd -ErrorAction SilentlyContinue
if (-not $azd) {
    throw 'Azure Developer CLI (azd) is not installed. Re-run without -Confirm to print the commands only.'
}

if (-not (Confirm-Destructive -ResourceName $envName -Prompt 'Type the module azd environment name to confirm cleanup')) {
    throw 'Cleanup cancelled because the typed environment name did not match config.json.'
}

Write-Host "Selecting azd environment '$envName'..."
& azd env select $envName
Write-Host "Running azd down for '$envName'..."
& azd down --force --purge

