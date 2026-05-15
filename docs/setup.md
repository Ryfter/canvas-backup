# Setup Guide

This guide walks through a first-time setup for Windows, macOS, and Linux.

## 1. Install Prerequisites

Install:

- Python 3.11 or newer.
- Git.

Confirm Python is available:

Windows PowerShell:

```powershell
python --version
```

macOS/Linux:

```bash
python3 --version
```

## 2. Download The Project

Clone the repository:

```bash
git clone https://github.com/Ryfter/canvas-backup.git
cd canvas-backup
```

If you downloaded a ZIP file from GitHub instead, unzip it and open a terminal in the `canvas-backup` folder.

## 3. Run Setup

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

If PowerShell blocks scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```

macOS/Linux:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script creates:

- `.venv/`
- `config.local.toml`
- `.env`
- `secrets/`
- The archive folder named in `config.local.toml`
- Parent folders for the Google credential and token files

It also installs Canvas Backup into the virtual environment.

After setup, use the launcher in the project folder. You do not need to find or run anything inside `.venv`.

## 4. Add Your Canvas Token

Edit `.env`:

```env
CANVAS_TOKEN=your-canvas-token
```

See [Configuration](configuration.md) for details.

## 5. Set Your Canvas URL

Edit `config.local.toml`:

```toml
[canvas]
base_url = "https://your-school.instructure.com"
token_env = "CANVAS_TOKEN"
```

The default archive folder is:

```toml
[archive]
root = "~/CanvasArchive"
```

The `~` means your user home folder, so this works on Windows, macOS, and Linux.

## 6. Test Canvas Access

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml courses
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml courses
```

If this lists your courses, Canvas access is working.

## 7. Preview A Bulk Archive

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose --dry-run
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose --dry-run
```

This lists matching course shells and lets you practice the selection step without downloading.

## 8. Download Selected Shells

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose
```

After each shell downloads, duplicate files are checked and removed automatically.

## 9. Optional: Set Up Google Drive

Follow [Google Drive Setup](google-drive.md), then run the same archive command with `--sync-drive`.
