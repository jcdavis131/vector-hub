"""
hub_v05_chimera_joint — Joint but not blind yet • Chimera and honest caveats
Marketing must not hide: sport identity still partly recoverable Δ+0.0593 over majority 0.6258 → 0.6851
6 live archetypes A0,A1,A2,A3,A5,A11 + 6 deferred A4,A6-A10 folded into A3 or T0-T3 trajectory axis
Silhouette 0.683, cross-sport NN same-arch 0.9828 random 0.1712, top-10 retrieval 0.0 on 40 hand-curated pairs (= informational), exploitable leak
100% accurate numbers from assets/data/unified.json + reports
"""

from __future__ import annotations
try:
    from cam_style import TEXT, SUBTLE_AAA, PAPER_DOT, OKABE, apply_cam_style, cam_label, add_blueprint_dots
    from manim import Scene
    MANIM_AVAILABLE=True
except ImportError:
    MANIM_AVAILABLE=False
    Scene=object

G2={"sport_acc":0.6851,"majority_baseline":0.6258,"delta_vs_majority":0.0593,"target_ceiling":0.7258,"status":"met but weak","shuffled_embedding":0.6257,"legacy_impossible":0.4333}
G1={"hoops_drop":-0.0526,"hoops_baseline":0.7385,"hoops_joint":0.7911,"gridiron_drop":0.0,"gridiron_baseline":0.9991,"pitch_drop":0.0021,"pitch_baseline":0.893,"pitch_joint":0.8909,"shuffled_drops":(0.5493,0.6920,0.5617)}
G4={"hit_rate":0.9828,"random_baseline":0.1712}
RET_TOP10={"n":40,"hit_rate":0.0}
ARCH={"declared_12":"A0-A11","live_6":"A0,A1,A2,A3,A5,A11","deferred_6":"A4,A6,A7,A8,A9,A10","fold_note":"A4 pitch-only 81% defenders folded into A3; A6/A7 pedigree grain, A8/A9 career-arc T0-T3 split off v0 0 members, pedigree join 17 matches 17 false positives Matt Ryan NFL≠NBA"}
SILHOUETTE=0.683
JOINT="20,719×64-d three encoders CORAL+contrastive+GRL, native 64/32/24 → shared 64-d trunk"

class HubV05ChimeraJoint(Scene if MANIM_AVAILABLE else object):
    def construct(self):
        if not MANIM_AVAILABLE: return
        apply_cam_style(self)
        add_blueprint_dots(self)
        # five cards — caveat honest marketing
        t1=cam_label("Joint but not blind yet — honest tagline must stay in marketing", size=26)
        g2=cam_label(f"Sport acc {G2['sport_acc']} vs majority {G2['majority_baseline']} Δ+{G2['delta_vs_majority']} ceiling {G2['target_ceiling']} — legacy {G2['legacy_impossible']} impossible", size=18)
        g4=cam_label(f"Same-arch NN {G4['hit_rate']} vs random {G4['random_baseline']} — silhouette {SILHOUETTE} — top-10 curly {RET_TOP10['hit_rate']} on {RET_TOP10['n']} hand-curated", size=18)
        arch=cam_label(f"12 archetypes {ARCH['declared_12']} 6 live {ARCH['live_6']} 6 deferred {ARCH['deferred_6']} — {ARCH['fold_note'][:120]}…", size=18)
        joint=cam_label(JOINT, size=18)
        caveat=cam_label("Forward: equites no; draft corr hoops 0.2611 gridiron 0.4175 — weak baseline — market has different physics", size=18)
        self.add(t1,g2,g4,arch,joint,caveat)
        self.wait(0.5)
