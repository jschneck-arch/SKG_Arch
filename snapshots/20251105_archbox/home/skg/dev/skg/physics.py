import math, time
PHASE_WEIGHTS={
 "Unified":dict(signal=1,novelty=1,caution=1),
 "Explore":dict(signal=0.8,novelty=1.3,caution=0.8),
 "Exploit":dict(signal=1.2,novelty=0.8,caution=1.1),
 "RealityAnchor":dict(signal=1,novelty=0.7,caution=1.3)}
def gravity_score(tele,phase="Unified"):
    p=PHASE_WEIGHTS.get(phase,PHASE_WEIGHTS["Unified"])
    s=tele.get("cpu",0)*p["signal"]
    n=(tele.get("port_variance",0)/100)*p["novelty"]
    c=(1 if tele.get("exfil") else 0.2)*p["caution"]
    return max(0,min(1,0.5*s+0.3*n+0.2*c))
class LFO:
    def __init__(self,amp=0.55,freq=0.0025,phi=0): self.amp, self.freq, self.phi, self.t0=float(amp),float(freq),float(phi),time.time()
    def value(self): t=time.time()-self.t0; return math.sin(2*math.pi*self.freq*t+self.phi)*self.amp
