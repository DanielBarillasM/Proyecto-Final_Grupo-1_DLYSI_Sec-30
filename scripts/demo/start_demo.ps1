[CmdletBinding()]
param(
    [string]$PythonPath = ".venv\Scripts\python.exe",
    [string]$CloudflaredPath = "",
    [switch]$LocalOnly
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$RunDirectory = Join-Path $RepoRoot ".demo-run"
$StatePath = Join-Path $RunDirectory "state.json"

function Resolve-RepoPath {
    param([string]$PathValue)
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $PathValue))
}

function Wait-HttpOk {
    param([string]$Uri, [int]$TimeoutSeconds = 90)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) { return }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $deadline)
    throw "El servicio no respondió HTTP 200 en $Uri dentro de ${TimeoutSeconds}s."
}

function Stop-CreatedProcess {
    param([System.Diagnostics.Process]$Process)
    if ($null -ne $Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
}

$resolvedPython = Resolve-RepoPath $PythonPath
if (-not (Test-Path -LiteralPath $resolvedPython -PathType Leaf)) {
    throw "No se encontró Python en $resolvedPython. Crea .venv e instala requirements-demo.txt."
}

if (-not $LocalOnly -and [string]::IsNullOrWhiteSpace($CloudflaredPath)) {
    $command = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($command) {
        $CloudflaredPath = $command.Source
    }
    else {
        $CloudflaredPath = Join-Path $env:USERPROFILE ".cache\cloudflared\cloudflared.exe"
    }
}
if (-not $LocalOnly) {
    $CloudflaredPath = [System.IO.Path]::GetFullPath($CloudflaredPath)
    if (-not (Test-Path -LiteralPath $CloudflaredPath -PathType Leaf)) {
        throw "No se encontró cloudflared. Indica -CloudflaredPath o usa -LocalOnly."
    }
}

New-Item -ItemType Directory -Force -Path $RunDirectory | Out-Null
if (Test-Path -LiteralPath $StatePath) {
    $previous = Get-Content -Raw -LiteralPath $StatePath | ConvertFrom-Json
    if (-not $previous.stopped_at_utc) {
        throw "Existe una demostración sin cierre registrado. Ejecuta scripts\demo\stop_demo.ps1."
    }
}

$backend = $null
$frontend = $null
$frontendServer = $null
$tunnel = $null
$savedMode = $env:TEXT_TO_SQL_MODE
$savedBackend = $env:TEXT_TO_SQL_BACKEND_URL
$savedShare = $env:GRADIO_SHARE
try {
    $env:TEXT_TO_SQL_MODE = "model"
    $backend = Start-Process -FilePath $resolvedPython `
        -ArgumentList @("-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000") `
        -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $RunDirectory "backend.stdout.log") `
        -RedirectStandardError (Join-Path $RunDirectory "backend.stderr.log")
    Wait-HttpOk -Uri "http://127.0.0.1:8000/health"

    $env:TEXT_TO_SQL_BACKEND_URL = "http://127.0.0.1:8000"
    $env:GRADIO_SHARE = "false"
    try {
        & $resolvedPython -c "import gradio" 2>$null
        $hasGradio = $LASTEXITCODE -eq 0
    }
    catch {
        $hasGradio = $false
    }
    if ($hasGradio) {
        $frontendExecutable = $resolvedPython
        $frontendArguments = @("app.py")
    }
    else {
        $uv = Get-Command uv -ErrorAction SilentlyContinue
        if (-not $uv) {
            throw "El entorno GPU no contiene Gradio y uv no está disponible para aislar la interfaz."
        }
        $frontendExecutable = $uv.Source
        $frontendArguments = @(
            "run", "--no-project", "--with", "gradio>=6,<7", "python", "app.py"
        )
    }
    $frontend = Start-Process -FilePath $frontendExecutable -ArgumentList $frontendArguments `
        -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $RunDirectory "frontend.stdout.log") `
        -RedirectStandardError (Join-Path $RunDirectory "frontend.stderr.log")
    Wait-HttpOk -Uri "http://127.0.0.1:7860"
    $frontendConnection = Get-NetTCPConnection -State Listen -LocalPort 7860 |
        Select-Object -First 1
    $frontendServer = Get-Process -Id $frontendConnection.OwningProcess

    $publicUrl = $null
    if (-not $LocalOnly) {
        $tunnel = Start-Process -FilePath $CloudflaredPath `
            -ArgumentList @("tunnel", "--url", "http://127.0.0.1:7860", "--no-autoupdate") `
            -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $RunDirectory "tunnel.stdout.log") `
            -RedirectStandardError (Join-Path $RunDirectory "tunnel.stderr.log")
        $deadline = (Get-Date).AddSeconds(90)
        do {
            Start-Sleep -Seconds 2
            $logs = @(
                (Join-Path $RunDirectory "tunnel.stdout.log"),
                (Join-Path $RunDirectory "tunnel.stderr.log")
            ) | Where-Object { Test-Path -LiteralPath $_ } | ForEach-Object {
                Get-Content -Raw -LiteralPath $_
            }
            $match = [regex]::Match(($logs -join "`n"), "https://[a-z0-9-]+\.trycloudflare\.com")
            if ($match.Success) { $publicUrl = $match.Value }
        } while (-not $publicUrl -and (Get-Date) -lt $deadline -and -not $tunnel.HasExited)
        if (-not $publicUrl) { throw "Cloudflare no produjo una URL temporal en 90 segundos." }
        Wait-HttpOk -Uri $publicUrl -TimeoutSeconds 120
    }

    $commit = (& git -C $RepoRoot rev-parse HEAD).Trim()
    $processes = @()
    if ($tunnel) {
        $processes += [ordered]@{ role = "tunnel"; pid = $tunnel.Id; name = $tunnel.ProcessName; started_utc = $tunnel.StartTime.ToUniversalTime().ToString("o") }
    }
    $processes += [ordered]@{ role = "frontend_server"; pid = $frontendServer.Id; name = $frontendServer.ProcessName; started_utc = $frontendServer.StartTime.ToUniversalTime().ToString("o") }
    if ($frontend.Id -ne $frontendServer.Id) {
        $processes += [ordered]@{ role = "frontend_launcher"; pid = $frontend.Id; name = $frontend.ProcessName; started_utc = $frontend.StartTime.ToUniversalTime().ToString("o") }
    }
    $processes += [ordered]@{ role = "backend"; pid = $backend.Id; name = $backend.ProcessName; started_utc = $backend.StartTime.ToUniversalTime().ToString("o") }
    $state = [ordered]@{
        repo_root = $RepoRoot
        commit = $commit
        started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        local_url = "http://127.0.0.1:7860"
        backend_url = "http://127.0.0.1:8000"
        public_url = $publicUrl
        processes = $processes
        stopped_at_utc = $null
    }
    $state | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $StatePath
    Write-Host "Demostración lista."
    Write-Host "Local:  http://127.0.0.1:7860"
    if ($publicUrl) { Write-Host "Pública: $publicUrl" }
    Write-Host "Estado: $StatePath"
}
catch {
    Stop-CreatedProcess $tunnel
    Stop-CreatedProcess $frontend
    Stop-CreatedProcess $backend
    throw
}
finally {
    $env:TEXT_TO_SQL_MODE = $savedMode
    $env:TEXT_TO_SQL_BACKEND_URL = $savedBackend
    $env:GRADIO_SHARE = $savedShare
}
