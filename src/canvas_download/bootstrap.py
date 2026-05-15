from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

from canvas_download.config import load_config


ProgressCallback = Callable[[str], None]


def ensure_local_paths(config_path: Path, progress: ProgressCallback | None = None) -> list[Path]:
    config = load_config(config_path)
    paths = [config.archive.root]

    if config.google_drive.credentials_file:
        paths.append(config.google_drive.credentials_file.parent)
    if config.google_drive.token_file:
        paths.append(config.google_drive.token_file.parent)

    ensured: list[Path] = []
    for path in _unique_paths(paths):
        existed = path.exists()
        path.mkdir(parents=True, exist_ok=True)
        ensured.append(path)
        if progress:
            status = "Found" if existed else "Created"
            progress(f"{status}: {path}")

    return ensured


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m canvas_download.bootstrap",
        description="Create local folders referenced by a Canvas Backup config file.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.local.toml"),
        help="Path to a TOML config file. Default: config.local.toml",
    )
    args = parser.parse_args(argv)

    ensure_local_paths(args.config, progress=print)
    return 0


def _unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


if __name__ == "__main__":
    raise SystemExit(main())
