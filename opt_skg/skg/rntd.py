#!/usr/bin/env python3
"""
RNTD: Resonant Network Topology daemon
- Broadcasts SKG resonance pulses over UDP
- Listens for peers, verifies HMAC, updates peer table
- Stores lightweight consensus and phase alignment scores
"""
import json, socket, threading, time, hmac, hashlib, os
from pathlib import Path

CONF = "/etc/skg/rnt.conf"
KEYF = "/etc/skg/rnt.key"
TEL  = Path("/var/lib/skg/state/telemetry.json")
REMJ = Path("/var/lib/skg/state/rem.json")
PEERS_STATE = Path("/var/lib/skg/state/rnt_peers.json")
CONSENSUS   = Path("/var/lib/skg/state/rnt_consensus.json")

def load_json(p, d=None):
    try: return json.load(open(p))
    except: return {} if d is None else d

def read_key():
    with open(KEYF,'rb') as f: return f.read().strip()

def sign(payload:bytes, key:bytes)->str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()

def now(): return time.time()

class RNT:
    def __init__(self):
        self.cfg = load_json(CONF, {})
        self.secret = read_key()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.cfg.get("listen","0.0.0.0"), int(self.cfg.get("port",49777))))
        self.peers = {}
        self.backlog = int(self.cfg.get("receive_backlog",200))
        self.id = self.cfg.get("id","skg-node")
        self.send_interval = int(self.cfg.get("send_interval_s",15))
        self._stop = False

    def pulse(self):
        tel = load_json(TEL, {})
        rem = load_json(REMJ, {})
        msg = {
            "ts": now(),
            "id": self.id,
            "entropy": tel.get("entropy"),
            "ethics": tel.get("ethics_coherence"),
            "cpu": tel.get("cpu_percent"),
            "phase": load_json("/var/lib/skg/state/lifecycle.json",{}).get("phase","reflection"),
            "sleep": rem.get("sleep_interval"),
        }
        body = json.dumps(msg, separators=(",",":")).encode()
        mac = sign(body, self.secret)
        pkt = json.dumps({"msg":msg,"mac":mac}).encode()
        for p in self.cfg.get("peers", []):
            try: self.sock.sendto(pkt, (p["host"], int(p["port"])))
            except: pass

    def verify_and_store(self, pkt:bytes):
        try:
            obj = json.loads(pkt.decode())
            body = json.dumps(obj["msg"], separators=(",",":")).encode()
            mac_ok = (sign(body, self.secret) == obj.get("mac"))
            if not mac_ok: return
            m = obj["msg"]; pid=m["id"]
            self.peers.setdefault(pid, [])
            self.peers[pid].append(m)
            if len(self.peers[pid])>self.backlog: self.peers[pid]=self.peers[pid][-self.backlog:]
            # write latest view
            PEERS_STATE.parent.mkdir(parents=True, exist_ok=True)
            json.dump({"ts":now(),"peers":{k:v[-1] for k,v in self.peers.items()}}, open(PEERS_STATE,"w"), indent=2)
            self._update_consensus()
        except Exception:
            pass

    def _update_consensus(self):
        # toy consensus: median entropy and mean ethics across latest pulses (self + peers)
        latest = [load_json(TEL, {})]
        latest.extend([v[-1] for v in self.peers.values() if v])
        ent = [x.get("entropy") for x in latest if x.get("entropy") is not None]
        eth = [x.get("ethics") for x in latest if x.get("ethics") is not None]
        c = {
            "ts": now(),
            "nodes": len(latest),
            "entropy_median": sorted(ent)[len(ent)//2] if ent else None,
            "ethics_mean": round(sum(eth)/len(eth),3) if eth else None
        }
        json.dump(c, open(CONSENSUS,"w"), indent=2)

    def recv_loop(self):
        while not self._stop:
            try:
                pkt,_ = self.sock.recvfrom(8192)
                self.verify_and_store(pkt)
            except Exception:
                time.sleep(0.1)

    def send_loop(self):
        while not self._stop:
            self.pulse()
            time.sleep(self.send_interval)

    def run(self):
        threading.Thread(target=self.recv_loop, daemon=True).start()
        self.send_loop()

if __name__=="__main__":
    RNT().run()
