$ErrorActionPreference = "Stop"

$root = Join-Path $PSScriptRoot ".."
$backendScript = Join-Path $PSScriptRoot "start-backend.ps1"

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript -WorkingDirectory $root

for ($tentativa = 1; $tentativa -le 60; $tentativa++) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1
        if ($health.status -eq "ok") { break }
    } catch {
        if ($tentativa -eq 60) {
            throw "A API não iniciou em 60 segundos. Confira a janela do back-end para ver o erro."
        }
        Start-Sleep -Seconds 1
    }
}

& (Join-Path $PSScriptRoot "start-frontend.ps1")
