"""
hub_v04_dailySeed — same link = same stars • deterministic across devices
Formula (seed*1103515245+12345) & 0x7fffffff — glibc rand()
seed = YYYYMMDD UTC — examples 20260807 -> 11190772 -> idx 2512 pair 11804 triple 13128
and 20260809 -> 70737614 -> idx 2948 (second LCG = ...) chain matches hub.js logic lcg(lcg(seed))
Window globals + ?daily=YYYYMMDD&n=1/3/5 deterministic triple bump no uniform sampler
Cam Authentic: #FFFEF7 #E8E0C8 blueprint dots, neobrute 2px ink +3px shadow
"""

from __future__ import annotations
try:
    from cam_style import BG, INK, TEXT, SUBTLE_AAA, PAPER_DOT, OKABE, apply_cam_style, cam_card, cam_label, add_blueprint_dots
    from manim import Scene
    MANIM_AVAILABLE=True
except ImportError:
    MANIM_AVAILABLE=False
    Scene=object

FORMULA="(seed*1103515245+12345) & 0x7fffffff — glibc rand() a=1103515245 b=12345 m=2^31"
EXAMPLES={
 "20260807":{"seed":20260807,"lcg_a":11190772,"idx":2512,"pair":11804,"triple":13128,"b":1183128861,"c":1996123026},
 "20260809":{"seed":20260809,"lcg_a":70737614,"idx":2948,"note":"70737614 % 20719 = 2948"},
}
ENTITY=20719
GLOBALS_EXPOSED=["window.DAILY_SEED","window.UNIFIED_CHIMERA_DAILY","hubDailySeed","hubLcg","unifiedChimeraDaily","DM_PROVENANCE"]
SAME_LINK_SAME_STARS="?daily=YYYYMMDD&n=1/3/5 deterministic LCG idx=A%ENTITY j=B%ENTITY if j==idx j+1 k=C%ENTITY if k==idx|j k+2"

def lcg(seed:int)->int: return (seed*1103515245+12345)&0x7fffffff

class HubV04DailySeed(Scene if MANIM_AVAILABLE else object):
    def construct(self):
        if not MANIM_AVAILABLE: return
        apply_cam_style(self)
        add_blueprint_dots(self)
        title=cam_label("DailySeed LCG • glibc rand • deterministic", size=28)
        formula=cam_label(FORMULA, size=20)
        ex1=cam_label(f"20260807 → lcg {EXAMPLES['20260807']['lcg_a']} → idx 2512 pair 11804 triple 13128", size=18)
        ex2=cam_label(f"20260809 → 70737614 → idx 2948 (verified %ENTITY={ENTITY})", size=18)
        same=cam_label(f"Same-link-same-stars {SAME_LINK_SAME_STARS}", size=18)
        globals_lbl=cam_label("Exposed: "+", ".join(GLOBALS_EXPOSED[:4]), size=18)
        countdown=cam_label("Countdown to UTC midnight Date.UTC(Y,M,D+1) copy daily link btn-copy-daily-hub", size=18)
        self.add(title,formula,ex1,ex2,same,globals_lbl,countdown)
        # Verify chain matches ground truth without hallucinating
        assert lcg(20260807)==11190772
        assert lcg(20260809)==70737614
        self.wait(0.5)
