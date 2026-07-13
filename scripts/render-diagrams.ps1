# Re-render docs/diagrams/*.mmd to PNG. Run after editing a .mmd source.
# Requires Node. Downloads mermaid-cli on first run.
$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

Get-ChildItem "docs/diagrams/*.mmd" | ForEach-Object {
    $out = $_.FullName -replace '\.mmd$', '.png'
    Write-Host "Rendering $($_.Name) -> $(Split-Path $out -Leaf)"
    npx -y @mermaid-js/mermaid-cli@11 -i $_.FullName -o $out -b white -s 3
}

Write-Host "Done."
