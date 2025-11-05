import sys; sys.path.append('/opt/skg')
def run():
    from datetime import datetime
    return {"reflection": f"Reflective ping at {datetime.utcnow().isoformat()}"}
