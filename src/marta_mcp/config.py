"""API key resolution for the MARTA rail real-time API.

The key is looked up in this order:
1. The MARTA_API_KEY environment variable.
2. ~/.marta/config.json  ->  {"api_key": "..."}

The config file lives in the home directory so the key never has to appear
in a client config, the repository, or a packaged extension.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".marta"
CONFIG_PATH = CONFIG_DIR / "config.json"


class MartaConfigError(RuntimeError):
    pass


def get_api_key() -> str:
    key = os.environ.get("MARTA_API_KEY", "").strip()
    if key:
        return key

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError) as exc:
            raise MartaConfigError(
                f"Could not read {CONFIG_PATH}: {exc}"
            ) from exc
        key = str(data.get("api_key") or "").strip()
        if key:
            return key

    raise MartaConfigError(
        "No MARTA API key found. Either set the MARTA_API_KEY environment "
        f"variable or run: marta-mcp-config <your-api-key> (writes {CONFIG_PATH}). "
        "Register for a key at https://www.itsmarta.com/developer-reg-rtt.aspx"
    )


def save_api_key(key: str) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError):
            data = {}
    data["api_key"] = key.strip()
    CONFIG_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        CONFIG_PATH.chmod(0o600)
    return CONFIG_PATH


def cli() -> None:
    """Console entry point: marta-mcp-config <api-key>"""
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: marta-mcp-config <api-key>")
        print(f"Stores the MARTA API key in {CONFIG_PATH}")
        raise SystemExit(0 if len(sys.argv) == 2 else 1)
    path = save_api_key(sys.argv[1])
    print(f"API key saved to {path}")
