#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

COMMAND="$PROJECT_ROOT/.venv/bin/canvas-backup"
if [ ! -x "$COMMAND" ]; then
  echo "Canvas Backup is not installed yet. Running setup..."
  "$PROJECT_ROOT/scripts/setup.sh"
fi

if [ ! -x "$COMMAND" ]; then
  echo "Could not find $COMMAND after setup." >&2
  exit 1
fi

exec "$COMMAND" "$@"
