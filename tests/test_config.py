from pathlib import Path

from canvas_download.config import CanvasConfig, load_config


def test_canvas_config_rejects_token_value_in_token_env() -> None:
    config = CanvasConfig(base_url="https://canvas.example.edu", token_env="123~not-an-env-var")

    try:
        config.token()
    except ValueError as exc:
        assert "canvas.token_env should be an environment variable name" in str(exc)
    else:
        raise AssertionError("Expected token_env validation error")


def test_canvas_config_accepts_local_token_value() -> None:
    config = CanvasConfig(
        base_url="https://canvas.example.edu",
        token_env="123~not-an-env-var",
        token_value="real-token",
    )

    assert config.token() == "real-token"


def test_load_config_reads_download_workers(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[canvas]
base_url = "https://canvas.example.edu"

[archive]
root = "~/CanvasArchive"
year = "2026"
semester = "Spring"
download_workers = 10
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.archive.download_workers == 10


def test_load_config_expands_home_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[canvas]
base_url = "https://canvas.example.edu"

[archive]
root = "~/CanvasArchive"
year = "2026"
semester = "Spring"

[google_drive]
credentials_file = "~/canvas-backup/secrets/google-client-secret.json"
token_file = "~/canvas-backup/secrets/google-token.json"
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert str(config.archive.root).startswith(str(Path.home()))
    assert str(config.google_drive.credentials_file).startswith(str(Path.home()))
    assert str(config.google_drive.token_file).startswith(str(Path.home()))
