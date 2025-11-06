#!/usr/bin/env python3
"""
SKG Field Hybrid Renderer
- inner quantum “string of pearls” (pearls.jsonl)
- outer spherical waveform field (CPU/MEM/NET)
- live service HUD (systemctl is-active)
- frame sequence emission for time-lapse analysis

Config (env):
  SKG_FRAMES=1                enable frame emission (default 1)
  SKG_FRAME_EVERY=4           emit every N renders (default 4)
  SKG_FRAME_DIR=/opt/skg/telemetry/frames
"""

import json, math, time, random, os, psutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TELEM   = Path("/var/lib/skg/memory/telemetry.json")
PEARLS  = Path("/var/lib/skg/memory/pearls.jsonl")
OUTDIR  = Path("/opt/skg/telemetry"); OUTDIR.mkdir(parents=True, exist_ok=True)
W, H    = 1280, 720
FONT    = ImageFont.load_default()

FRAMES_ON     = int(os.getenv("SKG_FRAMES", "1")) == 1
FRAME_EVERY   = int(os.getenv("SKG_FRAME_EVERY", "4"))
FRAME_ROOT    = Path(os.getenv("SKG_FRAME_DIR", "/opt/skg/telemetry/frames"))

def get_services():
    names = ["skg-core-v4.service","skg-api.service","skg-brain.service","skg-field.service","skg-integrator.service","skg-coder.service"]
    states = {}
    for n in names:
        try:
            s = subprocess.run(["systemctl","is-active",n], capture_output=True, text=True, timeout=1)
            states[n.replace('.service','')] = s.stdout.strip()
        except Exception:
            states[n] = "unknown"
    return states

def load_pearls(limit=240):
    if not PEARLS.exists(): return []
    pearls=[]
    with PEARLS.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try: pearls.append(json.loads(line))
            except: pass
    return pearls[-limit:]

def draw_frame():
    img = Image.new("RGB",(W,H),(4,6,12))
    draw = ImageDraw.Draw(img)

    # outer waveform field (spherical-ish)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    amp = 40 + cpu/2
    for a in range(0,360,3):
        r = 240 + math.sin(math.radians(a*4)+time.time()*0.9)*amp
        x = W//2 + math.cos(math.radians(a))*r
        y = H//2 + math.sin(math.radians(a))*r
        col = (min(255,int(60+mem*1.4)), min(255,int(40+cpu*1.6)), 200)
        draw.point((x,y),fill=col)

    # inner pearls (quantum nucleus)
    pearls = load_pearls()
    t = time.time()
    for i,p in enumerate(pearls):
        ang = i*0.33 + t/5.0
        r = 16 + i*1.4
        x = W//2 + math.cos(ang)*r
        y = H//2 + math.sin(ang)*r
        size = 2 + (i % 3)
        draw.ellipse((x-size,y-size,x+size,y+size),fill=(175,175,255))

    # telemetry HUD
    draw.rectangle((8,8,350,8+88), fill=(0,0,0,0))
    net=psutil.net_io_counters()
    hud = [
        f"CPU {cpu:5.1f}%  MEM {mem:5.1f}%",
        f"NET sent {net.bytes_sent//1024}k recv {net.bytes_recv//1024}k",
    ]
    ytxt=14
    for line in hud:
        draw.text((14, ytxt), line, fill=(230,232,238), font=FONT); ytxt+=14

    ytxt+=4
    for name,state in get_services().items():
        good = (state=="active")
        color = (200,230,210) if good else (240,120,120)
        draw.text((14, ytxt), f"{name:<12}: {state}", fill=color, font=FONT); ytxt+=14

    # save current PNG for wallpaper/panel
    (OUTDIR/"field_hybrid.png").write_bytes(img.tobytes())  # fast? No—fallback below.
    img.save(OUTDIR/"field_hybrid.png","PNG")
    return img

def ensure_day_dir(root: Path) -> Path:
    d = root / time.strftime("%Y%m%d")
    d.mkdir(parents=True, exist_ok=True)
    return d

def main():
    frame_i = 0
    while True:
        try:
            img = draw_frame()
            frame_i += 1
            if FRAMES_ON and frame_i % FRAME_EVERY == 0:
                daydir = ensure_day_dir(FRAME_ROOT)
                ts = time.strftime("%H%M%S")
                img.save(daydir / f"frame_{ts}.png", "PNG")
        except Exception:
            pass
        time.sleep(0.5)

if __name__=="__main__":
    main()
