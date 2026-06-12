# marta-mcp

An [MCP](https://modelcontextprotocol.io) server for Atlanta **MARTA** real-time
transit data. Ask Claude things like *"When's the next northbound Red Line train
at Midtown?"* or *"Where are the buses on route 110 right now?"*

## Tools

| Tool | Data source | API key? |
|---|---|---|
| `get_rail_arrivals` | Rail real-time RESTful API — arrival predictions for every station, filterable by station / line / direction | Yes |
| `list_rail_stations` | Static — canonical station names | No |
| `get_bus_positions` | GTFS-realtime vehicle positions feed (protobuf) | No |
| `get_bus_trip_updates` | GTFS-realtime trip updates feed (protobuf) | No |

## API key setup

Rail data requires a free MARTA API key —
[register here](https://www.itsmarta.com/developer-reg-rtt.aspx).

The key is **never stored in this project or in your MCP client config**. The
server reads it from, in order:

1. The `MARTA_API_KEY` environment variable
2. `~/.marta/config.json`:

   ```json
   { "api_key": "your-key-here" }
   ```

The easiest way to create the config file:

```bash
uvx --from git+https://github.com/rnissen/marta-mcp marta-mcp-config <your-key>
```

## Installation

### Option 1 — Claude Desktop extension (one-click)

Build (or download) `marta-mcp.dxt` / `marta-mcp.mcpb` and double-click it, or
drag it into Claude Desktop's **Settings → Extensions**. No JSON editing needed.

Build it yourself (requires `uv` and Node.js):

```bash
bash scripts/build_dxt.sh          # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts\build_dxt.ps1   # Windows
```

Output lands in `dist/`. Note: the bundle includes Python dependencies
installed on the build machine, so build it on the same OS you'll run it on.

### Option 2 — uvx straight from GitHub

Add to your MCP client config (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "marta": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rnissen/marta-mcp", "marta-mcp"]
    }
  }
}
```

### Option 3 — local clone

```bash
git clone https://github.com/rnissen/marta-mcp
cd marta-mcp
uv run marta-mcp
```

## Development

```bash
uv sync
uv run pytest          # live smoke tests against MARTA's APIs
```

## Notes

- Bus `route_id` values are MARTA's internal GTFS identifiers, which don't
  always match the public route numbers. Pair this server with MARTA's
  [static GTFS feed](https://itsmarta.com/app-developer-resources.aspx) if you
  need the mapping.
- This project is not affiliated with or endorsed by MARTA. MARTA's marks may
  not be used without written authorization.

## License

MIT
