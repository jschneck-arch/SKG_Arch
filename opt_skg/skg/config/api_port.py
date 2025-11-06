from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5056

def load():
    """
    Read /opt/skg/etc/api_port.conf if it exists.
    Returns (host, port).
    """
    conf = Path("/opt/skg/etc/api_port.conf")
    if not conf.exists():
        return DEFAULT_HOST, DEFAULT_PORT

    host, port = DEFAULT_HOST, DEFAULT_PORT
    for line in conf.read_text().splitlines():
        if "=" not in line:
            continue
        k, v = line.strip().split("=", 1)
        if k == "API_HOST":
            host = v
        elif k == "API_PORT":
            try:
                port = int(v)
            except ValueError:
                pass
    return host, port
