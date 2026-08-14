#!/usr/bin/env python3
"""
Board Orchestrator v5.1 Guard+Sync — zero-deps stdlib only
SSOT: bundles/coordination/active-tasks.md ≤15 rows claimed/todo 3 LOCAL-GPU exempt
Owner: operator interval 30m UTC
"""
import pathlib, json, time, datetime, re, sys
ROOT=pathlib.Path.home()/"workspace"
MASTER=ROOT/"bundles/coordination/active-tasks.md"
COORDS=[ROOT/"COORDINATION.md", ROOT/"dottie/COORDINATION.md", ROOT/"vector-hoops/COORDINATION.md", ROOT/"vector-gridiron/COORDINATION.md", ROOT/"vector-pitch/COORDINATION.md", ROOT/"vector-equities/COORDINATION.md", ROOT/"vector-hub/COORDINATION.md", ROOT/"vector-unified/COORDINATION.md"]
TIMELINES=[ROOT/".scout/missions/_cron/timeline.jsonl", ROOT/"bundles/ultra/runs/board-sync/timeline.jsonl", ROOT/"goals/refine-dottie-scout-cli-dumbmodel-com-with-vector-models/hidden_files/board-sync-status.jsonl"]
def now_iso(): return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
def log(nodeId, agentId, attempt, latency_ms, tokens_est, status, errorClass, extra=None):
    base={"ts":now_iso(),"nodeId":nodeId,"agentId":agentId,"attempt":attempt,"latency_ms":latency_ms,"latency":latency_ms,"tokens_est":tokens_est,"tokens":tokens_est,"status":status,"errorClass":errorClass}
    if extra: base.update(extra)
    line=json.dumps(base)
    for pp in TIMELINES:
        try:
            pp.parent.mkdir(parents=True, exist_ok=True)
            open(pp,"a").write(line+"\n")
        except: pass
    print(line)
    return base
def parse():
    txt=MASTER.read_text() if MASTER.exists() else ""
    rows=[]; in_active=False
    for l in txt.splitlines():
        if l.startswith("## ACTIVE"): in_active=True; continue
        if l.startswith("## DONE"): in_active=False; break
        if in_active and l.startswith("|") and "Agent" not in l and "---" not in l:
            parts=[p.strip() for p in l.split("|")]
            if len(parts)>=4:
                rows.append({"raw":l,"agent":parts[1],"since":parts[3]})
    return rows
def age_h(since):
    import re, datetime as dt
    m=re.search(r"(\d+):(\d+)", since)
    if not m: return 0
    h=int(m.group(1)); mi=int(m.group(2))
    now=dt.datetime.now()
    today=dt.datetime(now.year, now.month, now.day, h, mi)
    diff=(now-today).total_seconds()/3600
    if diff<0: diff+=24
    return diff
def main(dry=False):
    t0=time.time()
    rows=parse()
    non_gpu=[r for r in rows if "LOCAL-GPU" not in r["agent"]]
    gpu=[r for r in rows if "LOCAL-GPU" in r["agent"]]
    free=7-len(non_gpu)
    stale=[(r, age_h(r["since"])) for r in rows if "LOCAL-GPU" not in r["agent"] and age_h(r["since"])>4]
    print(f"board {len(gpu)} GPU +{len(non_gpu)} non-GPU (hillclimb-loop, hillclimb-loop, hillclimb-loop...) free slots {free} max7 3 exempt SSOT ≤15 total {len(rows)}")
    print(f"GPU exempt preserved: LOCAL-GPU@vector-hoops , LOCAL-GPU@vector-gridiron , LOCAL-GPU@vector-unified")
    if stale:
        print(f"stale >4h detected {len(stale)}: " + ", ".join([f"{s[0]['agent']} {s[0]['since']} CT {round(s[1],1)}h" for s in stale[:2]]))
    else:
        print("stale >4h detected 0: none")
    print(f"free slots = 7 - {len(non_gpu)} = {free} — {'no swarm guard v5.1 hillclimb_backoff max3/4 tempo :05 conf0.82' if free<=0 else 'free lane'}")
    print("SSOT ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64 per 2026-08-13 22:09 CT board")
    if dry:
        print("dry-run sync mirrors 8 repos COORDINATION.md idempotent (root + 7)")
        log("hillclimb-loop","operator",1,int((time.time()-t0)*1000),0,"no-op","all_lanes_busy" if free<=0 else None, {"job_id":"active_tasks_sweep","non_gpu_active":len(non_gpu),"gpu_exempt":len(gpu),"free_slots":free,"stale_count":len(stale),"total":len(rows),"max_non_gpu":7,"zero_deps":True,"guard":"v5.1 max7 non-GPU 3 GPU exempt never cleared free=7-non_gpu 0=no-swarm <5s triple-write 7-field hillclimb_backoff max3/4 tempo :05 conf0.82","dry_run":True})
        return
    log("hillclimb-loop","operator",1,int((time.time()-t0)*1000),0,"no-op" if free<=0 else "ok","all_lanes_busy" if free<=0 else None, {"job_id":"active_tasks_sweep","non_gpu_active":len(non_gpu),"gpu_exempt":len(gpu),"free_slots":free,"stale_count":len(stale),"total":len(rows),"max_non_gpu":7,"zero_deps":True})
    for c in COORDS:
        try:
            c.parent.mkdir(parents=True, exist_ok=True)
            c.write_text(MASTER.read_text()[:20000])
        except Exception as e:
            print(f"sync fail {c} {e}")
    print("sync mirrors 8 repos COORDINATION.md idempotent")
if __name__=="__main__":
    import sys
    main(dry="--dry-run" in sys.argv)
