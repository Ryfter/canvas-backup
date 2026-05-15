# Setup Guide

This guide walks through a first-time setup on Windows PowerShell.

## 1. Install Prerequisites

Install Python 3.11 or newer.

Confirm Python is available:

```powershell
python --version
```

## 2. Install The Project

From the project folder:

```powershell
cd D:\Dev\canvas-backup
.\scripts\setup.ps1
```

The setup script creates `.venv` and installs the package in editable mode.

If PowerShell blocks scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\setup.ps1
```

## 3. Create Local Config Files

```powershell
Copy-Item config.example.toml config.local.toml
Copy-Item .env.example .env
```

Both `.env` and `config.local.toml` are ignored by Git.

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

Use your institution's Canvas domain.

## 6. Test Canvas Access

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml courses
```

If this lists your courses, Canvas access is working.

## 7. Preview A Bulk Archive

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --dry-run
```

This lists matching course shells and lets you practice the selection step without downloading.

## 8. Download Selected Shells

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose
```

## 9. Optional: Set Up Google Drive

Follow [Google Drive Setup](google-drive.md), then run:

```powershell
.\.venv\Scripts\canvas-backup --config config.local.toml archive-recent --years 4 --choose --sync-drive
```
