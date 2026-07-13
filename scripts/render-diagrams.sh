#!/usr/bin/env bash
# Re-render docs/diagrams/*.mmd to PNG. Run after editing a .mmd source.
# Requires Node. Downloads mermaid-cli on first run.
set -euo pipefail

cd "$(dirname "$0")/.."

for src in docs/diagrams/*.mmd; do
  out="${src%.mmd}.png"
  echo "Rendering $src -> $out"
  npx -y @mermaid-js/mermaid-cli@11 -i "$src" -o "$out" -b white -s 3
done

echo "Done."
