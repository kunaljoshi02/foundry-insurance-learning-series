#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ArtifactsPath = (Join-Path $PSScriptRoot 'artifacts')
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

Write-Section 'Cleaning local artifacts'

if (-not (Test-Path $ArtifactsPath)) {
    Write-Host 'No local artifacts folder found. Nothing to clean.'
    return
}

$targets = Get-ChildItem -Path $ArtifactsPath -File -ErrorAction SilentlyContinue
if (-not $targets) {
    Write-Host 'Artifacts folder exists but contains no files to remove.'
    return
}

foreach ($target in $targets) {
    if ($PSCmdlet.ShouldProcess($target.FullName, 'Remove generated local artifact')) {
        Remove-Item -Path $target.FullName -Force
        Write-Host ('Removed {0}' -f $target.Name)
    }
}

$remaining = Get-ChildItem -Path $ArtifactsPath -Force -ErrorAction SilentlyContinue
if (-not $remaining) {
    if ($PSCmdlet.ShouldProcess($ArtifactsPath, 'Remove empty artifacts directory')) {
        Remove-Item -Path $ArtifactsPath -Force
        Write-Host 'Removed empty artifacts directory.'
    }
}
