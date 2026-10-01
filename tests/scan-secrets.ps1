#Requires -Version 7.0
<#
.SYNOPSIS
    Standalone wrapper for the tenant-specific/secret scan (used directly or by run-all-validation.ps1).
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue) ? 'python' : ((Get-Command python3 -ErrorAction SilentlyContinue) ? 'python3' : $null)
if (-not $pythonCmd) {
    throw "Python is required for the secret scan. Install Python 3.10+."
}

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
exit $exit
