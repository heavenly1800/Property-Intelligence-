[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repositoryRoot = $PSScriptRoot

if ((Get-Location).Path.TrimEnd("\") -ne $repositoryRoot.TrimEnd("\")) {
    Write-Error "Run this script from the repository root: $repositoryRoot"
    exit 1
}

function Stop-PortListener {
    param([Parameter(Mandatory = $true)][int]$Port)

    $processIds = @(
        netstat -ano -p tcp |
            Select-String -Pattern "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$" |
            ForEach-Object { [int]$_.Matches[0].Groups[1].Value } |
            Sort-Object -Unique
    )

    if ($processIds.Count -eq 0) {
        Write-Host "Port $Port is already clear." -ForegroundColor DarkGray
        return
    }

    foreach ($processId in $processIds) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($null -ne $process) {
            Write-Host "Stopping PID $processId ($($process.ProcessName)) bound to port $Port..." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force
        }
    }
}

Stop-PortListener -Port 8000
Stop-PortListener -Port 5173
$scannerPidFile = Join-Path $repositoryRoot ".notification-scanner.pid"
if (Test-Path -LiteralPath $scannerPidFile) {
    $scannerPid = [int](Get-Content -LiteralPath $scannerPidFile -Raw)
    $scannerProcess = Get-Process -Id $scannerPid -ErrorAction SilentlyContinue
    if ($null -ne $scannerProcess) {
        Write-Host "Stopping notification scanner PID $scannerPid..." -ForegroundColor Yellow
        Stop-Process -Id $scannerPid -Force
    }
    Remove-Item -LiteralPath $scannerPidFile -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1

$remainingListeners = @(
    netstat -ano -p tcp |
        Select-String -Pattern "^\s*TCP\s+\S+:(8000|5173)\s+\S+\s+LISTENING\s+\d+\s*$"
)

if ($remainingListeners.Count -gt 0) {
    Write-Host "FAILURE: One or more development ports are still in use." -ForegroundColor Red
    $remainingListeners | ForEach-Object { Write-Host $_.Line }
    exit 1
}

Write-Host "SUCCESS: Ports 8000 and 5173 are clear." -ForegroundColor Green
