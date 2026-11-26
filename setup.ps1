# Windows PowerShell: create the virtual environment and install core packages.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = if ($env:PYTHON) { $env:PYTHON } else { "py" }
& $python -3.11 -m venv .venv
if (-not $?) { & $python -m venv .venv }

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example - add your own OpenRouter key to enable AI responses."
}

Write-Host "Setup complete. Run: .\.venv\Scripts\python.exe scripts\preflight.py"
