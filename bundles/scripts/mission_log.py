"""
Scout v5 Prime — Mission Log writer
Path: workspace/bundles/scripts/mission_log.py
Spec: workspace/.scout/missions/<id>/timeline.jsonl with 7-field mandatory + OODA optional
Fields required: nodeId, agentId, attempt, latency, tokens, status, errorClass
Plus ts, runId, layer, ooda, tempo for v3.3
"""

import json, pathlib, datetime, os, sys, time

BASE = pathlib.Path.home() / "workspace" / ".scout" / "missions"
# fallback to workspace/.scout/missions (group-writable)
if not BASE.exists():
    alt = pathlib.Path.home() / ".scout" / "missions"
    if alt.exists():
        BASE = alt
    else:
        BASE.mkdir(parents=True, exist_ok=True)

REQUIRED = ["nodeId","agentId","attempt","latency","tokens","status","errorClass"]

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def init_mission(mission_id: str, meta: dict | None = None):
    """Create mission dir + init checkpoint.json"""
    mid = mission_id
    md = BASE / mid
    md.mkdir(parents=True, exist_ok=True)
    cp = md / "checkpoint.json"
    if not cp.exists():
        data = {
            "mission_id": mid,
            "version": "v5 Prime",
            "created": _now(),
            "status": "running",
            "meta": meta or {},
            "guarantees": {
                "structured_workflow": True,
                "tool_safety": "schema+sandbox 30s×2",
                "memory_discipline": "read/update summaries",
                "reasoning_boundaries": "max 7 steps",
                "eval_hooks": 6,
                "multi_agent": "routing+message passing+shared mem+hierarchical"
            }
        }
        cp.write_text(json.dumps(data, indent=2))
    # ensure timeline exists
    (md / "timeline.jsonl").touch(exist_ok=True)
    return str(md)

def log(mission_id: str, entry: dict):
    """Append one timeline entry, validating required fields — log even no-change"""
    # normalize aliases first — latency_ms->latency tokens_est->tokens (v3.3 compat)
    e = dict(entry)
    if "latency" not in e and "latency_ms" in e:
        e["latency"] = e["latency_ms"]
    if "tokens" not in e and "tokens_est" in e:
        e["tokens"] = e["tokens_est"]
    # also allow latency/tokens legacy to satisfy primary for JS interop
    if "latency_ms" not in e and "latency" in e:
        e["latency_ms"] = e["latency"]  # keep both for dual-search
    if "tokens_est" not in e and "tokens" in e:
        e["tokens_est"] = e["tokens"]

    missing = [k for k in REQUIRED if k not in e]
    if missing:
        raise ValueError(f"missing required timeline fields {missing} need {REQUIRED} got keys {list(entry.keys())} (supports aliases latency_ms->latency tokens_est->tokens)")

    if "ts" not in e:
        e["ts"] = _now()
    if "runId" not in e and "mission_id" not in e:
        e["runId"] = mission_id
    # write — mandatory 7-field JSONL, even no-change guaranteed
    md = BASE / mission_id
    md.mkdir(parents=True, exist_ok=True)
    tl = md / "timeline.jsonl"
    with open(tl, "a") as f:
        f.write(json.dumps(e) + "\n")
    return e

def pause(mission_id: str, reason: str = "human gate"):
    md = BASE / mission_id
    md.mkdir(parents=True, exist_ok=True)
    # log pause event as timeline entry (with required fields fake but spec wants event)
    entry = {
        "ts": _now(),
        "nodeId": "L0-scout-prime-pause",
        "agentId": "scout-prime",
        "attempt": 1,
        "latency": 0,
        "tokens": 0,
        "status": "paused",
        "errorClass": None,
        "event": "checkpoint_pause",
        "reason": reason,
        "runId": mission_id
    }
    log(mission_id, entry)
    # update checkpoint.json
    cp = md / "checkpoint.json"
    if cp.exists():
        data = json.loads(cp.read_text())
        data["paused"] = True
        data["pause_reason"] = reason
        data["paused_at"] = _now()
        cp.write_text(json.dumps(data, indent=2))
    return entry

def resume(mission_id: str):
    md = BASE / mission_id
    if not md.exists():
        raise FileNotFoundError(f"no mission {mission_id}")
    # load checkpoint.json pending nodes — v5 Prime pause/resume days later
    pending_nodes = []
    cp = md / "checkpoint.json"
    pending_count = 0
    if cp.exists():
        try:
            data = json.loads(cp.read_text())
            nodes = data.get("nodes") or data.get("dag", {}).get("nodes") or []
            # filter pending: status != done
            for n in nodes:
                if isinstance(n, dict) and n.get("status") != "done":
                    pending_nodes.append(n)
            pending_count = len(pending_nodes)
        except Exception:
            pending_nodes = []
            pending_count = 0
    entry = {
        "ts": _now(),
        "nodeId": "L0-scout-prime-resume",
        "agentId": "scout-prime",
        "attempt": 1,
        "latency": 0,
        "tokens": 0,
        "status": "resumed",
        "errorClass": None,
        "event": "checkpoint_resume",
        "runId": mission_id,
        "pending": pending_count,
        "pending_nodes": [n.get("nodeId") if isinstance(n, dict) else str(n) for n in pending_nodes[:10]],
        "ooda": "Feedback",
        "tempo": ":13"
    }
    log(mission_id, entry)
    if cp.exists():
        data = json.loads(cp.read_text())
        data["paused"] = False
        data["resumed_at"] = _now()
        cp.write_text(json.dumps(data, indent=2))
    return {"entry": entry, "pending_nodes": pending_nodes, "resume_msg": f"resumed {mission_id} {pending_count} nodes pending"}

if __name__ == "__main__":
    # quick self-test
    mid = sys.argv[1] if len(sys.argv)>1 else "test-mission"
    init_mission(mid, {"goal":"test"})
    log(mid, {"nodeId":"L1-strategist-1","agentId":"strategist","attempt":1,"latency":123,"tokens":45,"status":"done","errorClass":None,"ooda":"Orient"})
    print(f"mission {mid} ready at {BASE/mid}")
