#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON:-python3}"

if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

./.venv/bin/python -m pip install -e ".[dev]"

if [ ! -f "config.local.toml" ]; then
  cp config.example.toml config.local.toml
  echo "Created config.local.toml from config.example.toml"
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

mkdir -p secrets

./.venv/bin/python -m canvas_download.bootstrap --config config.local.toml

echo "Setup complete."
echo "Next: edit .env and config.local.toml for your Canvas instance."
