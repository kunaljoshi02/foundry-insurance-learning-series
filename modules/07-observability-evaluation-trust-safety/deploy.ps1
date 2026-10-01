#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot 'config.json'),
    [switch]$EnableLiveMode
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\shared\powershell\Common.ps1')

function Write-Guidance {
    param([hashtable]$Config)

    Write-Section 'Authoring-time OTel guidance'
    Write-Host 'This module does not provision Azure resources.' -ForegroundColor Yellow
    Write-Host 'Use the foundation or later networking modules for Application Insights creation.'
    Write-Host ''
    Write-Host 'Wire telemetry into agent code directly:'
    Write-Host '  1. Import src\otel_setup.py from your triage/adjudicator process.'
    Write-Host '  2. Call configure_otel(service_name=<agent-role>).' 
    Write-Host '  3. Wrap each request in start_agent_run_span(...).' 
    Write-Host '  4. Decorate tool functions with @instrument_tool_call.'
    Write-Host ''
    Write-Host ('Configured placeholders: foundryEndpoint={0}; evalPassThreshold={1}' -f $Config.foundryEndpoint, $Config.evalPassThreshold)

    if ($Config.appInsightsConnectionString) {
        Write-Host 'App Insights connection string is present in config.json and can be supplied to agent code at runtime.'
    }

    if ($EnableLiveMode) {
        Write-Host ''
        Write-Host 'Optional live mode guidance:' -ForegroundColor Cyan
        Write-Host '  - Keep live evaluation explicit and opt-in.'
        Write-Host '  - Pass a custom router implementation to src\evaluator.py via --live --router module:function.'
        Write-Host '  - Do not make live mode the default CI path.'
    }
}

if ($WhatIfPreference) {
    Write-Section 'WhatIf plan'
    Write-Host ('Would validate configuration at {0}' -f $ConfigPath)
    Write-Host 'Would print authoring-time OTel wiring guidance for agent code.'
    if ($EnableLiveMode) {
        Write-Host 'Would also print optional live-mode evaluation guidance.'
    }
    return
}

Write-Section 'Validating configuration'
$config = Get-ModuleConfig -ConfigPath $ConfigPath -RequiredKeys @(
    'foundryEndpoint',
    'appInsightsConnectionString',
    'evalPassThreshold'
)

if ($PSCmdlet.ShouldProcess('module configuration', 'Validate offline guidance inputs')) {
    Write-Host 'Configuration is present and non-placeholder.' -ForegroundColor Green
    Write-Guidance -Config $config
}
