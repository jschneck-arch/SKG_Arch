from skg.telemetry_bus import upsert
def publish_adaptive(entropy_avg, amp, freq):
    return upsert("expressor",{"entropy_avg":entropy_avg,"amp":amp,"freq":freq})
