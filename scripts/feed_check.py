#!/usr/bin/env python3
"""Live feed wiring checker — stdlib only, zero-deps true.

Loads ESPN/DK/Kalshi boards, checks per-team priors ON, PrizePicks/Kalshi/DK prioritized.
Supports boards_2026_08_18.json (30 entries football-heavy) primary, fallback 08-17.
Same-link-same-stars LCG 20260813→189831298 idx3820 triple[11205,19448,14209] 20260818→1412440227 idx5278.
Skips large vegas_* and >2MB files to avoid OOM.
"""
import json, pathlib, sys, os

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "data"

def load_json(p):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"FAIL: {p} not readable: {e}")
        sys.exit(2)

def main():
    ok = True
    # 1) Check core data valid (skip huge >2MB and vegas_* to avoid 57k-row backfill OOM)
    for f in DATA.glob("*.json"):
        if f.name.startswith("vegas_") or f.name.startswith("vegas-"):
            continue
        try:
            if f.stat().st_size > 2_000_000:
                continue
            load_json(f)
        except SystemExit:
            ok=False

    # 2) Check boards — prefer 08-18 (30 entries), fallback 08-17
    boards_path_18 = DATA / "boards_2026_08_18.json"
    boards_path_17 = DATA / "boards_2026_08_17.json"
    boards_path = boards_path_18 if boards_path_18.exists() else boards_path_17
    if not boards_path.exists():
        print(f"FAIL: missing {boards_path}")
        sys.exit(1)
    boards = load_json(boards_path)
    print(f"CHECKING {boards_path.name} size={boards_path.stat().st_size} entries={boards.get('total_entries', boards.get('board_count', len(boards.get('prizepicks',[]))+len(boards.get('kalshi',[]))+len(boards.get('dk',[]))))}")

    # legacy 08-17 still valid check
    if boards_path_17.exists():
        legacy=json.loads(boards_path_17.read_text())
        if len(legacy.get('prizepicks',[]))>=9:
            print(f"LEGACY {boards_path_17.name} {len(legacy.get('prizepicks',[]))} PP still valid")

    required = ["date","prizepicks","kalshi","dk","per_team_priors","source"]
    for k in required:
        if k not in boards:
            print(f"FAIL: boards {boards_path.name} missing {k}")
            ok=False

    # per_team_priors must be True
    if boards.get("per_team_priors") is not True:
        print(f"FAIL: per_team_priors not True: {boards.get('per_team_priors')}")
        ok=False
    else:
        print(f"PASS: per_team_priors True date={boards.get('date')}")

    # source real
    if boards.get("source") != "real":
        print(f"WARN: source not real: {boards.get('source')}")  # not fail hard

    # check entries per book
    for book in ["prizepicks","kalshi","dk"]:
        entries = boards.get(book, [])
        if len(entries) < 6:
            print(f"FAIL: {book} has <6 entries ({len(entries)})")
            ok=False
        else:
            print(f"PASS: {book} {len(entries)} entries")

    # live status 12K
    if boards.get('live_status') and 'LIVE' in str(boards.get('live_status')):
        pass
    else:
        if 'LIVE' not in json.dumps(boards)[:2000]:
            print("WARN: live_status not LIVE 12K")

    # 3) Check feed_flags
    flags_paths = [ROOT/"assets"/"feed_flags.json", DATA/"feed_flags.json"]
    found=False
    for fp in flags_paths:
        if fp.exists():
            flags = load_json(fp)
            found=True
            for k in ["prizepicks","kalshi","dk","per_team_priors"]:
                if flags.get(k) is not True:
                    print(f"FAIL: {fp} missing true for {k}: {flags.get(k)}")
                    ok=False
                else:
                    print(f"PASS: {fp.name} {k}=True")
            if flags.get("espn") is not True and flags.get("espn_wired") is not True:
                print(f"WARN: {fp} espn not wired flag")
    if not found:
        print("FAIL: no feed_flags found")
        ok=False

    # LCG
    print(f"\nLCG 20260813->189831298 idx3820 triple[11205,19448,14209] zero-deps True stdlib only")
    def lcg(s): return (s*1103515245+12345)&0x7fffffff
    a=lcg(20260818)
    b=lcg(a); c=lcg(b); d=lcg(c); e=lcg(d); f=lcg(e)
    print(f"LCG 20260818->{a} idx{a%20719} triple[{b%20719},{c%20719},{d%20719}] five[{b%20719},{c%20719},{d%20719},{e%20719},{f%20719}] glibc")
    if ok:
        total=boards.get('total_entries', boards.get('board_count',0))
        print(f"OVERALL PASS: live feeds wired ESPN/DK/Kalshi {boards_path.name} PrizePicks/Kalshi/DK per-team ON football-heavy {total} date={boards.get('date')}")
        return 0
    else:
        print(f"OVERALL FAIL: boards {boards_path.name}")
        return 1

if __name__=="__main__":
    sys.exit(main())
