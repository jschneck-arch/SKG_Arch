from . import sysinfo, netinfo, procwatch
TOOLS = {
    "sysinfo": sysinfo.snapshot,
    "netinfo": netinfo.snapshot,
    "procwatch": procwatch.snapshot
}
