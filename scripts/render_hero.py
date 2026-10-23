#!/usr/bin/env python3
"""Render a static hero frame of the Vector Hoops 3D embedding atlas.

Source data: ~/workspace/vector-hoops assets/projections/embed3d.json (master)
- 12,966 NBA player-seasons, PCA 3D coordinates of the served 64-d MTNN v5
  embeddings, kmeans k=8 clusters (STATED in the file's own meta, not eyeballed).
- Rotation is fixed (az ~ -25deg, tilt ~ 15deg), perspective projection.
- Colors: Okabe-Ito CVD-safe palette (same as hoops' embed3d.js); the
  black-swatch cluster is rendered as moss gray so it reads on the dark board.
- Axes are arbitrary units -- no axis labels drawn (binding honesty rule).

Output: hero-atlas.png, night-board dark (#0C110D), 1600x900.
"""
import json, math, sys
from PIL import Image, ImageDraw

SRC = "/tmp/embed3d.json"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hero-atlas.png"
W, H = 1600, 900
BG = (12, 17, 13)  # night-board void

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
           "#56B4E9", "#E69F00", "#8A9A8B", "#F0E442"]  # c6 -> moss (was black)

def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

pal = [hexrgb(c) for c in PALETTE]

def main():
    d = json.load(open(SRC))
    pts = [(p["pca"], p["c"]) for p in d["points"]]
    assert len(pts) == 12966, f"expected 12966 points, got {len(pts)}"
    xs = [p[0][0] for p in pts]; ys = [p[0][1] for p in pts]; zs = [p[0][2] for p in pts]
    cx, cy, cz = sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)

    az, tilt = math.radians(-25), math.radians(15)
    ca, sa, ct, st = math.cos(az), math.sin(az), math.cos(tilt), math.sin(tilt)

    proj = []
    for (x, y, z), c in pts:
        x, y, z = x - cx, y - cy, z - cz
        x1 = x * ca - z * sa
        z1 = x * sa + z * ca
        y1 = y * ct - z1 * st
        z2 = y * st + z1 * ct
        proj.append((x1, y1, z2, c))

    zs2 = [p[2] for p in proj]
    zmin, zmax = min(zs2), max(zs2)
    f = (zmax - zmin) * 1.6

    img = Image.new("RGBA", (W, H), BG + (255,))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)

    # far -> near so near points paint on top
    proj.sort(key=lambda p: p[2])
    span = max(x for x, _, _, _ in proj) - min(x for x, _, _, _ in proj)
    span_y = max(y for _, y, _, _ in proj) - min(y for _, y, _, _ in proj)
    scale = min(W * 0.92 / span, H * 0.92 / span_y)

    for x, y, z, c in proj:
        t = (z - zmin) / (zmax - zmin)  # 0 far, 1 near
        s = f / (f + (z - (zmin + zmax) / 2))
        px = W / 2 + x * scale * s
        py = H / 2 - y * scale * s
        r = 1.2 + 2.2 * t
        alpha = int(70 + 150 * t)
        col = pal[c % 8] + (alpha,)
        dr.ellipse([px - r, py - r, px + r, py + r], fill=col)

    img = Image.alpha_composite(img, lay).convert("RGB")
    img.save(OUT, optimize=True)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
