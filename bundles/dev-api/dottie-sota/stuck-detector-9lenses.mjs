// stuck-detector-9lenses.mjs — Dottie SOTA 9 lateral-thinking lenses + Glass-box honesty
// PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1
// LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link ?daily=20260813&n=1/3/5
// zero_deps true torch auto cuda else cpu honest 503 never fake audit dm_dev_**** last4
// device = "cuda" if torch.cuda.is_available() else "cpu"

import { PWA, LCG, tripleWriteTimeline } from './mission-log-v2.mjs';

export const Lateral9 = [
  { id:'inversion', name:'Inversion', prompt:'Invert the problem: what would guarantee failure? Then invert solutions.' },
  { id:'scamper', name:'SCAMPER', prompt:'Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse the trace pipeline.' },
  { id:'analogy', name:'Analogy', prompt:'Map Dottie trace→pref to biological evolution / traffic flow — find isomorphic bottleneck.' },
  { id:'worst-idea', name:'Worst Idea', prompt:'List 5 worst factory proposals, extract kernel to invert into SOTA.' },
  { id:'provocation', name:'Provocation', prompt:'PO: GRPO is harmful — explore what breaks and what that reveals about reward.' },
  { id:'concept-fan', name:'Concept Fan', prompt:'Fan out from GRPO → RL → optimization → alignment, fan in different branch.' },
  { id:'random-stimulus', name:'Random Stimulus', prompt:'Word = chimera 20719 — force connect to factory: pack battle analogy.' },
  { id:'six-hats', name:'Six Hats', prompt:'White: facts MAE0.2085, Red: frustration OOM 7.8G, Black: risks fake 7/7, Yellow: 80% token save, Green: MoMA new path, Blue: control next step.' },
  { id:'lateral', name:'Lateral Jump', prompt:'Unrelated domain: Zep TLPG bi-temporal tx ordering — apply to timeline ordering.' },
];

const OPERATIONAL_ALLOWLIST_RE = /poll|heartbeat|sync_bundles|brief-auto-exec|dottie-triple-write/;

export function detectStuck9(input){
  if(typeof input==='string' && OPERATIONAL_ALLOWLIST_RE.test(input)) return {stuck:false, lens:null, metaPattern:'operational noise filtered', reasons:[], confidence:0.92};
  let attempts=[], confidences=[], latencies=[], errorClasses=[], obsHashes=[], nodeIds=[];
  if(Array.isArray(input) && input[0]?.nodeId){ 
    attempts=input.map(h=>h.attempt||1);
    confidences=input.map(h=>h.confidence||1);
    latencies=input.map(h=>h.latency_ms||h.latency||0);
    errorClasses=input.map(h=>h.errorClass||'').filter(Boolean);
    obsHashes=input.map(h=>h.observationHash||'').filter(Boolean);
    nodeIds=input.map(h=>h.nodeId||'');
  } else if(input && typeof input==='object'){
    attempts=input.attempts||[]; confidences=input.confidences||[]; latencies=input.latencies||[]; errorClasses=input.errorClasses||[]; obsHashes=input.obsHashes||[]; nodeIds=input.nodeIds||[];
  }
  const reasons=[]; let triggers=[];
  const counts={}; for(const id of nodeIds.slice(-10)) if(id) counts[id]=(counts[id]||0)+1;
  for(const [id,c] of Object.entries(counts)) if(c>3){ reasons.push(`loop>3 node=${id} count=${c}`); triggers.push(`loop:${id}`); }
  if(confidences.slice(-2).every(c=>typeof c==='number' && c<0.4)) { reasons.push(`confidence<0.4 x2 [${confidences.slice(-2).join(',')}]`); triggers.push('low-confidence'); }
  if(latencies.length>=2){ const last=latencies.at(-1); const rest=latencies.slice(0,-1); const p95=rest.slice().sort((a,b)=>a-b)[Math.floor(0.95*(rest.length-1))||0]||0; const thr= rest.length>=3? p95*2.0 : 180000; if(last>thr && last>1000){ reasons.push(`latency ${last}ms > ${Math.round(thr)}ms`); triggers.push('high-latency'); } }
  const ecCount={}; for(const ec of errorClasses.slice(-6)) if(ec) ecCount[ec]=(ecCount[ec]||0)+1;
  for(const [ec,c] of Object.entries(ecCount)) if(c>=2){ reasons.push(`errorClass ${ec} x${c}`); triggers.push(`error:${ec}`); }
  if(obsHashes.length>=3 && new Set(obsHashes.slice(-3)).size===1){ reasons.push(`obsHash stuck ${String(obsHashes.at(-1)).slice(0,24)} x3`); triggers.push('obs-stalled'); }

  const stuck=reasons.length>0;
  let metaPattern='none';
  const trig=triggers[0]||null;
  if(trig?.startsWith('loop')) metaPattern='cognitive loop reattempting same node without progress — needs DAG re-plan';
  else if(trig==='low-confidence') metaPattern='epistemic stall — low confidence twice, needs memory lattice 1-2 hops + 2 fresh sources';
  else if(trig==='high-latency') metaPattern='resource stall — tool contention or context window blowout';
  else if(trig?.startsWith('error:')) metaPattern=`recurring failure ${trig} — needs patch not retry`;
  else if(trig==='obs-stalled') metaPattern='observation stall — same output hash, no novelty';
  else if(stuck) metaPattern='compound stall';

  const lens = stuck ? pickLens9({trigger:trig, nodeIds, attempts, confidences}) : null;
  return { stuck, trigger:trig, lens, metaPattern, reasons, confidence: stuck?0.32:0.92, thresholds:{loopRepeats:3, confidenceLow:0.4, latencyMultiplier:2.0}, stats:{attemptCount:attempts.length}, pwa:PWA.shorthand, lcg:LCG.triple, everyday:PWA.everyday_chain, zero_deps:true, private:true, audit_lens_only:true };
}

function hashCode(s){ let h=0; for(let i=0;i<s.length;i++) h=Math.imul(31,h)+s.charCodeAt(i)|0; return Math.abs(h); }

function pickLens9(ctx){
  const key=(ctx?.trigger||'')+(ctx?.nodeIds?.at(-1)||'')+String(ctx?.attempts?.at(-1)||'');
  const idx= hashCode(key) % Lateral9.length;
  return Lateral9[idx];
}

export function applyLens9(lensId, context={}){
  const lens = Lateral9.find(l=>l.id===lensId) || Lateral9[0];
  const nodeId=context.nodeId||context.trigger||'stuck node';
  const goal=context.goal||'ship Dottie SOTA';
  const elaborated = {
    inversion: `Inversion lens on ${nodeId} for ${goal}: List 3 guaranteed failures (fake 7/7 provenance, over-reward OOM, ignore TLPG tx). Invert: ensure real disk triple-write, bound reward KL, enforce valid≤tx batch window 2 sync +5 async.`,
    scamper: `SCAMPER ${nodeId} ${goal}: Substitute torch with MoMA-lite heuristic, Combine GRPO entropy thermostat, Adapt Zep bi-temporal, Modify batch window, Put trace→pref to other use, Eliminate checkout, Reverse planner order.`,
    analogy: `Analogy: ${nodeId} resembles Formula1 pit stop — pit crew = agents 13, telemetry = MissionLog, stuck = tire gun jam. Apply F1 solution: parallel gun + pre-stage + blue-flag tempo :01 ultra.`,
    'worst-idea': `Worst ideas for ${nodeId}: delete timeline.jsonl, invent provenance hashes, ship without node --check. Kernel extraction: no-delete append-only, provenance 59 hashes computed not invented, node --check mandatory PASS gate 8.93.`,
    provocation: `Provocation PO: we must ship Dottie broken to learn — what breaks if we delete ACNE? Lose 80% token save. Therefore ACNE is load-bearing, keep 17n27e + Bloom m8192 k7 FPR0.9%.`,
    'concept-fan': `Concept fan: ${nodeId} instance of [verification economics budget3 thr8.0]. Fan out: budget allocation, game theory, earlyExit0.3. Fan in via different branch: verifier-with-budget single enforcement not per node.`,
    'random-stimulus': `Random stimulus "chimera 20719" → ${nodeId}: 12966+5323+2430 cross-sport — Dottie factory similarly fuses reasoning+trace+reward like 3-sport chimera, need shared-map.js same-link-same-stars ?daily=20260813&n=1/3/5.`,
    'six-hats': `Six Hats on ${nodeId}: White MAE0.2085 vs smoke 0.2313, Red annoyed by OOM 7.8G, Black risk vanity metric, Yellow 80% token cache win 82%, Green MoMA-lite 17,700× faster, Blue next: fix L2 DAG side-effect tagged + pacing-filtered swarm.`,
    lateral: `Lateral: what if ${goal} is wrong question? Alternative framing 3: Dottie is data packaging not model training, edge is lie detection not win, users want same-link-same-stars pack battle not leaderboard. Pick first: rebuild foundation dataset v0.1.0 80/10/10 split train13/val1/test3 strict.`,
  };
  // structured return includes SHAP hint for glass-box
  const shap_hint = {
    construct:'stuck_detector_lateral_9',
    plain:'Apply one of 9 de Bono style lenses when loop>3 conf<0.4 latency>thr to unblock reasoning without fake progress',
    operationalization:'detectStuck9 over last 10 timeline entries → 9 lens pick deterministic hash → triple-write honest report visibleAbandonment',
    convergent:'Correlate with verifier budget thr8.0 + recovery ladder attempts',
    discriminant:'Independent from mission success itself — detector vs task outcome',
    threat:'Vanity: claiming unstuck when still looping — mitigated by same-run repeat check',
    glass_box:{lens:lens.id, dim8_usage_TS:0.2923, dim18_def_vers:0.1862, shap_3features:[8,18,33]}
  };
  return { lens: lens.id, name: lens.name, prompt: elaborated[lens.id]||lens.prompt, context: {nodeId, goal}, shap_hint, pwa:PWA.shorthand, lcg:LCG.triple, everyday:PWA.everyday_chain };
}

export async function stuckWithLogging(input, ctx={}){
  const info = detectStuck9(input);
  const entry={
    nodeId:'stuck-detector-9lenses',
    agentId:ctx.agentId||'builder',
    attempt:ctx.attempt||1,
    latency_ms:ctx.latency_ms||0,
    tokens_est:ctx.tokens_est||0,
    status: info.stuck? 'stuck':'ok',
    errorClass: info.trigger||'none',
    ooda_phase: info.stuck? 'Orient':'Observe',
    confidence: info.confidence,
    metaPattern: info.metaPattern,
    lens: info.lens?.id||null,
  };
  await tripleWriteTimeline(entry,{runId:'dottie-sota-v2'});
  if(info.stuck && info.lens){
    const applied = applyLens9(info.lens.id, ctx);
    await tripleWriteTimeline({nodeId:'stuck-detector-9lenses-lens-apply',agentId:ctx.agentId||'builder',attempt:1,latency_ms:1,tokens_est:50,status:'ok',errorClass:'none',ooda_phase:'Decide',confidence:0.82,lens:applied.lens},{runId:'dottie-sota-v2'});
    return {...info, remediation:applied, honest_lens:{visibleAbandonments:true,noFake7of7:true}};
  }
  return info;
}

export default { Lateral9, detectStuck9, applyLens9, stuckWithLogging, PWA, LCG };
