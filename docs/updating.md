# Updating Canvas Backup

Use this guide when Canvas Backup has already been installed and you want the newest changes from GitHub.

## Recommended Update Path

Run the update script from the `canvas-backup` project folder.

Windows PowerShell:

```powershell
.\scripts\update.ps1
```

macOS/Linux:

```bash
chmod +x scripts/update.sh
./scripts/update.sh
```

The update script:

- Confirms the folder is a Git clone.
- Stops if local uncommitted changes exist.
- Pulls the newest version from GitHub with `git pull --ff-only`.
- Refreshes the local `.venv` install.
- Recreates any missing local folders from `config.local.toml`.

Your local files are preserved:

- `.env`
- `config.local.toml`
- `secrets/`
- Local archive folders

## If You Downloaded A ZIP

The update script only works in a Git clone.

If you downloaded a ZIP file from GitHub, download the newest ZIP again and move your local files into the new folder:

- `.env`
- `config.local.toml`
- `secrets/`

Do not move `.venv`. Run setup again in the new folder.

## If You Make Code Changes Yourself

Canvas Backup is installed in editable mode during setup:

```text
python -m pip install -e ".[dev]"
```

That means most changes under `src/canvas_download/` show up the next time you run the launcher.

You should rerun setup or refresh the editable install when:

- Dependencies change in `pyproject.toml`.
- Console script names change in `pyproject.toml`.
- Setup scripts change.
- You switch branches or pull a larger update.

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

macOS/Linux:

```bash
./scripts/setup.sh
```

## If Update Stops Because Of Local Changes

The script stops when it sees uncommitted local changes. This protects local work from being overwritten.

For most professors, the best path is to ask for help before continuing.

For technical users, common options are:

Windows PowerShell:

```powershell
git status --short
git stash push -m "local canvas-backup changes"
.\scripts\update.ps1
```

macOS/Linux:

```bash
git status --short
git stash push -m "local canvas-backup changes"
./scripts/update.sh
```

After updating, reapply the saved changes only if you still need them:

```bash
git stash pop
```

## Verify The Update

Check the current version of the command:

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --help
```

macOS/Linux:

```bash
./canvas-backup.sh --help
```

Then run a safe preview:

Windows PowerShell:

```powershell
.\canvas-backup.ps1 --config config.local.toml archive-recent --years 4 --choose --dry-run
```

macOS/Linux:

```bash
./canvas-backup.sh --config config.local.toml archive-recent --years 4 --choose --dry-run
```
