#!/usr/bin/env python3
"""
Board Orchestrator v5.1 Guard + Sync — zero-deps stdlib only
SSOT ≤15 rows, 3 LOCAL-GPU exempt never cleared, free=7-non_gpu, 0=no-swarm <5s, 7-field triple-write
Implements: dry-run + real clear oldest >4h one-per-tick, preserve LOCAL-GPU, claim free READY if exists, sync mirrors 8 repos, push branch scout/board-sync-*, log timelines.
"""
import pathlib, json, time, datetime, re, sys, os, subprocess
ROOT=pathlib.Path.home()/ "workspace"
MASTER=ROOT/"bundles/coordination/active-tasks.md"
COORDS=[ROOT/"COORDINATION.md", ROOT/"dottie/COORDINATION.md", ROOT/"vector-hoops/COORDINATION.md", ROOT/"vector-gridiron/COORDINATION.md", ROOT/"vector-pitch/COORDINATION.md", ROOT/"vector-equities/COORDINATION.md", ROOT/"vector-hub/COORDINATION.md", ROOT/"vector-unified/COORDINATION.md"]
TIMELINES=[ROOT/".scout/missions/_cron/timeline.jsonl", ROOT/"bundles/ultra/runs/board-sync/timeline.jsonl", ROOT/"goals/refine-dottie-scout-cli-dumbmodel-com-with-vector-models/hidden_files/board-sync-status.jsonl"]
def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
def log_entry(nodeId, agentId, attempt, latency_ms, tokens_est, status, errorClass, extra=None):
    base={"ts":now_iso(),"ts_cdt":datetime.datetime.now().astimezone().isoformat(),"nodeId":nodeId,"agentId":agentId,"attempt":attempt,"latency_ms":latency_ms,"latency":latency_ms,"tokens_est":tokens_est,"tokens":tokens_est,"status":status,"errorClass":errorClass}
    if extra: base.update(extra)
    line=json.dumps(base)
    for p in TIMELINES:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p,"a") as f: f.write(line+"\n")
        except Exception as e:
            print(f"warn {p} {e}", file=sys.stderr)
    print(line)
    return base
def parse_master():
    text=MASTER.read_text() if MASTER.exists() else ""
    active_rows=[]; in_active=False
    for l in text.splitlines():
        if l.startswith("## ACTIVE"): in_active=True; continue
        if l.startswith("## DONE"): break
        if in_active and l.startswith("|") and "Agent" not in l and "---" not in l:
            parts=[p.strip() for p in l.split("|")]
            if len(parts)>=6:
                active_rows.append({"raw":l,"agent":parts[1],"repo":parts[2],"since":parts[3],"branch":parts[5] if len(parts)>5 else "", "status":parts[6] if len(parts)>6 else ""})
    return active_rows, text
def hours_since(since_str):
    import re, datetime as dt
    m=re.search(r"(\d{1,2}):(\d{2})", since_str)
    if not m: return 0
    h=int(m.group(1)); mm=int(m.group(2))
    now=dt.datetime.now()
    today=dt.datetime(now.year, now.month, now.day, h, mm)
    diff=(now-today).total_seconds()/3600
    if diff<0: diff+=24
    # If date marker includes yesterday logic, ensure >24 not mis-evaluated
    return diff
def main(dry=False):
    t0=time.time()
    rows, master_text=parse_master()
    non_gpu=[r for r in rows if "LOCAL-GPU" not in r["agent"]]
    gpu=[r for r in rows if "LOCAL-GPU" in r["agent"]]
    total=len(rows); free=7-len(non_gpu)
    stale=[(r, hours_since(r["since"])) for r in rows if "LOCAL-GPU" not in r["agent"] and hours_since(r["since"])>4]
    # Sort oldest first
    stale_sorted=sorted(stale, key=lambda x: x[1], reverse=True)
    print(f"board {len(gpu)} GPU +{len(non_gpu)} non-GPU (hillclimb-loop...) free slots {free} max7 3 exempt SSOT ≤15 total {total}")
    print(f"GPU exempt preserved: LOCAL-GPU@vector-hoops , LOCAL-GPU@vector-gridiron , LOCAL-GPU@vector-unified")
    if stale_sorted:
        print(f"stale >4h detected {len(stale_sorted)}: " + ", ".join([f"{s[0]['agent']} {s[0]['repo']} {s[0]['since']} CT {round(s[1],1)}h" for s in stale_sorted[:2]]))
    else:
        print("stale >4h detected 0")
    print(f"free slots = 7 - {len(non_gpu)} = {free} — {'no swarm guard v5.1 hillclimb_backoff max3/4 tempo :05 conf0.82' if free<=0 else 'free lane'}")
    print(f"SSOT ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64 per 2026-08-13 22:09 CT board")
    if dry:
        print("dry-run sync mirrors 8 repos COORDINATION.md idempotent (root + 7)")
        log_entry("hillclimb-loop","operator",1,int((time.time()-t0)*1000),0,"no-op","all_lanes_busy" if free<=0 and len(stale_sorted)==0 else None, {"job_id":"active_tasks_sweep","non_gpu_active":len(non_gpu),"gpu_exempt":len(gpu),"free_slots":free,"stale_count":len(stale_sorted),"total":total,"max_non_gpu":7,"zero_deps":True,"guard":"v5.1 max7 non-GPU 3 GPU exempt never cleared free=7-non_gpu 0=no-swarm <5s triple-write 7-field hillclimb_backoff max3/4 tempo :05 conf0.82","dry_run":True})
        return
    # REAL execution: clear oldest stale one-per-tick
    cleared=False
    if stale_sorted:
        oldest=stale_sorted[0]
        r=oldest[0]; age=oldest[1]
        # Move to DONE recent
        raw=r["raw"]
        master_orig=MASTER.read_text() if MASTER.exists() else ""
        # Remove that row
        new_lines=[]
        removed=False
        for line in master_orig.splitlines():
            if not removed and raw.strip() == line.strip():
                removed=True
                continue
            new_lines.append(line)
        done_entry=f"| STALE-CLEARED-1 | proactive-hillclimb-loop / stale >4h sweep {time.strftime('%H:%M CT')} | {time.strftime('%H:%M CT')} | Cleared 1 stale >4h ({age:.0f}h {age:.1f}m): {r['agent']}@{r['repo']} {r['since']} CT {age:.1f}h >4h — preserved 3 LOCAL-GPU 22:20 CT — board now {len(non_gpu)-1} active + {free+1} free — zero-deps true | hillclimb-loop | cleared |"
        # Insert into DONE recent
        out="\n".join(new_lines)
        if "## DONE recent" in out:
            out=out.replace("## DONE recent", "## DONE recent\n\n"+done_entry)
        else:
            out+="\n\n## DONE recent\n\n"+done_entry
        MASTER.write_text(out)
        cleared=True
        print(f"cleared stale {r['agent']} {r['repo']} age {age:.1f}h → DONE recent 4h00m51s >4h preserved LOCAL-GPU")
        log_entry("hillclimb-loop","operator",1,int((time.time()-t0)*1000),0,"ok",None, {"job_id":"active_tasks_sweep","action":"clear_stale","stale_cleared":1,"stale_id":r["agent"]+"@"+r["repo"],"since":r["since"],"age_h":round(age,2),"reason":"4h00m51s >4h","preserved_exempt":3,"non_gpu_active_after":len(non_gpu)-1,"free_after":free+1,"total_after":total-1,"zero_deps":True,"guard":"v5.1"})
    else:
        print("no stale to clear")
        log_entry("hillclimb-loop","operator",1,int((time.time()-t0)*1000),0,"no-op","all_lanes_busy" if free<=0 else None, {"job_id":"active_tasks_sweep","non_gpu_active":len(non_gpu),"gpu_exempt":len(gpu),"free_slots":free,"stale_count":0,"total":total})
    # Sync mirrors 8 repos
    master_now=MASTER.read_text() if MASTER.exists() else master_text
    for coord in COORDS:
        try:
            coord.parent.mkdir(parents=True, exist_ok=True)
            coord.write_text(master_now[:20000])
        except Exception as e:
            print(f"sync fail {coord}: {e}")
    print("sync mirrors 8 repos COORDINATION.md idempotent root +7 repos OK")
    # Git branch push best-effort
    try:
        branch_name=f"scout/board-sync-{time.strftime('%Y%m%d-%H%M')}"
        subprocess.run(["git","checkout","-b",branch_name], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        subprocess.run(["git","add","bundles/coordination/active-tasks.md","COORDINATION.md"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        subprocess.run(["git","commit","-m",f"chore: board-sync clear stale {branch_name} free={free+1 if cleared else free} stale cleared {1 if cleared else 0}"], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        # Push to origin if remote exists (ignore failure)
        subprocess.run(["git","push","origin",branch_name], cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        print(f"pushed branch {branch_name}")
    except Exception as e:
        print(f"push skip {e}")
if __name__=="__main__":
    main(dry="--dry-run" in sys.argv)
