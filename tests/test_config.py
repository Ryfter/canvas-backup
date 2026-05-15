from canvas_download.config import CanvasConfig


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
