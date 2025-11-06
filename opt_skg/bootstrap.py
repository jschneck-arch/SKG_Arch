# Always importable very early
import sys, os
if "/opt/skg" not in sys.path:
    sys.path.insert(0, "/opt/skg")
