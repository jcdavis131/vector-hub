#!/usr/bin/env python3
"""
bundles/scaffold_check.py — W2 Cross-Repo Coherence drift table
Offline-capable, stdlib only.
Reads ~/workspace/vector-*/manifest.json + vector-hub manifest, prints drift.
Checks: icons 192/512 any+maskable, categories, shortcuts Daily/Lab UTM,
display standalone+display_override, theme_color bg, screenshots og-embed 1200x630,
pwa fields, js/css counts, delight/motion/final_qa/trading_card/unified_css present.
Zero-deps true allow acne:./src
"""
import json
import os
from pathlib import Path

BASE = Path(os.path.expanduser("~/workspace"))
REPOS = ["vector-hoops","vector-equities","vector-pitch","vector-gridiron","vector-unified","vector-hub"]

def load_manifest(repo):
    p = BASE / repo / "manifest.json"
    if not p.exists():
        return None, f"missing {p}"
    try:
        j = json.loads(p.read_text())
        return j, None
    except Exception as e:
        return None, str(e)

def check_icons(m):
    if not m: return "N/A"
    icons = m.get("icons",[])
    has_192_any = any(i.get("sizes")=="192x192" and "any" in (i.get("purpose") or "") for i in icons)
    has_512_any = any(i.get("sizes")=="512x512" and "any" in (i.get("purpose") or "") for i in icons)
    has_192_mask = any(i.get("sizes")=="192x192" and "maskable" in (i.get("purpose") or "") for i in icons)
    has_512_mask = any(i.get("sizes")=="512x512" and "maskable" in (i.get("purpose") or "") for i in icons)
    return f"192any:{has_192_any} 512any:{has_512_any} 192mask:{has_192_mask} 512mask:{has_512_mask} count={len(icons)}"

def check_categories(m):
    if not m: return "N/A"
    cats = m.get("categories",[])
    return f"{cats}"

def check_shortcuts(m):
    if not m: return "N/A"
    sc = m.get("shortcuts",[])
    daily = any("Daily" in (s.get("name","") or s.get("short_name","")) or "daily" in s.get("url","").lower() for s in sc)
    lab = any("Lab" in (s.get("name","") or s.get("short_name","")) or "lab" in s.get("url","").lower() for s in sc)
    utm = all("utm_source=pwa_shortcut" in (s.get("url","") ) for s in sc) if sc else False
    return f"count={len(sc)} Daily={daily} Lab={lab} UTM={utm} → {[s.get('short_name') for s in sc]}"

def check_display(m):
    if not m: return "N/A"
    d = m.get("display")
    do = m.get("display_override",[])
    return f"display={d} override={do} standalone?={d=='standalone' and 'standalone' in do}"

def check_theme(m):
    if not m: return "N/A"
    return f"theme={m.get('theme_color')} bg={m.get('background_color')} id={m.get('id')} start={m.get('start_url')} scope={m.get('scope')}"

def check_screenshots(m):
    if not m: return "N/A"
    shots = m.get("screenshots",[])
    wide_1200 = any(s.get("sizes")=="1200x630" for s in shots)
    og_embed = any("og-embed" in s.get("src","") or "og-1200x630" in s.get("src","") for s in shots)
    return f"count={len(shots)} 1200x630={wide_1200} og-embed={og_embed} srcs={[s.get('src') for s in shots]}"

def check_pwa_fields(m):
    if not m: return "N/A"
    fields = ["name","short_name","description","background_color","theme_color","display","display_override","orientation","scope","start_url","id","lang","dir","categories","prefer_related_applications","icons","screenshots","shortcuts"]
    missing = [f for f in fields if f not in m]
    return f"present {len(fields)-len(missing)}/{len(fields)} missing={missing} lang={m.get('lang')} dir={m.get('dir')} orient={m.get('orientation')} prefer={m.get('prefer_related_applications')}"

def check_assets(repo):
    asset_dir = BASE / repo / "assets"
    if not asset_dir.exists():
        return "no assets/"
    js = list(asset_dir.glob("*.js"))
    css = list(asset_dir.glob("*.css"))
    # check required files
    required = ["final-qa.css","motion.css","shell.css","unified.css","responsive.css","trading-card.css","player-profile-v28.css","pwa-install.js","site-nav.js","error-boundary.js","keyboard-a11y.js","delight.js"]
    present = {f: (asset_dir / f).exists() for f in required}
    miss = [k for k,v in present.items() if not v]
    return f"js={len(js)} css={len(css)} required_missing={miss} delight={present.get('delight.js')} motion={(asset_dir/'motion.css').exists()} final_qa={(asset_dir/'final-qa.css').exists()} trading={(asset_dir/'trading-card.css').exists()} unified={(asset_dir/'unified.css').exists()}"

def main():
    print("=== W2 Cross-Repo PWA Coherence Drift Table ===")
    print(f"Gold: hoops 8.9 v66 LOD 4000/8000 DPR1 22990B shared-map.js v57 provenance 7/7/0")
    print(f"Bundles: manifest.json 13 agents 11 packs ultra modules MoMA-lite GARNet checkpoint-manager recovery-ladder pacing-filter verification-econ")
    print(f"Zero-deps: true allow acne:./src")
    print()
    header = f"{'repo':<18} | icons | cats | shortcuts | display | theme/bg | screenshots | pwa fields | assets"
    print(header)
    print("-"*160)
    for repo in REPOS:
        m, err = load_manifest(repo)
        if err:
            print(f"{repo:<18} | ERROR {err}")
            continue
        icons = check_icons(m)
        cats = check_categories(m)
        sc = check_shortcuts(m)
        disp = check_display(m)
        theme = check_theme(m)
        shots = check_screenshots(m)
        pwa = check_pwa_fields(m)
        assets = check_assets(repo)
        print(f"\n--- {repo} ---")
        print(f" icons 192/512 any+maskable : {icons}")
        print(f" categories                 : {cats}")
        print(f" shortcuts Daily/Lab UTM   : {sc}")
        print(f" display standalone+override: {disp}")
        print(f" theme_color bg             : {theme}")
        print(f" screenshots og-embed 1200x630: {shots}")
        print(f" pwa fields                 : {pwa}")
        print(f" js/css counts delight/motion/final_qa/trading/unified: {assets}")
        # vercel check
        vpath = BASE / repo / "vercel.json"
        if vpath.exists():
            try:
                vj = json.loads(vpath.read_text())
                print(f" vercel.json cleanUrls={vj.get('cleanUrls')} headers={len(vj.get('headers',[]))} rewrites={len(vj.get('rewrites',[]))}")
            except Exception as e:
                print(f" vercel.json error {e}")
        else:
            print(f" vercel.json MISSING (need cleanUrls true)")
        # candidate
        cpath = BASE / repo / "candidate.json"
        if cpath.exists():
            try:
                cj = json.loads(cpath.read_text())
                print(f" candidate.json score={cj.get('score', cj.get('overall_score'))} passes={cj.get('passes')} verifier={cj.get('verifier')} zero_deps={cj.get('zero_deps')} threshold={cj.get('threshold')}")
            except Exception as e:
                print(f" candidate.json parse error {e}")
        else:
            print(f" candidate.json MISSING")
        print()

    # zero_deps bundle
    zd = BASE / "bundles" / "zero_deps.json"
    if zd.exists():
        print(f"bundles/zero_deps.json: {zd.read_text()[:300]}")
    else:
        print("bundles/zero_deps.json MISSING")

if __name__ == "__main__":
    main()
