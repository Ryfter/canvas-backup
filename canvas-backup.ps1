$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ProjectRoot

try {
    $Command = Join-Path $ProjectRoot ".venv\Scripts\canvas-backup.exe"
    if (-not (Test-Path $Command)) {
        Write-Host "Canvas Backup is not installed yet. Running setup..."
        & (Join-Path $ProjectRoot "scripts\setup.ps1")
    }

    if (-not (Test-Path $Command)) {
        throw "Could not find $Command after setup."
    }

    & $Command @args
    if ($LASTEXITCODE -ne 0) {
        throw "Canvas Backup exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
