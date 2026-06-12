# Build the Claude Desktop extension (.dxt / .mcpb) for marta-mcp.
#
# The extension is a thin manifest-only bundle (like garmin_mcp): Claude
# Desktop launches the server with `uvx --from git+<repo>`, which fetches
# the package and its dependencies on first run. Users need uv installed.
#
# Requires: node (npx). Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\build_dxt.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$staging = Join-Path $root "build\dxt"
$dist = Join-Path $root "dist"

if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Force $staging | Out-Null
New-Item -ItemType Directory -Force $dist | Out-Null

Copy-Item (Join-Path $root "manifest.json") $staging

# Pack with Anthropic's bundler (MCPB is the successor to DXT; Claude
# Desktop accepts both). Produce both file extensions for convenience.
npx --yes @anthropic-ai/mcpb pack $staging (Join-Path $dist "marta-mcp.mcpb")
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed" }
Copy-Item (Join-Path $dist "marta-mcp.mcpb") (Join-Path $dist "marta-mcp.dxt") -Force

Write-Host "Built: $dist\marta-mcp.mcpb and $dist\marta-mcp.dxt"
