# Build the Claude Desktop extension (.dxt / .mcpb) for marta-mcp.
# Requires: uv, node (npx). Run from the repo root:
#   powershell -ExecutionPolicy Bypass -File scripts\build_dxt.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$staging = Join-Path $root "build\dxt"
$dist = Join-Path $root "dist"

if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Force "$staging\server" | Out-Null
New-Item -ItemType Directory -Force $dist | Out-Null

Copy-Item (Join-Path $root "manifest.json") $staging
Copy-Item (Join-Path $root "scripts\dxt_main.py") "$staging\server\main.py"

# Bundle marta_mcp and its dependencies into server/lib
uv pip install --target "$staging\server\lib" $root
if ($LASTEXITCODE -ne 0) { throw "uv pip install failed" }

# Pack with Anthropic's bundler (MCPB is the successor to DXT; Claude
# Desktop accepts both). Produce both file extensions for convenience.
npx --yes @anthropic-ai/mcpb pack $staging (Join-Path $dist "marta-mcp.mcpb")
if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed" }
Copy-Item (Join-Path $dist "marta-mcp.mcpb") (Join-Path $dist "marta-mcp.dxt") -Force

Write-Host "Built: $dist\marta-mcp.mcpb and $dist\marta-mcp.dxt"
