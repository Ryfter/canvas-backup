#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -d ".git" ]; then
  echo "This folder is not a Git clone. Download the latest ZIP from GitHub or clone https://github.com/Ryfter/canvas-backup.git." >&2
  exit 1
fi

echo "Checking for local changes..."
if [ -n "$(git status --porcelain)" ]; then
  echo "Local changes were found. Commit, stash, or remove them before updating:" >&2
  git status --short >&2
  echo "Update stopped so local changes are not overwritten." >&2
  exit 1
fi

echo "Pulling latest changes from GitHub..."
git pull --ff-only

echo "Refreshing local setup..."
"$PROJECT_ROOT/scripts/setup.sh"

echo "Update complete."
