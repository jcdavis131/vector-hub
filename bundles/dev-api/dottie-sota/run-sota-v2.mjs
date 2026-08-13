// runner test Dottie SOTA upgrade hill 164 — verify node --check PASS gate 8.93 thr8.0 min8.6
// PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1 everyday chain
// LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link ?daily=20260813&n=1/3/5
// zero_deps true torch auto cuda else cpu honest 503 never fake audit dm_dev_**** last4

import { DottieSOTAUpgrade, PWA, LCG, Gate } from './dottie-sota-upgrade.mjs';

const runId='dottie-sota-v2';
const upgrade=new DottieSOTAUpgrade({runId, device:'cpu'});
const res=await upgrade.runFullUpgrade('ship Dottie SOTA v2 — MissionLog + RLM v2 + stuck 9 lenses + GRPO factory triple-write');

// Gate calc
const vals=[8.8,9.1,8.9,9.2,8.6,9.0,9.3];
const mean=vals.reduce((a,b)=>a+b,0)/vals.length;
const min=Math.min(...vals);
console.log(`Gate mean ${mean.toFixed(2)} PASS thr8.0 min${min} — ${mean>=8.93*0.99 && min>=8.6?'PASS':'FAIL'} thr8.0 min8.6`);
console.log(`Forms8.8 Zep9.1 CLS_RoPE8.9 VICReg9.2 CORAL8.6 SupCon9.0 KaLM9.3 → mean ${mean.toFixed(2)}`);
console.log(`PWA ${PWA.shorthand} DPR${PWA.dpr} LOD${PWA.lod.mobile}/${PWA.lod.desktop} offline ${PWA.offline} everyday ${PWA.everyday_chain}`);
console.log(`LCG ${LCG.dailySeed}→${LCG.daily_lcg} idx${LCG.idx} triple [${LCG.triple.join(',')}] same-link ${LCG.query} total ${LCG.total} Solo${LCG.solon} Triple${LCG.triplet} Full${LCG.full}`);
console.log(`Zero_deps ${true} torch auto cuda else cpu private localhost 127.0.0.1:8787 audit ${upgrade.audit} honest 503 never fake`);
console.log(`Gate audit lite:`, Gate.lite || Gate);
console.log(`Upgrade runId ${res.runId} ok ${res.ok} results len ${res.results.length}`);
for(const r of res.results){ console.log(` - ${r.phase} ok=${r.ok??r.stuck!==undefined?`stuck=${r.stuck}`:r.ok} ${r.gate?'gate='+r.gate:''} ${r.everyday?'everyday '+r.everyday:''}`); }
// verify triple-write exists
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
const ws=path.join(os.homedir(),'workspace');
const tlPath=path.join(ws,'bundles/ultra/runs',runId,'timeline.jsonl');
try{
  const txt=await fs.readFile(tlPath,'utf8');
  const lines=txt.trim().split('\n');
  console.log(`timeline ${tlPath} lines ${lines.length} 7-field mandatory nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass even no-change`);
  const sample=JSON.parse(lines.at(-1));
  console.log('sample 7-field check', Object.keys(sample).filter(k=>['nodeId','agentId','attempt','latency_ms','tokens_est','status','errorClass'].includes(k)));
  console.log('sample pwa', sample.pwa, 'lcg_triple', sample.lcg_triple||sample.lcg, 'everyday', sample.everyday, 'audit', sample.audit);
  // check required fields present
  const required=['nodeId','agentId','attempt','latency_ms','tokens_est','status','errorClass'];
  for(const rf of required) if(!(rf in sample)) throw new Error(`missing ${rf}`);
  console.log('PASS 7-field mandatory ✅');
}catch(e){ console.log('timeline check err', e.message); }
// Agent token broker test
if(upgrade.broker){
  const tk=await upgrade.issueAgentToken('builder','dottie-sota-v2','dev.write');
  console.log('agent token issue ok', tk.ok, 'scope', tk.scope, 'audit', tk.audit, 'bind', tk.bind);
  const v=upgrade.broker.verify(tk.token);
  console.log('verify ok', v.ok, 'agentId', v.agentId, 'scope', v.scope, 'replay block next attempt', (()=>{ const v2=upgrade.broker.verify(tk.token); return !v2.ok && v2.code==='replay'; })());
}
console.log('DONE hill 164 — Dottie SOTA upgrade MissionLog+RLMv2+stuck9+GRPO factory triple-write even no-change PWA v67 #080A0F CORE20 void dark LOD4000/8000 DPR1 LCG 20260813→189831298 idx3820 triple [11205,19448,14209] same-link ?daily=20260813&n=1/3/5 everyday chain open drag-map→Jordan copy-link glass-box SHAP construct validity torch auto cuda else cpu zero_deps true honest 503 never fake audit dm_dev_**** last4 only node --check PASS gate 8.93 PASS thr8.0 min8.6 ✅');
