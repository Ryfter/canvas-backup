# Development

## Install

Windows PowerShell:

```powershell
.\scripts\setup.ps1
```

macOS/Linux:

```bash
chmod +x scripts/setup.sh scripts/test.sh
./scripts/setup.sh
```

## Run Tests

Windows PowerShell:

```powershell
.\scripts\test.ps1
```

macOS/Linux:

```bash
./scripts/test.sh
```

## Project Layout

```text
src/canvas_download/
  archive.py            Local archive writer
  bootstrap.py          First-run local folder creator
  canvas_client.py      Canvas REST API client
  cli.py                Command-line interface
  config.py             TOML and environment config
  course_selection.py   Bulk archive target inference and chooser parsing
  dedupe.py             Exact duplicate downloaded file cleanup
  drive.py              Google Drive sync
  filesystem.py         Safe filenames and path guards
  json_io.py            JSON/text file helpers
tests/
  test_*.py
docs/
```

## Release Checklist

Before publishing changes:

```text
Run the test script for your operating system.
git status --short
```

Confirm these files are not staged:

- `.env`
- `config.local.toml`
- `secrets/google-client-secret.json`
- `secrets/google-token.json`
- `.venv/`

## Design Principles

- Local archive is canonical.
- Google Drive sync mirrors the local archive.
- Reruns should be safe.
- Secrets must stay out of Git.
- Course selection must be explicit when the instructor has access to unrelated shells.

## AI-Assisted Build Notes

For a nontechnical explanation of how this project was created, see:

- [How Canvas Backup Was Created With AI](ai-build-workflow.md)
- [Prompt Playbook](prompt-playbook.md)
