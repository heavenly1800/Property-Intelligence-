[CmdletBinding()]
param([switch]$WithScanner)

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

function Wait-ForService {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$Attempts = 30
    )

    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
                Write-Host "SUCCESS: $Name responded with HTTP $($response.StatusCode) at $Url" -ForegroundColor Green
                return $true
            }
        }
        catch {
            if ($attempt -eq $Attempts) {
                Write-Host "FAILURE: $Name did not respond at $Url. $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        Start-Sleep -Seconds 1
    }

    return $false
}

Stop-PortListener -Port 8000
Stop-PortListener -Port 5173
Start-Sleep -Seconds 1

$backendDirectory = Join-Path $repositoryRoot "services\api"
$frontendDirectory = Join-Path $repositoryRoot "apps\web"
$backendCommand = "Set-Location -LiteralPath '$($backendDirectory.Replace("'", "''"))'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
$frontendCommand = "Set-Location -LiteralPath '$($frontendDirectory.Replace("'", "''"))'; npm run dev -- --host 127.0.0.1"
$scannerPidFile = Join-Path $repositoryRoot ".notification-scanner.pid"
$scannerCommand = "Set-Location -LiteralPath '$($backendDirectory.Replace("'", "''"))'; .\.venv\Scripts\python.exe -m app.jobs.notification_scan --interval 300 --pid-file '$($scannerPidFile.Replace("'", "''"))'"

Write-Host "Starting FastAPI backend in a new PowerShell window..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -WorkingDirectory $backendDirectory -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCommand)

Write-Host "Starting React frontend in a new PowerShell window..." -ForegroundColor Cyan
Start-Process -FilePath "powershell.exe" -WorkingDirectory $frontendDirectory -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontendCommand)

if ($WithScanner) {
    Write-Host "Starting notification scanner in a new PowerShell window..." -ForegroundColor Cyan
    Start-Process -FilePath "powershell.exe" -WorkingDirectory $backendDirectory -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $scannerCommand)
}

Start-Sleep -Seconds 2
$backendReady = Wait-ForService -Name "Backend" -Url "http://127.0.0.1:8000/docs"
$frontendReady = Wait-ForService -Name "Frontend" -Url "http://127.0.0.1:5173"

if (-not ($backendReady -and $frontendReady)) {
    Write-Host "Development startup completed with one or more failures." -ForegroundColor Red
    exit 1
}

Write-Host "Development services are running." -ForegroundColor Green
