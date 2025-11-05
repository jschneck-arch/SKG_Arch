#!/usr/bin/env python3
from skg.peer import export_manifest
from skg.ethics import check
def run(**params):
    check("peer","export_manifest")
    path = params.get("path","/opt/skg/manifest.json")
    return export_manifest(path)
