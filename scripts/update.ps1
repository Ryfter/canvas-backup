$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Push-Location $ProjectRoot

try {
    if (-not (Test-Path ".git")) {
        throw "This folder is not a Git clone. Download the latest ZIP from GitHub or clone https://github.com/Ryfter/canvas-backup.git."
    }

    Write-Host "Checking for local changes..."
    $Status = git status --porcelain
    if ($Status) {
        Write-Host "Local changes were found. Commit, stash, or remove them before updating:"
        git status --short
        throw "Update stopped so local changes are not overwritten."
    }

    Write-Host "Pulling latest changes from GitHub..."
    git pull --ff-only

    Write-Host "Refreshing local setup..."
    & (Join-Path $ProjectRoot "scripts\setup.ps1")

    Write-Host "Update complete."
}
finally {
    Pop-Location
}
