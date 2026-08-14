/**
 * all-lanes-busy-guard.js v5.1 — max7 non-GPU 3 GPU exempt never cleared free=7-non_gpu 0=no-swarm <5s 7-field
 * zero-deps stdlib only — hillclimb_backoff max3/4 tempo :05 conf0.82
 * SSOT: bundles/coordination/active-tasks.md ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64
 */
module.exports={
  id:"all-lanes-busy-guard",
  version:"5.1",
  v51:{
    maxNonGPU:7,
    exemptGPU:3,
    freeFormula:"free = 7 - non_gpu_active",
    noSwarmCondition:"free<=0 → no-op <5s log mandatory 7-field nodeId hillclimb-loop attempt latency_ms tokens_est status errorClass all_lanes_busy",
    required_fields:["nodeId","agentId","attempt","latency_ms","tokens_est","status","errorClass"],
    tags:["always-on","operator","v5.1","guard","sync","heartbeat"],
    tempo:":05",
    conf:0.82,
    hillclimb_backoff:{max:3, parallel:4},
    zero_deps:true,
    ssot:"bundles/coordination/active-tasks.md ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64 per 2026-08-13 22:09 CT",
    guard_ref:"bundles/scripts/all-lanes-busy-guard.js v5.1",
    tool_ref:"bundles/scripts/board_sync.py zero-deps stdlib only triple-write",
    triple_write:["workspace/.scout/missions/_cron/timeline.jsonl","bundles/ultra/runs/board-sync/timeline.jsonl","goals/refine-dottie-scout-cli-dumbmodel-com-with-vector-models/hidden_files/board-sync-status.jsonl"],
    required_fields_spec:["nodeId","agentId","attempt","latency_ms","tokens_est","status","errorClass"],
    version:"1.2",
    zero_deps:true,
    free_platform:"everything free for users — profitability via own calibrated edge private 0.25Kelly 1% day kill-switch",
    free_slots_formula:"free = 7 - non_gpu_active",
    no_swarm_condition:"free_slots <= 0 → no-op <5s log mandatory 7-field nodeId hillclimb-loop attempt latency_ms tokens_est status errorClass all_lanes_busy"
  },
  check:(activeTasks)=>{
    const nonGpu=activeTasks.filter(t=>!t.agent?.includes("LOCAL-GPU")&&!t.agent?.includes("LOCAL_GPU")).length;
    const gpu=activeTasks.filter(t=>t.agent?.includes("LOCAL-GPU")).length;
    const free=7-nonGpu;
    return {nonGpu,gpu,free,full:nonGpu>=7,total:activeTasks.length,ssot_ok:activeTasks.length<=15};
  },
  action:"clear stale >4h sweep one-per-tick 4h00m51s >4h move DONE recent preserve 3 LOCAL-GPU exempt never cleared sync COORDINATION.md to 7 repos + root push branch scout/board-sync- triple-write 7-field mandatory nodeId hillclimb-loop",
  guardLogic:`
    if (non_gpu_active >= 7) {
      // 0 free = no swarm per v5.1 Guard
      log 7-field {nodeId:"hillclimb-loop", agentId:"operator", attempt:1, latency_ms:<5s, tokens_est:0, status:"no-op", errorClass:"all_lanes_busy", non_gpu_active, gpu_exempt:3, free_slots:0, stale_cleared:0}
      return no-swarm;
    }
    free_slots = 7 - non_gpu_active;
    // stale detection >4h (>14400000 ms) exempt LOCAL-GPU
    // claim one free lane if READY exists in TODO.md
    // sync mirrors
  `,
  zero_deps:true,
  free_platform:"everything free-access single subtle footer Built free · Open-source · No paywall",
  gated_honesty:"MAE 0.2313 vs SOTA 0.2085 no fake promo comp0.809 honest SIGTERM 167s epoch0 14.4k 60ep OOMGuard LOCAL-GPU offload"
};
