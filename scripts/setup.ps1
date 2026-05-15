$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python -m pip install -e ".[dev]"

Write-Host "Setup complete. Next: copy config.example.toml to config.local.toml and .env.example to .env."
