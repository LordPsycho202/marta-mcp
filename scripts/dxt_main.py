"""Entry point used inside the packaged .dxt/.mcpb extension.

Bundled dependencies live in ./lib next to this file; put them on sys.path
before importing the server. Pure-python protobuf is forced so the bundle
does not depend on a platform-specific native extension.
"""

import os
import sys

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from marta_mcp.server import main

main()
