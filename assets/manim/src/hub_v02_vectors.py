"""
hub_v02_vectors — 20,719 stars in 64-d • the map that fits all three sports
Accuracy: joint = 12,966 hoops + 5,323 gridiron + 2,430 pitch = 20,719 verified against unified.json headline_stats source split
Native widths: 64-d hoops / 32-d gridiron / 24-d pitch → shared trunk 64-d CORAL+contrastive+GRL
Shared-map.js 26792B LOD 4000 mobile / 8000 desktop DPR1 fillRect no arc() throttle 30/24 idle 8s pause
"""

from __future__ import annotations
try:
    from cam_style import BG, INK, CARD_FILL, PAPER_DOT, TEXT, SUBTLE_AAA, OKABE, apply_cam_style, cam_card, cam_label, add_blueprint_dots
    from manim import Scene, VGroup, FadeIn, Write
    MANIM_AVAILABLE=True
except ImportError:
    MANIM_AVAILABLE=False
    Scene=object

ENTITY=20719
BREAKDOWN=(12966,5323,2430)  # sum 20719
ENCODERS="64-d hoops / 32-d gridiron / 24-d pitch → shared trunk 64-d"
MAP_SPEC={"file":"assets/shared-map.js","bytes_now":26792,"LOD_mobile":4000,"LOD_desktop":8000,"DPR":1,"renderer":"fillRect no arc()"}
PER_GAME={
 "hoops":{"entity_count":12966,"dims":"64-d MTNN 18 towers","source_files":10},
 "gridiron_joint":{"player_seasons_joint":5323,"game_projection_2026":646,"dims":"32-d MTNN v2 gated fusion","source_files":7},
 "pitch":{"entity_count":2430,"dims":"24-d MTNN","source_files":3},
 "equities":{"tickers":500,"company_years":4831,"dims":"64-d MTNN 17 towers","source_files":7,"separate":"not in joint"},
 "tennis":{"player_seasons":4022,"dims":"315 features → 32-d MTNN 8 towers","source_files":14,"separate":"probe only, no daily"},
}

class HubV02Vectors(Scene if MANIM_AVAILABLE else object):
    def construct(self):
        if not MANIM_AVAILABLE: return
        apply_cam_style(self)
        add_blueprint_dots(self, color=PAPER_DOT)
        title=cam_label(f"One 64-d space • {ENTITY} player-seasons", mono=True, size=36, color=TEXT)
        breakdown=cam_label(f"{BREAKDOWN[0]} hoops + {BREAKDOWN[1]} gridiron + {BREAKDOWN[2]} pitch = {ENTITY}", mono=False, size=20, color=SUBTLE_AAA)
        enc=cam_label(ENCODERS, mono=False, size=18, color=TEXT)
        map_spec=cam_label(f"shared-map.js {MAP_SPEC['bytes_now']}B LOD {MAP_SPEC['LOD_mobile']}/{MAP_SPEC['LOD_desktop']} DPR1 fillRect no arc() throttle 30/24 idle 8s pause", mono=True, size=18, color=TEXT)
        caveat=cam_label("Equities 500×10yr = 4,831 rows own puzzle — market has different physics — not in joint", mono=False, size=18, color=TEXT)
        for obj in (title,breakdown,enc,map_spec,caveat):
            self.add(obj)
        self.wait(0.6)
