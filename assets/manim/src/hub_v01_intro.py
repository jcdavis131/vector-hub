"""
hub_v01_intro — Five daily vector puzzles, one arcade
Cam Authentic: #FFFEF7 paper, #E8E0C8 blueprint dots, neobrute 2px ink +3px shadow,
Okabe-Ito flat, mono 24px+, caption 18px+ AAA 17:1
Accuracy: 100% marketing — tagline live 2026-08-09, tennis caveat, 6 models 5 puzzles

Design tokens per cam_style.py
"""

from __future__ import annotations
try:
    from cam_style import (
        BG, INK, CARD_FILL, PAPER_DOT, SHADOW, TEXT, SUBTLE_AAA,
        OKABE, apply_cam_style, cam_card, cam_label, add_blueprint_dots,
        check_no_overlap,
    )
    from manim import Scene, VGroup, FadeIn, Write, UP
    MANIM_AVAILABLE = True
except ImportError:
    MANIM_AVAILABLE = False
    BG="#FFFEF7"; INK="#111111"; CARD_FILL="#FFFFFF"; PAPER_DOT="#E8E0C8"; TEXT="#111111"
    Scene=object
    VGroup=object

# Ground truth — do not drift
TAGLINE = "Five daily vector puzzles — NBA, NFL, World Cup, public companies, and joint cross-sport chimera (20,719×64-d, dailySeed LCG)"
ENTITY = 20719
DIMS = 64
SIX_CARDS = ["hoops 12,966","gridiron 646 → 5,323 joint","pitch 2,430","equities 500","tennis 4,022 probe","unified 20,719 joint"]
CAVEATS = ["Tennis model card only — 4,022 player-seasons, 315 feats, 32-d probe, no daily yet",
           "Gridiron game: 646 players for 2026 season; joint holds 5,323 historical player-seasons"]

class HubV01Intro(Scene if MANIM_AVAILABLE else object):
    """
    6-model hub intro — what dumbmodel.com actually is.
    Structure: 6 cards (Okabe-Ito flat fill white + accent border), triple-encoded.
    """
    def construct(self):
        if not MANIM_AVAILABLE:
            return
        apply_cam_style(self)  # #FFFEF7 + blueprint #E8E0C8 dots + AAA check
        add_blueprint_dots(self, spacing=22, opacity=0.18, color=PAPER_DOT)
        # Card grid 6 columns x 1 row (mobile 2 rows)
        # SITE_PILL: Six models · five daily puzzles · free · no account
        cards = VGroup(*[
            cam_card(width=2.4, height=1.4, fill=CARD_FILL, stroke=INK, shadow=SHADOW,
                     label=label, mono=False, accent=OKABE[list(OKABE.keys())[i%8]])
            for i,label in enumerate(SIX_CARDS)
        ]).arrange(buff=0.18)
        title = cam_label("Six models · five daily puzzles", mono=True, size=24, color=TEXT, weight=900)
        subtitle = cam_label(TAGLINE, mono=False, size=18, color=SUBTLE_AAA)
        # CAPTION: tennis no daily
        caption = cam_label(CAVEATS[0], mono=False, size=18, color=TEXT)
        self.play(FadeIn(title))
        self.play(cards.animate.shift(UP*0.2))
        # triple encoding: shape+icon+text+pattern — AAA checks inside cam_style
        check_no_overlap([title, cards, subtitle, caption], padding=12)
        self.play(Write(subtitle), Write(caption))
        self.wait(0.6)
