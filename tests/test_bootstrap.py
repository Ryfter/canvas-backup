from pathlib import Path

from canvas_download.bootstrap import ensure_local_paths


def test_ensure_local_paths_creates_archive_and_google_parent_dirs(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    archive_root = tmp_path / "archive-root"
    credentials_file = tmp_path / "nested" / "secrets" / "google-client-secret.json"
    token_file = tmp_path / "nested" / "secrets" / "google-token.json"
    messages: list[str] = []

    config_path.write_text(
        f"""
[canvas]
base_url = "https://canvas.example.edu"

[archive]
root = "{archive_root.as_posix()}"
year = "2026"
semester = "Spring"

[google_drive]
credentials_file = "{credentials_file.as_posix()}"
token_file = "{token_file.as_posix()}"
""",
        encoding="utf-8",
    )

    ensured = ensure_local_paths(config_path, progress=messages.append)

    assert archive_root.is_dir()
    assert credentials_file.parent.is_dir()
    assert token_file.parent.is_dir()
    assert ensured == [archive_root, credentials_file.parent]
    assert f"Created: {archive_root}" in messages
    assert f"Created: {credentials_file.parent}" in messages
