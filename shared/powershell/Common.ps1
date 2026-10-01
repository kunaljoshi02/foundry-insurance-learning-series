# PowerShell helper functions shared across module deploy/verify/cleanup scripts.
# Dot-source with:  . (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Assert-CourseTag {
    <#
    .SYNOPSIS
        Throws unless the given Azure resource (as returned by `az ... show | ConvertFrom-Json`)
        carries the course ownership tag. Used by every cleanup.ps1 to avoid deleting anything
        this curriculum did not create.
    #>
    param(
        [Parameter(Mandatory = $true)][psobject]$Resource,
        [string]$ExpectedCourseTag = 'foundry-insurance-learning-series'
    )
    $tag = $Resource.tags.course
    if ($tag -ne $ExpectedCourseTag) {
        throw "Refusing to act on resource '$($Resource.name)': missing/mismatched 'course' tag (found '$tag')."
    }
}

function Confirm-Destructive {
    <#
    .SYNOPSIS
        Prompts the user to type the resource name to confirm a destructive action.
        Returns $true only on an exact match.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$ResourceName,
        [string]$Prompt = "Type the resource name to confirm deletion"
    )
    $typed = Read-Host $Prompt
    return $typed -eq $ResourceName
}

function Get-ModuleConfig {
    <#
    .SYNOPSIS
        Loads a module's config.json (never config.example.json), failing fast with guidance
        if it is missing or still contains placeholder values.
    #>
    param(
        [Parameter(Mandatory = $true)][string]$ConfigPath,
        [string[]]$RequiredKeys = @()
    )
    if (-not (Test-Path $ConfigPath)) {
        $example = $ConfigPath -replace '\.json$', '.example.json'
        $hint = (Test-Path $example) ? " Copy '$example' to '$ConfigPath' and fill in your own values." : ""
        throw "Config file not found: $ConfigPath.$hint"
    }
    $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json -AsHashtable
    foreach ($key in $RequiredKeys) {
        if (-not $config.ContainsKey($key) -or [string]::IsNullOrEmpty($config[$key])) {
            throw "Config file $ConfigPath is missing required key '$key'."
        }
        if ($config[$key] -is [string] -and $config[$key] -match '^<.*>$') {
            throw "Config file $ConfigPath still has a placeholder value for '$key' ('$($config[$key])')."
        }
    }
    return $config
}

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)
    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
}
