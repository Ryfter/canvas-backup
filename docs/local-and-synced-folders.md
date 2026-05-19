# Local And Synced Folder Backups

Canvas Backup is designed to download course shells to a local folder first.

That local folder can be:

- A normal folder on your computer.
- An external drive.
- A network drive.
- A Google Drive Desktop folder.
- A Dropbox folder.
- A OneDrive folder.

The built-in Google Drive API upload is optional. Many instructors can skip it entirely by choosing a local archive folder that already syncs through Google Drive Desktop, Dropbox, or OneDrive.

## Recommended Default

For most professors, use a normal local folder:

```toml
[archive]
root = "~/CanvasArchive"
```

This creates:

```text
~/CanvasArchive/
  2026/
    Spring/
      Course Shell Name/
```

This is the simplest and least error-prone path.

## External Drive Example

Windows:

```toml
[archive]
root = "D:/CanvasArchive"
```

macOS:

```toml
[archive]
root = "/Volumes/BackupDrive/CanvasArchive"
```

Linux:

```toml
[archive]
root = "/mnt/backup/CanvasArchive"
```

## Google Drive Desktop Example

If Google Drive Desktop is installed, you can point the archive root to a synced local folder.

Windows example:

```toml
[archive]
root = "G:/My Drive/CanvasArchive"
```

Another common Windows layout:

```toml
[archive]
root = "C:/Users/YourName/My Drive/CanvasArchive"
```

macOS example:

```toml
[archive]
root = "/Users/YourName/Library/CloudStorage/GoogleDrive-your.email@example.com/My Drive/CanvasArchive"
```

The exact path depends on how Google Drive Desktop is configured.

## Dropbox Example

Windows:

```toml
[archive]
root = "C:/Users/YourName/Dropbox/CanvasArchive"
```

macOS:

```toml
[archive]
root = "/Users/YourName/Dropbox/CanvasArchive"
```

## OneDrive Example

Windows:

```toml
[archive]
root = "C:/Users/YourName/OneDrive/CanvasArchive"
```

Institutional OneDrive folders may include the school name:

```toml
[archive]
root = "C:/Users/YourName/OneDrive - School Name/CanvasArchive"
```

## Important: Project Folder vs Archive Folder

Avoid putting the Canvas Backup project folder itself inside Dropbox, OneDrive, Google Drive Desktop, or iCloud Drive.

The project folder contains `.venv/`, `.git/`, scripts, and many small dependency files. Sync tools can lock, delay, or partially hydrate those files while setup is running.

Better:

```text
C:/Dev/canvas-backup              Project folder
C:/Users/YourName/Dropbox/CanvasArchive
```

or:

```text
C:/CanvasBackup/canvas-backup     Project folder
G:/My Drive/CanvasArchive         Archive folder
```

The archive folder can be synced. The project folder should stay in a normal local folder.

## When To Use Built-In Google Drive Sync

Use the built-in Google Drive API sync only if you want Canvas Backup to upload the completed archive directly to Google Drive.

That path requires:

- Google Cloud project setup.
- Google Drive API enabled.
- OAuth desktop app credentials.
- `secrets/google-client-secret.json`.
- A first-run Google authorization in the browser.

For many instructors, a synced local folder is easier than API setup.

## Command Behavior

This downloads locally only:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose
```

This downloads locally and then uploads through the Google Drive API:

```text
<canvas-backup> --config config.local.toml archive-recent --years 4 --choose --sync-drive
```

If your archive root is already inside Google Drive Desktop, Dropbox, or OneDrive, do not add `--sync-drive` unless you intentionally want both sync methods.
