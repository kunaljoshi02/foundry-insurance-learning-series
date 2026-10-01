#Requires -Version 7.0
[CmdletBinding()]
param(
    [double]$Threshold = 0.85,
    [string]$DatasetPath = (Join-Path $PSScriptRoot 'eval\triage-eval-dataset.json'),
    [string]$OutputPath = (Join-Path $PSScriptRoot 'artifacts\scorecard.json')
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

Write-Section 'Running offline evaluator'
$python = Get-PythonCommand
$evaluatorScript = Join-Path $PSScriptRoot 'src\evaluator.py'
$artifactDir = Split-Path -Parent $OutputPath
if (-not (Test-Path $artifactDir)) {
    New-Item -ItemType Directory -Path $artifactDir | Out-Null
}

& $python $evaluatorScript --dataset $DatasetPath --output $OutputPath --threshold $Threshold
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "Offline evaluation failed threshold $Threshold (exit code $exitCode)."
}

Write-Section 'Scorecard summary'
$scorecard = Get-Content $OutputPath -Raw | ConvertFrom-Json -AsHashtable
$datasetResolved = (Resolve-Path $DatasetPath).Path
$datasetDisplay = [System.IO.Path]::GetRelativePath($PSScriptRoot, $datasetResolved)
Write-Host ('Dataset: {0}' -f $datasetDisplay)
Write-Host ('Total:   {0}' -f $scorecard.total)
Write-Host ('Passed:  {0}' -f $scorecard.passed)
Write-Host ('Failed:  {0}' -f $scorecard.failed)
Write-Host ('PassRate:{0:P2}' -f [double]$scorecard.pass_rate)
Write-Host 'Verification passed.' -ForegroundColor Green
