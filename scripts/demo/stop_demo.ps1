[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$StatePath = Join-Path $RepoRoot ".demo-run\state.json"
if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
    throw "No existe $StatePath. No hay una demostración registrada para cerrar."
}

$state = Get-Content -Raw -LiteralPath $StatePath | ConvertFrom-Json
if ([System.IO.Path]::GetFullPath($state.repo_root) -ne $RepoRoot) {
    throw "El estado pertenece a otro repositorio; no se detendrá ningún proceso."
}

foreach ($entry in $state.processes) {
    if ($null -eq $entry.pid) { continue }
    $process = Get-Process -Id ([int]$entry.pid) -ErrorAction SilentlyContinue
    if ($null -eq $process) { continue }
    $expectedStart = [datetime]::Parse($entry.started_utc).ToUniversalTime()
    $sameStart = [math]::Abs(($process.StartTime.ToUniversalTime() - $expectedStart).TotalSeconds) -le 5
    if ($process.ProcessName -ne $entry.name -or -not $sameStart) {
        Write-Warning "PID $($entry.pid) ya pertenece a otro proceso; no se detuvo."
        continue
    }
    Stop-Process -Id $process.Id -Force
    Write-Host "Detenido: $($entry.role) (PID $($entry.pid))."
}

$state.stopped_at_utc = (Get-Date).ToUniversalTime().ToString("o")
$state | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $StatePath

$activePorts = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in 3000, 7860, 8000 }
if ($activePorts) {
    Write-Warning "Los puertos 3000, 7860 u 8000 siguen ocupados por procesos ajenos al estado registrado."
}
else {
    Write-Host "Demostración cerrada; los puertos 3000, 7860 y 8000 están libres."
}
