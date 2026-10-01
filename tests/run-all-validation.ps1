#Requires -Version 7.0
<#
.SYNOPSIS
    Runs ALL offline validation for the Foundry Insurance Learning Series repository.

.DESCRIPTION
    100% offline: PowerShell/Python syntax checks, JSON/YAML parsing, Bicep `az bicep build`
    (skipped gracefully if the Bicep CLI isn't installed), Markdown link sanity (local links only),
    and a tenant-specific/secret scan. NEVER calls `az deployment`, `azd provision/deploy`, or any
    live Foundry/Azure endpoint.

.PARAMETER RepoRoot
    Root of the repository. Defaults to two levels up from this script (tests/..).

.EXAMPLE
    ./tests/run-all-validation.ps1
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'
$failures = [System.Collections.Generic.List[string]]::new()
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue) ? 'python' : ((Get-Command python3 -ErrorAction SilentlyContinue) ? 'python3' : $null)

function Test-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Host "`n== $Name ==" -ForegroundColor Cyan
    try {
        & $Action
        Write-Host "PASS: $Name" -ForegroundColor Green
    }
    catch {
        Write-Host "FAIL: $Name -> $($_.Exception.Message)" -ForegroundColor Red
        $failures.Add($Name)
    }
}

# 1. PowerShell syntax check for every .ps1 file.
Test-Step 'PowerShell syntax' {
    $ps1Files = Get-ChildItem -Path $RepoRoot -Recurse -Filter '*.ps1' -File |
        Where-Object { $_.FullName -notmatch '\\\.git\\' }
    $bad = @()
    foreach ($f in $ps1Files) {
        $tokens = $null; $parseErrors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$parseErrors) | Out-Null
        if ($parseErrors.Count -gt 0) {
            $bad += "$($f.FullName): $($parseErrors[0].Message)"
        }
    }
    if ($bad.Count -gt 0) { throw ($bad -join '; ') }
    Write-Host "Checked $($ps1Files.Count) .ps1 files."
}

# 2. Python syntax check (py_compile) for every .py file.
if ($pythonCmd) {
    Test-Step 'Python syntax' {
        $pyFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter '*.py' -File |
            Where-Object { $_.FullName -notmatch '\\\.git\\|__pycache__' }
        $bad = @()
        foreach ($f in $pyFiles) {
            & $pythonCmd -m py_compile $f.FullName 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) { $bad += $f.FullName }
        }
        if ($bad.Count -gt 0) { throw ("Syntax errors in: " + ($bad -join ', ')) }
        Write-Host "Checked $($pyFiles.Count) .py files."
    }
}
else {
    Write-Host "`nSKIP: Python syntax (python not found)" -ForegroundColor Yellow
}

# 3. JSON parse check.
Test-Step 'JSON validity' {
    $jsonFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter '*.json' -File |
        Where-Object { $_.FullName -notmatch '\\\.git\\' }
    $bad = @()
    foreach ($f in $jsonFiles) {
        try { Get-Content $f.FullName -Raw | ConvertFrom-Json -ErrorAction Stop | Out-Null }
        catch { $bad += "$($f.FullName): $($_.Exception.Message)" }
    }
    if ($bad.Count -gt 0) { throw ($bad -join '; ') }
    Write-Host "Checked $($jsonFiles.Count) .json files."
}

# 4. YAML parse check (best-effort: uses Python's PyYAML if available, else a soft skip).
if ($pythonCmd) {
    Test-Step 'YAML validity' {
        $yamlFiles = Get-ChildItem -Path $RepoRoot -Recurse -Include '*.yaml', '*.yml' -File |
            Where-Object { $_.FullName -notmatch '\\\.git\\' }
        if ($yamlFiles.Count -eq 0) { Write-Host "No YAML files found."; return }
        $script = @'
import sys
try:
    import yaml
except ImportError:
    print("SKIP: PyYAML not installed"); sys.exit(0)
bad = []
for path in sys.argv[1:]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            list(yaml.safe_load_all(fh))
    except Exception as exc:
        bad.append(f"{path}: {exc}")
if bad:
    print("\n".join(bad)); sys.exit(1)
print(f"Checked {len(sys.argv) - 1} YAML files.")
'@
        $tmp = New-TemporaryFile
        Set-Content -Path $tmp -Value $script -Encoding utf8
        & $pythonCmd $tmp.FullName @($yamlFiles.FullName)
        $exit = $LASTEXITCODE
        Remove-Item $tmp -Force
        if ($exit -ne 0) { throw "YAML validation failed." }
    }
}

# 5. Bicep build (skipped gracefully if Bicep CLI isn't installed). Never deploys.
$bicepAvailable = $false
try { az bicep version 2>$null | Out-Null; $bicepAvailable = ($LASTEXITCODE -eq 0) } catch { $bicepAvailable = $false }
if ($bicepAvailable) {
    Test-Step 'Bicep build (offline)' {
        $bicepFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter '*.bicep' -File |
            Where-Object { $_.FullName -notmatch '\\\.git\\' }
        $bad = @()
        foreach ($f in $bicepFiles) {
            $out = az bicep build --file $f.FullName --stdout 2>&1
            if ($LASTEXITCODE -ne 0) { $bad += "$($f.FullName): $out" }
        }
        if ($bad.Count -gt 0) { throw ($bad -join "`n") }
        Write-Host "Checked $($bicepFiles.Count) .bicep files."
    }
}
else {
    Write-Host "`nSKIP: Bicep build (az bicep not available)" -ForegroundColor Yellow
}

# 6. Markdown local-link sanity (relative links only; does not fetch remote URLs).
Test-Step 'Markdown local links' {
    $mdFiles = Get-ChildItem -Path $RepoRoot -Recurse -Filter '*.md' -File |
        Where-Object { $_.FullName -notmatch '\\\.git\\' }
    $bad = @()
    $linkPattern = '\[[^\]]+\]\(([^)#]+)(#[^)]*)?\)'
    foreach ($f in $mdFiles) {
        $content = Get-Content $f.FullName -Raw
        foreach ($m in [regex]::Matches($content, $linkPattern)) {
            $target = $m.Groups[1].Value.Trim()
            if ($target -match '^(https?:|mailto:)') { continue }
            if ([string]::IsNullOrWhiteSpace($target)) { continue }
            $resolved = Join-Path $f.DirectoryName $target
            if (-not (Test-Path $resolved)) {
                $bad += "$($f.FullName) -> broken local link '$target'"
            }
        }
    }
    if ($bad.Count -gt 0) { throw ($bad -join "`n") }
    Write-Host "Checked $($mdFiles.Count) .md files."
}

# 7. Tenant-specific / secret scan via shared/python/secret_scan.py.
if ($pythonCmd) {
    Test-Step 'Secret / tenant-specific scan' {
        $script = @"
import sys
sys.path.insert(0, r'$RepoRoot\shared\python')
from secret_scan import scan_paths
from pathlib import Path
findings = scan_paths([Path(r'$RepoRoot')])
if findings:
    print('\n'.join(findings))
    sys.exit(1)
print('No findings.')
"@
        $tmp = New-TemporaryFile
        Set-Content -Path $tmp -Value $script -Encoding utf8
        & $pythonCmd $tmp.FullName
        $exit = $LASTEXITCODE
        Remove-Item $tmp -Force
        if ($exit -ne 0) { throw "Secret/tenant-specific scan found issues (see output above)." }
    }
}

# 8. Repository contract tests and Python unit tests across all modules (offline only).
if ($pythonCmd) {
    Test-Step 'Repository contract tests' {
        Push-Location $RepoRoot
        try {
            $output = & $pythonCmd -m unittest discover -s tests -v 2>&1
            $exit = $LASTEXITCODE
            if ($exit -ne 0) { throw ($output -join "`n") }
            Write-Host ($output -join "`n")
        }
        finally { Pop-Location }
    }
    Test-Step 'Python unit tests (all modules)' {
        $testDirs = Get-ChildItem -Path (Join-Path $RepoRoot 'modules') -Recurse -Directory -Filter 'tests' -ErrorAction SilentlyContinue
        $anyRan = $false
        $bad = @()
        foreach ($dir in $testDirs) {
            $moduleRoot = Split-Path $dir.FullName -Parent
            Push-Location $moduleRoot
            try {
                $output = & $pythonCmd -m unittest discover -s tests -v 2>&1
                $exit = $LASTEXITCODE
                if ($exit -ne 0) { $bad += "$moduleRoot`: $output" }
                else { $anyRan = $true }
            }
            finally { Pop-Location }
        }
        if ($bad.Count -gt 0) { throw ($bad -join "`n---`n") }
        if (-not $anyRan) { Write-Host "No module test directories found yet." }
    }
}

Write-Host "`n================================" -ForegroundColor Cyan
if ($failures.Count -eq 0) {
    Write-Host "ALL VALIDATION PASSED" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "VALIDATION FAILED: $($failures -join ', ')" -ForegroundColor Red
    exit 1
}
