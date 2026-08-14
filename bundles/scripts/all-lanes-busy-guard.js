/**
 * all-lanes-busy-guard.js v5.1 — max7 non-GPU 3 GPU exempt never cleared free=7-non_gpu 0=no-swarm <5s 7-field
 * zero-deps stdlib only via node (but pure js logic zero-deps)
 */
module.exports={
  id:"all-lanes-busy-guard",
  version:"5.1",
  v51:{
    maxNonGPU:7,
    exemptGPU:3,
    freeFormula:"free = 7 - non_gpu_active",
    noSwarmCondition:"free<=0 → no-op <5s",
    required_fields:["nodeId","agentId","attempt","latency_ms","tokens_est","status","errorClass"],
    tags:["always-on","operator","v5.1","guard","sync"],
    tempo:":05",
    conf:0.82,
    hillclimb_backoff:{max:3, parallel:4},
    zero_deps:true,
    ssot:"bundles/coordination/active-tasks.md ≤15 rows claimed/todo 3 LOCAL-GPU exempt hoops-v6 150ep composite 0.7937→0.85 top1 0.438→0.55 gridiron 32-d MAE 4.268→3.8 unified G2 0.685→0.64 per 2026-08-13 22:09 CT",
    free_platform:"everything free-access single subtle footer Built free · Open-source · No paywall",
    free_slots_formula:"free = 7 - non_gpu_active",
    no_swarm:"0 free = no swarm log no-op <5s mandatory 7-field timeline nodeId hillclimb-loop"
  },
  check:(activeTasks)=>{
    const nonGpu=activeTasks.filter(t=>!t.agent?.includes("LOCAL-GPU")&&!t.agent?.includes("LOCAL_GPU")).length;
    const gpu=activeTasks.filter(t=>t.agent?.includes("LOCAL-GPU")).length;
    const free=7-nonGpu;
    return {nonGpu,gpu,free,full:nonGpu>=7,total:activeTasks.length,ssot_ok:activeTasks.length<=15};
  }
};
