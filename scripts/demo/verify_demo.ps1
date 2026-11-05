[CmdletBinding()]
param(
    [string]$PublicUrl = "",
    [switch]$RunInference
)

$ErrorActionPreference = "Stop"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$RunDirectory = Join-Path $RepoRoot ".demo-run"
$StatePath = Join-Path $RunDirectory "state.json"
if (-not (Test-Path -LiteralPath $StatePath -PathType Leaf)) {
    throw "Primero ejecuta scripts\demo\start_demo.ps1."
}

$state = Get-Content -Raw -LiteralPath $StatePath | ConvertFrom-Json
if ([string]::IsNullOrWhiteSpace($PublicUrl)) { $PublicUrl = $state.public_url }
$checks = [ordered]@{}
$health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 10
$checks.backend_health = $health
$local = Invoke-WebRequest -Uri "http://127.0.0.1:7860" -UseBasicParsing -TimeoutSec 10
$checks.local_http_status = $local.StatusCode
if (-not [string]::IsNullOrWhiteSpace($PublicUrl)) {
    $public = Invoke-WebRequest -Uri $PublicUrl -UseBasicParsing -TimeoutSec 30
    $checks.public_url = $PublicUrl
    $checks.public_http_status = $public.StatusCode
}

$unsafeBodies = @(
    @{ id = "delete"; sql = "DELETE FROM clientes WHERE id = 1;" },
    @{ id = "multiple"; sql = "SELECT * FROM clientes; DROP TABLE clientes;" }
)
$rejections = @()
foreach ($case in $unsafeBodies) {
    try {
        Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/validate-sql" `
            -ContentType "application/json" -Body (@{ sql = $case.sql } | ConvertTo-Json) | Out-Null
        $rejections += [ordered]@{ case = $case.id; rejected = $false; status = 200 }
    }
    catch {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $rejections += [ordered]@{ case = $case.id; rejected = ($statusCode -eq 422); status = $statusCode }
    }
}
$checks.unsafe_sql_rejections = $rejections

if ($RunInference) {
    $schema = @"
CREATE TABLE clientes (
  id INT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  ciudad VARCHAR(80) NOT NULL
);
CREATE TABLE pedidos (
  id INT PRIMARY KEY,
  cliente_id INT NOT NULL,
  fecha DATE NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  estado VARCHAR(30) NOT NULL,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
"@
    $questions = @(
        @{ id = "facil"; text = "Lista los nombres y las ciudades de todos los clientes." },
        @{ id = "media"; text = "Muestra los clientes que no tienen ningún pedido." },
        @{ id = "dificil"; text = "¿Qué cliente tuvo el mayor total de pedidos completados durante 2024?" }
    )
    $inferences = @()
    foreach ($case in $questions) {
        $body = @{ esquema = $schema; pregunta = $case.text; variante = "qlora" } | ConvertTo-Json
        $result = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/generate" `
            -ContentType "application/json" -Body $body -TimeoutSec 240
        $inferences += [ordered]@{
            case = $case.id
            sql = $result.sql
            latency_ms = $result.latency_ms
            variant = $result.variante
        }
    }
    $checks.synthetic_inferences = $inferences
}

$report = [ordered]@{
    verified_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    commit = $state.commit
    checks = $checks
}
$ReportPath = Join-Path $RunDirectory "verification.json"
$report | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 -LiteralPath $ReportPath
$report | ConvertTo-Json -Depth 8
Write-Host "Resultado guardado en $ReportPath"
