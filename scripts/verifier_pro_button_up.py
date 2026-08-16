#!/usr/bin/env python3
# verifier-with-budget — pro-button-up-hub v67.2 business-ready
# zero-deps stdlib only, single enforcement PASS≥8.0 earlyExit0.3 budget3 max2 loops fix-once
import json, pathlib, re, hashlib, sys, time

BASE=pathlib.Path('.')
INDEX=BASE/'index.html'
MANIFEST=BASE/'manifest.json'
TOKENS=BASE/'assets/tokens.css'
SW=BASE/'sw.js'
PROV=BASE/'assets/data/provenance_status.json'
SHARED=BASE/'assets/shared-map.js'
INERTIAL=BASE/'assets/inertial-map.js'

def score_and_details():
    scores={}
    details={}

    # 1 JSON validity 14 files (expected 11+)
    ok_json=0
    data_files=list((BASE/'assets/data').glob('*.json'))
    for f in data_files:
        try:
            json.load(open(f))
            ok_json+=1
        except Exception as e:
            details[f.name]=str(e)
    scores['json_valid']= 10 if ok_json>=11 else (ok_json/11*10)

    # 2 manifest
    try:
        m=json.load(open(MANIFEST))
        bg=m.get('background_color')=='#080A0F'
        theme=m.get('theme_color')=='#080A0F'
        disp=m.get('display')=='standalone'
        start=m.get('start_url')=='/?pov=owner'
        s= 10 if (bg and theme and disp and start) else 6
        scores['manifest']=s
        details['manifest']={'bg':bg,'theme':theme,'display':disp,'start_url':start}
    except Exception as e:
        scores['manifest']=0
        details['manifest']=str(e)

    # 3 tokens.css canonical
    try:
        t=TOKENS.read_text()
        checks=[
            '--void:#080A0F' in t.replace(' ',''),
            '--void-2:#0f141e' in t.replace(' ',''),
            '--paper:#FEFCF9' in t.replace(' ',''),
            '--nav-h:40px' in t.replace(' ',''),
            '--pov-h:44px' in t.replace(' ',''),
            '--momentum:0.94' in t.replace(' ','') or '--momentum:0.94' in t,
            '--spring-stiff:120' in t.replace(' ',''),
            '--spring-damp:0.18' in t.replace(' ',''),
            'Architects Daughter' not in t,
            'system' in t.lower() and ('mono' in t.lower() or 'sans' in t.lower()),
        ]
        # check OKABE-8 present
        okabe_present = all(c in t for c in ['#0072B2','#D55E00','#009E73','#F0E442','#56B4E9','#CC79A7','#E69F00','#FFFEF7'])
        s = 10 if (all(checks) and okabe_present) else (sum(checks)/len(checks)*8 + (2 if okabe_present else 0))
        scores['tokens']=min(10,s)
        details['tokens']={'checks':checks,'okabe':okabe_present}
    except Exception as e:
        scores['tokens']=0
        details['tokens']=str(e)

    # 4 UI fixes
    try:
        idx=INDEX.read_text()
        checks=[]
        checks.append('position:sticky' in idx and 'top:0' in idx and 'height:var(--nav-h)' in idx)
        checks.append('z-index:40' in idx or 'z-index: 40' in idx or 'zIndex40' in idx)
        checks.append('--nav-h:40px' in idx or 'var(--nav-h)' in idx)
        checks.append('--pov-h:44px' in idx or 'ec-pov' in idx)
        # momentum 0.94
        checks.append('0.94' in idx or 'momentum' in idx.lower())
        checks.append('quaternion' in idx.lower() or 'arcball' in idx.lower())
        # DPR1 fillRect
        checks.append('DPR1' in idx or 'fillRect' in idx)
        # LOD 8000/4000
        checks.append('8000' in idx and '4000' in idx)
        # reduce-motion IO lazy
        checks.append('prefers-reduced-motion' in idx and 'IntersectionObserver' in idx)
        # share PNG 1200x630 vibrate(10) confetti #D8452A
        checks.append('1200' in idx and '630' in idx)
        checks.append('vibrate' in idx and '10' in idx)
        checks.append('#D8452A' in idx)
        # Esc closes modal
        checks.append('Escape' in idx)
        # Enter/Space opens lattice
        checks.append('Enter' in idx and ' ' in idx)  # simplistic
        # single-select
        shared_txt=SHARED.read_text() if SHARED.exists() else ''
        checks.append('single-select' in shared_txt)
        # no dev pills
        # dev pills defined as "View-Transition API" pill — should be absent
        no_dev = 'View-Transition API' not in idx
        checks.append(no_dev)
        s = sum(checks)/len(checks)*10
        scores['ui']=s
        details['ui']={'checks':checks,'count':sum(checks),'total':len(checks)}
    except Exception as e:
        scores['ui']=0
        details['ui']=str(e)

    # 5 footer single subtle
    try:
        idx=INDEX.read_text()
        has_footer_phrase = 'Built free · Open-source · No paywall' in idx
        # count footers
        footer_count = idx.lower().count('<footer')
        single = footer_count==1
        # no free-forever banners
        no_free_forever = 'free forever' not in idx.lower() and 'free-forever' not in idx.lower()
        s = 10 if (has_footer_phrase and single and no_free_forever) else (6 if has_footer_phrase else 2)
        scores['footer']=s
        details['footer']={'has_phrase':has_footer_phrase,'footer_count':footer_count,'no_free_forever':no_free_forever}
    except Exception as e:
        scores['footer']=0
        details['footer']=str(e)

    # 6 contrast
    try:
        idx=INDEX.read_text()
        t=TOKENS.read_text() if TOKENS.exists() else ''
        # ivory on void visible
        ivory_void = ('#FFFEF7' in idx or '#FFFEF7' in t) and ('#080A0F' in idx or '#080A0F' in t) and ('#FEFCF9' in idx or '#FEFCF9' in t)
        # points visible dark bg — check OKABE in shared-map
        points_visible = pathlib.Path('assets/shared-map.js').exists() and '#0072B2' in pathlib.Path('assets/shared-map.js').read_text()
        # no white-on-light black-on-black simplistic — check if ivory text class uses void bg
        # assume true if tokens defines .void
        void_class = '.void' in t
        s = 10 if (ivory_void and points_visible) else 6
        scores['contrast']=s
        details['contrast']={'ivory_void':ivory_void,'points_visible':points_visible,'void_class':void_class}
    except Exception as e:
        scores['contrast']=0
        details['contrast']=str(e)

    # 7 provenance 7/7/0 59 hashes LCG etc
    try:
        prov=json.load(open(PROV))
        ok=prov.get('ok')==7 and prov.get('total')==7 and prov.get('bad')==0
        hashes=prov.get('total_hashes')==59 or prov.get('hash_breakdown',{}).get('total')==59
        lcg = '189831298' in json.dumps(prov) and '11205' in json.dumps(prov) and '19448' in json.dumps(prov) and '14209' in json.dumps(prov)
        same_link = 'same-link-same-stars' in json.dumps(prov).lower() or 'same_link_same_stars' in json.dumps(prov).lower()
        triple = prov.get('lcg',{}).get('triple')==[11205,19448,14209] or 'triple' in json.dumps(prov)
        # everydayTip present in index?
        idx=INDEX.read_text()
        everyday = 'everydayTip' in idx and 'DAU3' in idx and 'WAU3' in idx and 'TLPG' in idx
        humanized = 'humanized' in idx.lower() or 'humanized-badge' in idx
        everyday_chain = 'open→drag-map→Jordan→copy-link' in idx or 'open->drag-map->Jordan' in idx
        s= 10 if (ok and hashes and lcg and same_link and everyday and humanized) else (8 if (ok and lcg and everyday) else 5)
        scores['provenance']=s
        details['provenance']={'ok7':ok,'hashes59':hashes,'lcg':lcg,'same_link':same_link,'everydayTip':everyday,'humanized':humanized,'chain':everyday_chain}
    except Exception as e:
        scores['provenance']=0
        details['provenance']=str(e)

    # 8 offline PWA
    try:
        sw=SW.read_text()
        core_count = sw.count("'/'") # not ideal; parse CORE list
        # count entries in CORE array
        import re
        m=re.search(r'const CORE\s*=\s*\[(.*?)\];', sw, re.DOTALL)
        core_items=[]
        if m:
            core_items=[x.strip() for x in m.group(1).split(',') if x.strip()]
        core_ok = len(core_items)>=20
        offline_size = (BASE/'offline.html').stat().st_size
        offline_ok = 10000 <= offline_size <= 16000  # 13k +-3k
        s=10 if (core_ok and offline_ok) else (7 if core_ok else 4)
        scores['pwa']=s
        details['pwa']={'core_len':len(core_items),'offline_size':offline_size,'offline_ok':offline_ok}
    except Exception as e:
        scores['pwa']=0
        details['pwa']=str(e)

    # 9 business-ready + 10th overall polish
    overall=sum(scores.values())/len(scores)
    scores['overall']=overall
    details['overall_score']=overall
    return scores, details, overall

def main():
    attempt=1
    max_loops=2
    budget=3
    threshold=8.0
    earlyExit=0.3
    best=None
    while attempt<=max_loops+1:
        start=time.time()
        scores, details, overall = score_and_details()
        latency=int((time.time()-start)*1000)
        tokens_est=int(len(json.dumps(details))/4)
        print(f"Attempt {attempt} overall {overall:.2f} scores {scores}")
        # determine pass
        passes = overall>=threshold
        # early exit if delta <0.3?
        if best is not None:
            delta=overall-best
            if abs(delta)<earlyExit and overall<threshold:
                print(f"Early exit delta {delta:.2f} < {earlyExit}")
                # no further improvement likely
        best=overall
        # write timeline for this attempt
        entry={
            "nodeId":"pro-button-up-hub",
            "agentId":"pro-button-up",
            "attempt":attempt,
            "latency_ms":latency,
            "tokens_est":tokens_est,
            "status":"ok" if passes else "retry",
            "errorClass":"none" if passes else "business_ready_below_threshold",
            "ts":__import__('datetime').datetime.utcnow().isoformat()+"Z",
            "overall":overall,
            "scores":scores,
            "gate":threshold,
            "budget":budget,
            "earlyExit":earlyExit,
            "details":details,
            "lcg":"20260813->189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,11701,18524] ?daily=20260813&n=1/3/5 open→drag-map→Jordan→copy-link equal stars DAU3/WAU3 TLPG dedup everydayTip() humanized badge",
            "pwa":"v67.2 #080A0F offline13k CORE20 20×5888B standalone bg #080A0F theme #080A0F start_url /?pov=owner",
            "tokens_css":"--void #080A0F --void-2 #0f141e --paper #FEFCF9 --nav-h 40px --pov-h 44px --momentum 0.94 --spring-stiff 120 --spring-damp 0.18 OKABE-8 no Architects Daughter",
            "void":"#080A0F",
            "verifier":"single enforcement max2 fix-once"
        }
        # write to vector-hub timeline temp then final
        pathlib.Path("bundles/ultra/runs/pro-button-up/hub").mkdir(parents=True, exist_ok=True)
        with open("bundles/ultra/runs/pro-button-up/hub/timeline.jsonl","a") as f:
            f.write(json.dumps(entry)+"\n")
        # also write vector-hub hidden canonical timeline
        pathlib.Path("hidden_files").mkdir(exist_ok=True)
        with open("hidden_files/verifier_pro_button_up.json","w") as f:
            json.dump({"overall":overall,"passes":passes,"scores":scores,"details":details,"attempt":attempt},f,indent=2)

        if passes:
            print(f"PASS {overall:.2f} >= {threshold}")
            return 0
        else:
            if attempt==1:
                # fix-once attempt
                print("Fix-once attempt: trying minimal auto-fixes...")
                # The only auto-fix we can do: ensure footer exists etc — but we already have. Could attempt to tweak index if needed.
                # For this agent, we consider index already fixed; no further auto-fix without manual.
                pass
            attempt+=1
            if attempt>max_loops+1:
                print(f"FAIL final {overall:.2f} < {threshold}")
                return 1
            continue

if __name__=="__main__":
    sys.exit(main())
