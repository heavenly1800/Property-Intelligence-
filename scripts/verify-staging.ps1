[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$FrontendUrl,
    [Parameter(Mandatory = $true)][string]$BackendUrl,
    [ValidateSet("enabled", "disabled", "skip")][string]$DocsExpectation = "skip"
)

$ErrorActionPreference = "Stop"
$FrontendUrl = $FrontendUrl.TrimEnd("/")
$BackendUrl = $BackendUrl.TrimEnd("/")
$failures = 0

function Test-Status {
    param([string]$Name, [string]$Url, [int[]]$Expected)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 20
        $status = [int]$response.StatusCode
    }
    catch {
        $status = if ($null -ne $_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
    }
    if ($status -in $Expected) {
        Write-Host "PASS: $Name returned HTTP $status" -ForegroundColor Green
    }
    else {
        Write-Host "FAIL: $Name returned HTTP $status; expected $($Expected -join ' or ')" -ForegroundColor Red
        $script:failures++
    }
}

Test-Status "Frontend" $FrontendUrl @(200)
Test-Status "Liveness" "$BackendUrl/health/live" @(200)
Test-Status "Readiness" "$BackendUrl/health/ready" @(200)
Test-Status "Version" "$BackendUrl/health/version" @(200)
Test-Status "Unauthenticated protected API" "$BackendUrl/properties" @(401)
if ($DocsExpectation -eq "enabled") { Test-Status "API docs" "$BackendUrl/docs" @(200) }
if ($DocsExpectation -eq "disabled") { Test-Status "API docs" "$BackendUrl/docs" @(404) }

if ($failures -gt 0) {
    Write-Error "$failures staging verification check(s) failed."
    exit 1
}
Write-Host "Staging endpoint verification passed." -ForegroundColor Green
