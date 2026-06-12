#!/usr/bin/env bash
# Build the Claude Desktop extension (.dxt / .mcpb) for marta-mcp.
# Requires: uv, node (npx). Run from the repo root: bash scripts/build_dxt.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
staging="$root/build/dxt"
dist="$root/dist"

rm -rf "$staging"
mkdir -p "$staging/server" "$dist"

cp "$root/manifest.json" "$staging/"
cp "$root/scripts/dxt_main.py" "$staging/server/main.py"

# Bundle marta_mcp and its dependencies into server/lib
uv pip install --target "$staging/server/lib" "$root"

# Pack with Anthropic's bundler (MCPB is the successor to DXT; Claude
# Desktop accepts both). Produce both file extensions for convenience.
npx --yes @anthropic-ai/mcpb pack "$staging" "$dist/marta-mcp.mcpb"
cp "$dist/marta-mcp.mcpb" "$dist/marta-mcp.dxt"

echo "Built: $dist/marta-mcp.mcpb and $dist/marta-mcp.dxt"
