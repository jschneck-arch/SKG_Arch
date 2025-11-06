from skg.config.api_port import load
host, port = load()

#!/usr/bin/env python3
import subprocess, sys
print("[SKG-API] Binding exclusively to {host}:{port}"); sys.stdout.flush()
subprocess.run([
    "/opt/skg/.venv/bin/python","-m","uvicorn",
    "skg.interface.api:app","--host","127.0.0.1","--port","5056","--no-server-header"
])
