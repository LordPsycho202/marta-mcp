#!/usr/bin/env bash
# Build the Claude Desktop extension (.dxt / .mcpb) for marta-mcp.
#
# The extension is a thin manifest-only bundle (like garmin_mcp): Claude
# Desktop launches the server with `uvx --from git+<repo>`, which fetches
# the package and its dependencies on first run. Users need uv installed.
#
# Requires: node (npx). Run from the repo root: bash scripts/build_dxt.sh
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
staging="$root/build/dxt"
dist="$root/dist"

rm -rf "$staging"
mkdir -p "$staging" "$dist"

cp "$root/manifest.json" "$staging/"

# Pack with Anthropic's bundler (MCPB is the successor to DXT; Claude
# Desktop accepts both). Produce both file extensions for convenience.
npx --yes @anthropic-ai/mcpb pack "$staging" "$dist/marta-mcp.mcpb"
cp "$dist/marta-mcp.mcpb" "$dist/marta-mcp.dxt"

echo "Built: $dist/marta-mcp.mcpb and $dist/marta-mcp.dxt"
