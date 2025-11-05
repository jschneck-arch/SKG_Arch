#!/usr/bin/env python3
import json, math, time, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SRC = Path("/var/lib/skg/memory/telemetry.json")
OUTDIR = Path("/opt/skg/telemetry"); OUTDIR.mkdir(parents=True, exist_ok=True)
DEST = OUTDIR / "field.png"

W, H = 1920, 1080
CX, CY = W//2, H//2
FONT = None
try:
    FONT = ImageFont.load_default()
except Exception:
    FONT = None

angles = {}

def hex_to_rgb(hx: str) -> tuple[int,int,int]:
    hx = hx.replace("#","").strip()
    if len(hx) == 6:
        return tuple(int(hx[i:i+2], 16) for i in (0,2,4))
    return (136,170,255)

def beacon(draw, x, y, ok: bool, label: str):
    r = 8
    col = (80,200,120) if ok else (120,120,120)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=col, outline=(230,230,230))
    draw.text((x+12, y-6), label, fill=(210,210,210), font=FONT)

def recent(path: Path, secs: int=180) -> bool:
    try:
        return time.time() - path.stat().st_mtime < secs
    except Exception:
        return False

def render(tele):
    img = Image.new("RGB", (W, H), (8, 8, 16))
    d = ImageDraw.Draw(img)

    # subtle stripes
    for y in range(0, H, 8):
        shade = int(16 + 24*math.sin((y/H)*math.pi))
        d.line([(0,y),(W,y)], fill=(shade,shade,shade))

    phase = tele.get("phase","calm")
    theme = tele.get("theme","calm")
    cpu = float(tele.get("cpu",0.0)); mem = float(tele.get("mem",0.0))
    core_r = 60 + int(min(120, (cpu+mem)))
    d.ellipse((CX-core_r, CY-core_r, CX+core_r, CY+core_r), outline=(80,120,255), width=3)

    label = f"SKG phase: {phase}  theme: {theme}  CPU:{cpu:.0f}% MEM:{mem:.0f}%"
    d.text((20, 20), label, fill=(200,200,210), font=FONT)

    spheres = tele.get("spheres",{})
    for name, spec in spheres.items():
        e = float(spec.get("energy",0.0))
        col = hex_to_rgb(spec.get("color","#88aaff"))
        orbit = 140 + int(420*e)
        speed = 0.003 + (0.010 * e)
        a = angles.get(name, random.random()*math.tau); a += speed; angles[name] = a
        x = int(CX + math.cos(a) * orbit)
        y = int(CY + math.sin(a) * orbit)
        r = 18 + int(36*e)
        d.ellipse((CX-orbit, CY-orbit, CX+orbit, CY+orbit), outline=(40, 50, 80))
        d.ellipse((x-r, y-r, x+r, y+r), fill=col, outline=(220,220,230))
        d.text((x - r, y + r + 6), f"{name} {e:.2f}", fill=(210,210,210), font=FONT)

    # status beacons (top-right)
    integ = Path("/var/log/skg/integrator.log")
    coder = Path("/var/log/skg/coder.log")
    beacon(d, W-160, 28, recent(integ), "integrator")
    beacon(d, W-160, 52, recent(coder),  "coder")

    img.save(DEST, "PNG")

def main():
    last = ""
    while True:
        try:
            if SRC.exists():
                txt = SRC.read_text(encoding="utf-8")
                if txt and txt != last:
                    last = txt
                    tele = json.loads(txt)
                    render(tele)
        except Exception:
            pass
        time.sleep(1.5)

if __name__ == "__main__":
    main()
