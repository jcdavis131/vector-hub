"""
hub_v06_offline_streak — PWA offline + Week Warrior • the daily habit
Ground truth 2026-08-09 measured FS now vs task-reported values (sw 5888 vs 5322, offline 13656 vs 13119) — both listed honest
PWA v67 shell CORE19 DENY9 manifest 2261B sw 5888B offline 13656B dark void #080A0F Week Warrior 7-dot localStorage streak
Copy daily link ?daily=YYYYMMDD&n=1/3/5 countdown UTC midnight UTC tock HH:MM:SS aria-live polite 2600ms fixed bottom 94px respects reduced-motion
"""

from __future__ import annotations
try:
    from cam_style import BG, INK, TEXT, SUBTLE_AAA, PAPER_DOT, OKABE, apply_cam_style, cam_card, cam_label, add_blueprint_dots
    from manim import Scene
    MANIM_AVAILABLE=True
except ImportError:
    MANIM_AVAILABLE=False
    Scene=object

PWA={"version":"v67","shell":"CORE19 DENY9","manifest_bytes_now":2261,"sw_bytes_now":5888,"sw_bytes_task_says":5322,"offline_bytes_now":13656,"offline_bytes_task_says":13119,"bg":"#080A0F dark void","theme":"#080A0F standalone","icons":"192/512 any+maskable ×4","start_url":"/?utm_source=pwa","screenshots":"1200x630 wide + 1080x1920 narrow","shortcuts":"Daily+Lab+Chimera UTM"}
STREAK={"dots":7,"storage_keys":["hub-streak","hub-best"],"filled":"#ffef8a shadow 1px 1px 0 #111 22×6px radius 999 border 1.5px #111","empty":"#fff.55 opacity","flame":".85s infinite","haptic":"vibrate(10) mobile"}
COPY="btn-copy-daily-hub data-hub-pack=1/3/5 hub-streak-track hub-toast hub-countdown LCG 1103515245 pill same link = same stars → ?daily=YYYYMMDD&n=1/3/5&a=A&b=B deterministic"
A11Y="toast role=status aria-live=polite fixed 50% 94px bg #fafaf8 countdown next in HH:MM:SS UTC tick setInterval 1000 Week Warrior 7-dot offline-streak-dots ●○ localStorage hub-streak hub-best best badge LCG A/B/C pills footer No fake promotion"

class HubV06OfflineStreak(Scene if MANIM_AVAILABLE else object):
    def construct(self):
        if not MANIM_AVAILABLE: return
        apply_cam_style(self)
        add_blueprint_dots(self)
        title=cam_label(f"PWA v67 shell {PWA['shell']} • CORE19 DENY9", size=26)
        sizes=cam_label(f"manifest {PWA['manifest_bytes_now']}B sw {PWA['sw_bytes_now']}B (task said {PWA['sw_bytes_task_says']}B) offline {PWA['offline_bytes_now']}B (target {PWA['offline_bytes_task_says']}B) shared-map 26792B", size=16)
        bg=cam_label(f"dark void {PWA['bg']} {PWA['theme']} theme #{PWA['bg']} offline card proof OFFLINE CACHED chip yellow 11px mono 800", size=18)
        streak=cam_label(f"Week Warrior {STREAK['dots']}-dot {STREAK['filled'][:30]}… filled #ffef8a empty #fff.55 haptic vibrate(10) flame .85s", size=18)
        copy=cam_label(COPY[:160], size=18)
        a11y=cam_label(A11Y[:160], size=18)
        cta=cam_label("Install PWA → keep streak → Week Warrior 7🔥 when ≥7 days — start your streak title", size=20)
        self.add(title,sizes,bg,streak,copy,a11y,cta)
        self.wait(0.5)
