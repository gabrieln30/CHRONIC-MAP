$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..\\frontend")
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "Node.js LTS (incluindo npm) não foi encontrado. Instale-o e execute este script novamente."
}

if (-not (Test-Path "node_modules")) {
    npm ci
}

$env:API_PROXY_TARGET = "http://localhost:8000"
npm run dev
