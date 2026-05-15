$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $ProjectRoot

try {
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }

    .\.venv\Scripts\python -m pip install -e ".[dev]"

    if (-not (Test-Path "config.local.toml")) {
        Copy-Item config.example.toml config.local.toml
        Write-Host "Created config.local.toml from config.example.toml"
    }

    if (-not (Test-Path ".env")) {
        Copy-Item .env.example .env
        Write-Host "Created .env from .env.example"
    }

    if (-not (Test-Path "secrets")) {
        New-Item -ItemType Directory -Force secrets | Out-Null
        Write-Host "Created secrets folder"
    }

    .\.venv\Scripts\python -m canvas_download.bootstrap --config config.local.toml

    Write-Host "Setup complete."
    Write-Host "Next: edit .env and config.local.toml for your Canvas instance."
}
finally {
    Pop-Location
}
