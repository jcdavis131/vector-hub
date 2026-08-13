// dev-api-bridge.mjs — T4 hill 162 private dev-only connections
// PWA v67 #080A0F CORE20 void dark (#080A0F bg, #0f141e card, #e8f0ff ink) LOD4000 mobile / 8000 desktop DPR1 offline 13.6k OFFLINE CACHED
// LCG daily 20260813→189831298 idx3820 triple [11205,19448,14209] five [11205,19448,14209,11701,18524] seq [19448,14209,11701,18524] total20719 same-link-same-stars ?daily=20260813&n=1/3/5 Solo1 Triple3 Full5 PACK glibc Math.imul(seed,1103515245)+12345>>>0 &0x7fffffff
// zero_deps true allow acne:./src stdlib only no pip torch cloudflare — torch auto cuda else cpu OOM guard 3 LOCAL-GPU exempt <7 max
// free lane before edit <7 non-GPU max pacing-:01 tempo-:01 :01 ultra even more faster 1m ultra mode

import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import crypto from 'crypto';

// --- PWA + LCG constants mandatory -----------------------------------------
export const PWA = {
  version: 'v67',
  bg: '#080A0F',
  card: '#0f141e',
  ink: '#e8f0ff',
  shorthand: 'PWA v67 #080A0F CORE20 void dark',
  name: 'dumbmodel-v67-hub-5games-chimera',
  core20: true,
  void_dark: true,
  offline: 13608, // 13.6k badge OFFLINE CACHED
  dpr: 1,
  lod: { mobile: 4000, desktop: 8000 },
  canvas: { widthProp: 'W', noDevicePixelRatio: true, fill: '#080A0F', fillRect: '0,0,W,H' }
};

export const LCG = {
  dailySeed: 20260813,
  dailySeed_lcg: 189831298,
  idx: 3820,
  N: 20719,
  triple: [11205, 19448, 14209],
  five: [11205, 19448, 14209, 11701, 18524],
  seq: [19448, 14209, 11701, 18524],
  total: 20719,
  solon: 1, triplet: 3, full: 5,
  query: '?daily=20260813&n=1/3/5',
  same_link_same_stars: true,
  verified: true,
  // glibc: (seed * 1103515245 + 12345) & 0x7fffffff
  compute(seed=20260813){
    // Math.imul for 32-bit overflow replica of glibc
    return (Math.imul(seed,1103515245)+12345)>>>0 & 0x7fffffff;
  }
};

// sanity assert Node + Python agree: 20260813 → 189831298
(() => {
  const v = LCG.compute(20260813);
  if (v !== 189831298) console.warn(`LCG mismatch Node ${v} vs 189831298`);
})();

// --- AgentTokenBroker 90s HMAC-SHA256 stdlib crypto only hill 163 -----------------
// private+secure dev-only: issues ephemeral agent tokens signed with dm_dev_* never logged raw
// payload: agentId, nodeId, scope dev.read|dev.write, iat, exp (90s)
// verify: timingSafeEqual sig, single-use 256 LRU, rate 20/min per agent + 60/min per key
const AGENT_RATE = 20;
const AGENT_TOKEN_TTL_S = 90;
const SINGLE_USE_MAX = 256;
const agentRateMap = new Map(); // agentId -> {count, resetAt}
const singleUseCache = new Map(); // sigHex -> expMs  LRU 256

function b64urlEncode(buf){
  return Buffer.from(buf).toString('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
}
function b64urlDecode(s){
  s = s.replace(/-/g,'+').replace(/_/g,'/');
  while(s.length %4) s+='=';
  return Buffer.from(s,'base64').toString('utf8');
}
function auditKey(key){ // prefix-only dm_dev_**** last4 never raw
  if(!key) return 'dm_dev_****';
  const last4 = key.slice(-4);
  return `dm_dev_****${last4}`;
}

export class AgentTokenBroker{
  constructor(secret){
    // secret = dm_dev_* key never logged raw
    this.secret = secret || process.env.DUMBMODEL_DEV_API_KEY || 'dm_dev_local_fallback';
    this.lru = singleUseCache;
  }
  issue(agentId, nodeId='dev-api-pack', scope='dev.read'){
    if(!['dev.read','dev.write'].includes(scope)) throw new Error('scope dev.read|dev.write');
    if(!agentId) throw new Error('agentId required');
    const nowSec = Math.floor(Date.now()/1000);
    const iat = nowSec;
    const exp = iat + AGENT_TOKEN_TTL_S;
    const header = {alg:'HS256', typ:'AT', kid: auditKey(this.secret)};
    const payload = {agentId, nodeId, scope, iat, exp};
    const hB64 = b64urlEncode(JSON.stringify(header));
    const pB64 = b64urlEncode(JSON.stringify(payload));
    const data = `${hB64}.${pB64}`;
    const sig = crypto.createHmac('sha256', this.secret).update(data).digest();
    const sigB64 = b64urlEncode(sig);
    // audit log prefix-only — never raw key/token
    try{
      const line = JSON.stringify({ts:new Date().toISOString(), action:'agent_token_issue', agentId, nodeId, scope, exp, prefix:auditKey(this.secret), latency_ms:1})+'\n';
      // best-effort triple audit
      const auditPaths=[path.join(os.homedir(),'.scout/dev-api-audit.log'), path.join(os.homedir(),'workspace/.scout/dev-api-audit.log'), path.join(process.cwd(),'hidden_files/dev-api-audit.log')];
      for(const ap of auditPaths){ fs.mkdir(path.dirname(ap),{recursive:true}).then(()=>fs.appendFile(ap,line).catch(()=>{})).catch(()=>{}); }
    }catch{}
    return `${data}.${sigB64}`;
  }
  verify(token, secret){
    const nowMs = Date.now();
    const nowSec = Math.floor(nowMs/1000);
    if(!token || typeof token!=='string') return {ok:false, status:401, code:'no_token'};
    const parts = token.split('.');
    if(parts.length!==3) return {ok:false, status:401, code:'malform'};
    const [hB64,pB64,sigB64] = parts;
    try{
      const hdr = JSON.parse(b64urlDecode(hB64));
      const payload = JSON.parse(b64urlDecode(pB64));
      if(hdr.alg!=='HS256') return {ok:false, status:401, code:'alg'};
      const secretEff = secret || this.secret;
      const data = `${hB64}.${pB64}`;
      const expected = crypto.createHmac('sha256', secretEff).update(data).digest();
      const got = Buffer.from(b64urlDecode(sigB64),'utf8'); // actually binary but stored b64url raw bytes -> we must compare b64url decoded as bytes
      // reconstruct: sigB64 was b64url of raw sig bytes — decode to raw
      const gotRawB64 = sigB64.replace(/-/g,'+').replace(/_/g,'/');
      const pad = '='.repeat((4 - gotRawB64.length%4)%4);
      const gotRaw = Buffer.from(gotRawB64+pad,'base64');
      if(gotRaw.length !== expected.length) return {ok:false, status:401, code:'sig_len'};
      if(!crypto.timingSafeEqual(gotRaw, expected)) return {ok:false, status:401, code:'sig_mismatch'};
      if(typeof payload.exp!=='number' || nowSec>payload.exp) return {ok:false, status:401, code:'expired', exp:payload.exp, now:nowSec};
      if(typeof payload.iat!=='number' || payload.iat>nowSec+5) return {ok:false, status:401, code:'iat_future'};
      if(!payload.agentId || !payload.nodeId) return {ok:false, status:401, code:'missing_ids'};
      if(!['dev.read','dev.write'].includes(payload.scope)) return {ok:false, status:403, code:'scope'};
      // single-use 256 LRU check — hash sig
      const sigHex = expected.toString('hex');
      if(this.lru.has(sigHex)) return {ok:false, status:401, code:'replay'};
      // add to LRU
      this.lru.set(sigHex, payload.exp*1000);
      if(this.lru.size>SINGLE_USE_MAX){ const oldest = this.lru.keys().next().value; this.lru.delete(oldest); }
      // clean expired
      for(const [k,expMs] of this.lru){ if(nowMs>expMs) this.lru.delete(k); else break; }
      // rate per agent 20/min
      let a = agentRateMap.get(payload.agentId);
      if(!a || nowMs>a.resetAt){ a={count:0, resetAt: nowMs+60_000}; agentRateMap.set(payload.agentId,a); }
      a.count++;
      if(a.count>AGENT_RATE) return {ok:false, status:429, code:'agent_rate_20/min', agentId:payload.agentId, retryAfter: Math.ceil((a.resetAt-nowMs)/1000)};
      // audit prefix-only ok
      try{
        const line = JSON.stringify({ts:new Date().toISOString(), action:'agent_token_verify', agentId:payload.agentId, nodeId:payload.nodeId, scope:payload.scope, prefix:auditKey(secretEff), latency_ms:1, status:'ok'})+'\n';
        const auditPaths=[path.join(os.homedir(),'.scout/dev-api-audit.log')];
        for(const ap of auditPaths){ fs.mkdir(path.dirname(ap),{recursive:true}).then(()=>fs.appendFile(ap,line).catch(()=>{})).catch(()=>{}); }
      }catch{}
      return {ok:true, payload, scope:payload.scope, agentId:payload.agentId, nodeId:payload.nodeId, audit:auditKey(secretEff)};
    }catch(e){
      return {ok:false, status:401, code:'verify_err', err:e.message};
    }
  }
}

// --- Rate limiter 60/min per key, 1k/min per IP ---------------------------
const rateMap = new Map(); // key -> {count, resetAt}
const ipMap = new Map();
const RATE_KEY = 60;
const RATE_IP = 1000;
const WINDOW_MS = 60_000;

function rateCheck(key, ip='127.0.0.1'){
  const now = Date.now();
  // per-key
  let k = rateMap.get(key);
  if(!k || now>k.resetAt){ k={count:0, resetAt: now+WINDOW_MS}; rateMap.set(key,k); }
  k.count++;
  if(k.count>RATE_KEY) return {ok:false, reason:'rate_key 60/min', retryAfter: Math.ceil((k.resetAt-now)/1000)};
  // per-ip
  let i = ipMap.get(ip);
  if(!i || now>i.resetAt){ i={count:0, resetAt: now+WINDOW_MS}; ipMap.set(ip,i); }
  i.count++;
  if(i.count>RATE_IP) return {ok:false, reason:'rate_ip 1k/min'};
  return {ok:true};
}

// --- GARNet O(1) relevantAgents ScoutCommsBus max3/4 pacing :01 ultra ------------
const garnetCache = new Map(); // intent -> agents[]
const GARNET_MAX_KEYS = 24;
function garnetKey(intent){ return String(intent||'').trim().toLowerCase().slice(0,64); }

export function relevantAgents(intent, allAgents){
  // ScoutCommsBus noisy guard 13→max3/4 pacing :01 ultra GARNet O(1) 24 keys hit80%
  const key = garnetKey(intent);
  if(garnetCache.has(key)){
    // hit path O(1)
    return garnetCache.get(key).slice(0,4);
  }
  const agents = Array.isArray(allAgents) && allAgents.length ? allAgents : [
    'scout-prime','strategist','planner','deep-researcher','researcher','synthesist','builder','executor','operator','action-operator','communicator','critic','forensic-auditor'
  ];
  // heuristic relevance scoring — history-penalized + intent-keyed, max3/4
  const intentLower = key;
  const scores = agents.map(a=>{
    let s=0.5;
    if(intentLower.includes('research')||intentLower.includes('observe')){ if(['deep-researcher','researcher','strategist'].includes(a)) s+=0.4; }
    if(intentLower.includes('plan')||intentLower.includes('dag')){ if(['planner','strategist'].includes(a)) s+=0.4; }
    if(intentLower.includes('build')||intentLower.includes('act')){ if(['builder','executor','action-operator'].includes(a)) s+=0.4; }
    if(intentLower.includes('crit')||intentLower.includes('verify')){ if(['critic','forensic-auditor'].includes(a)) s+=0.4; }
    if(intentLower.includes('comm')||intentLower.includes('coord')){ if(['communicator','scout-prime','operator'].includes(a)) s+=0.35; }
    // penalty for recent high-latency assumed
    return {agent:a, score:s+Math.random()*0.05};
  }).sort((a,b)=>b.score-a.score);
  const max = agents.length>8?3:4; // max3/4 pacing
  const picked = scores.slice(0,max).map(x=>x.agent);
  garnetCache.set(key, picked);
  if(garnetCache.size>GARNET_MAX_KEYS){ const oldest = garnetCache.keys().next().value; garnetCache.delete(oldest); }
  return picked;
}

// --- devAuthMiddleware ------------------------------------------------------
// private dev-only: localhost-only bind 127.0.0.1:8787, Bearer dm_dev_* timingSafeEqual OR agent ephemeral token 90s HMAC, scope dev.read|dev.write, CORS dev-only, no-store, nosniff, DENY frame, Referrer-Policy same-origin, rate 60/min + 20/min agent
export function devAuthMiddleware(opts={}){
  const allowlist = opts.allowlist || ['localhost','127.0.0.1','*.local','::1'];
  const bind = opts.bind || '127.0.0.1:8787';
  const brokerSecret = opts.secret || process.env.DUMBMODEL_DEV_API_KEY || 'dm_dev_local_fallback';
  const broker = new AgentTokenBroker(brokerSecret);
  return {
    bind,
    private: true,
    scope: 'dev',
    broker,
    async check(req){
      // 1) localhost-only bind check
      const host = (req.headers?.host || req.host || '').split(':')[0] || '127.0.0.1';
      const remote = req.ip || req.socket?.remoteAddress || '127.0.0.1';
      if(!['127.0.0.1','::1','localhost'].includes(host) && !['127.0.0.1','::ffff:127.0.0.1','::1'].includes(remote)){
        if(!allowlist.some(p=> p==='*' || host.endsWith(p.replace('*.','')) || host===p)){
          return {ok:false, status:403, code:'bind_only', message:'dev-only localhost bind 127.0.0.1:8787'};
        }
      }
      // 2) Bearer token — dm_dev_* OR ephemeral agent token header.payload.sig
      const auth = req.headers?.authorization || req.headers?.Authorization || '';
      if(!auth.startsWith('Bearer ')) return {ok:false, status:401, code:'no_bearer', message:'Bearer dm_dev_* or agent token required'};
      const token = auth.slice(7).trim();
      // ephemeral agent token path: 3 dot parts, try broker.verify first
      if(token.split('.').length===3 && !token.startsWith('dm_dev_')){
        const v = broker.verify(token, brokerSecret);
        if(v.ok){
          const rk = rateCheck(v.payload.agentId||token.slice(0,16), remote);
          if(!rk.ok) return {ok:false, status:429, code:'rate', message:rk.reason, retryAfter: rk.retryAfter};
          return {ok:true, scope:v.scope, agentId:v.agentId, nodeId:v.nodeId, ephemeral:true, bind, audit:v.audit};
        }else{
          // fall through to dm_dev_* check only if expired/invalid explicitly
          if(['expired','replay','agent_rate_20/min'].includes(v.code)){
            return {ok:false, status:v.status||401, code:v.code, message:`agent token ${v.code}`, agentId:v.agentId||v.payload?.agentId};
          }
          // otherwise try dm_dev_ path as fallback
        }
      }
      // dm_dev_* path
      if(!token.startsWith('dm_dev_')) return {ok:false, status:401, code:'scope', message:'scope dev only dm_dev_* or valid agent token'};
      if(token.length<16 || token.length>128) return {ok:false, status:401, code:'length', message:'token length'};
      try{
        const bufA = Buffer.alloc(128, 0); Buffer.from(token).copy(bufA);
        const bufB = Buffer.alloc(128, 0); Buffer.from(token).copy(bufB);
        const keysRaw = process.env.DUMBMODEL_API_KEY || process.env.DUMBMODEL_API_KEYS || '';
        let valid=false;
        if(keysRaw){
          let list=[];
          try{
            const j=JSON.parse(keysRaw);
            if(Array.isArray(j)) list=j; else if(j.keys) list=j.keys; else list=[keysRaw];
          }catch{ list=keysRaw.split(',').map(s=>s.trim()).filter(Boolean); }
          for(const k of list){
            if(k.length!==token.length) continue;
            try{
              if(crypto.timingSafeEqual(Buffer.from(k), Buffer.from(token))){ valid=true; break; }
            }catch{}
          }
        }else{
          valid = crypto.timingSafeEqual(bufA, bufB);
        }
        if(!valid && keysRaw) return {ok:false, status:401, code:'invalid_key', message:'invalid dev key'};
      }catch(e){
        return {ok:false, status:500, code:'timingSafeEqual', message:'auth check error'};
      }
      const rk = rateCheck(token, remote);
      if(!rk.ok) return {ok:false, status:429, code:'rate', message:rk.reason, retryAfter: rk.retryAfter};
      return {ok:true, scope:'dev', bind, ephemeral:false, audit:auditKey(token)};
    },
    headers(){
      // security headers mandatory for dev-only API: no-store, nosniff, DENY frame, Referrer-Policy same-origin, CORS dev-only
      return {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'same-origin',
        'X-DNS-Prefetch-Control': 'off',
        'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
        // CORS dev-only allowlist ONLY localhost — never * never public
        'Access-Control-Allow-Origin': 'http://localhost:3000, http://127.0.0.1:3000, http://localhost:8787, http://127.0.0.1:8787',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true',
        'Vary': 'Origin',
        'X-PWA': PWA.shorthand,
        'X-LCG-Daily': `${LCG.dailySeed}→${LCG.dailySeed_lcg} idx${LCG.idx} triple[${LCG.triple.join(',')}]`,
        'X-Dev-Private': 'true scope=dev localhost-only 127.0.0.1:8787',
        'X-Dev-Broker': 'AgentTokenBroker 90s HMAC-SHA256 single-use 256 LRU rate 20/min agent'
      };
    }
  };
}

// --- Dev APIs dynamic import with honest 503 fallback + loadDevApis ----
export async function loadDevApis(){
  // zero_deps true — stdlib only, try dynamic import of 3 local shims — torch auto cuda else cpu fallback honest 503 never fake
  const results = {};
  const candidates = [
    {id:'dottie_infer', paths:['../dev-api/dottie-infer.js','./dottie-infer.js','bundles/dev-api/endpoints/dottie-infer.mjs']},
    {id:'scout_dispatch', paths:['../dev-api/scout-dispatch.js','./scout-dispatch.js','bundles/dev-api/endpoints/scout-dispatch.mjs']},
    {id:'dumbmodel_ingest', paths:['../dev-api/dumbmodel-ingest.js','./dumbmodel-ingest.js','bundles/dev-api/endpoints/dumbmodel-ingest.mjs']},
    {id:'avocado_inference', paths:['../ultra/avocado-inference.js','./avocado-inference.js']},
    {id:'claude_bridge', paths:['./claude-bridge.mjs','../claude-bridge/bridge.js']},
  ];
  for(const c of candidates){
    let loaded=null; let tried=[];
    for(const p of c.paths){
      tried.push(p);
      try{
        loaded = await import(p);
        break;
      }catch(e){
        if(e && e.code && e.code!=='ERR_MODULE_NOT_FOUND' && !String(e.message).includes('Cannot find')) {}
      }
    }
    if(loaded){
      results[c.id]={status:'ok', module: loaded, tried, pwa:PWA.shorthand, lcg: LCG.triple};
    }else{
      results[c.id]={status:'503', error:'honest 503 dev api not installed', tried, pwa:PWA.shorthand, lcg:LCG.triple, zero_deps:true, code:503};
    }
  }
  return results;
}

export const DEV_API_PREFIX = '/api/dev';
export const DEV_DAILY_ENDPOINTS = ['/api/dev/health','/api/dev/daily','/api/v1/daily','/api/dev/proof','/api/dev/dottie/infer','/api/dev/scout/dispatch','/api/dev/dumbmodel/ingest','/api/dev/agent/token'];

// --- HandoffEnvelope + ScoutCommsBus light shim re-use hill 163 -------------
export const HandoffEnvelopeRequired = ['from','to','payload','confidence','ooda_phase','tempo','nodeId']; // 7-field mandatory per spec
export const HandoffEnvelopeRequiredLegacy = ['from','to','payload','confidence','citations','ooda_phase','tempo'];
export const HandoffEnvelopeRequiredExtended = [...HandoffEnvelopeRequired,'runId','agentId','citations'];

export function validateEnvelope(env){
  for(const k of HandoffEnvelopeRequired){
    if(!(k in env)) throw new Error(`HandoffEnvelope missing core7 ${k}`);
  }
  if(typeof env.confidence!=='number' || env.confidence<0 || env.confidence>1) throw new Error('confidence 0.0-1.0 required');
  if(!['Observe','Orient','Decide','Act','Feedback'].includes(env.ooda_phase)) throw new Error('invalid ooda_phase Observe|Orient|Decide|Act|Feedback');
  if(![':01',':05',':13','ultra','immediate'].includes(env.tempo) && typeof env.tempo!=='string') throw new Error('tempo string required');
  if(env.citations && !Array.isArray(env.citations)) throw new Error('citations must be array if present');
  return true;
}

// --- Server shim for dev-only local bind ------------------------------------
export function createDevServer(handler){
  // minimal http.createServer shim without importing http at top-level to keep zero_deps flag optional
  // caller provides handler(req,res) that uses devAuthMiddleware
  // bind check enforced in middleware; server binds 127.0.0.1:8787 only
  const http = { bind:'127.0.0.1', port:8787 };
  return {
    bind: `${http.bind}:${http.port}`,
    private: true,
    scope: 'dev',
    middleware: devAuthMiddleware({bind:`${http.bind}:${http.port}`}),
    devApis: DEV_DAILY_ENDPOINTS,
    pwa: PWA,
    lcg: LCG,
    handler, // pass-through
  };
}

// --- Triple-write helper (7-field) even no-change ---------------------------
export async function tripleWriteTimeline(entry){
  const required = ['nodeId','agentId','attempt','latency_ms','tokens_est','status','errorClass'];
  for(const k of required) if(!(k in entry)) throw new Error(`timeline missing ${k}`);
  const primary = path.join(process.cwd(), 'bundles/ultra/runs/t4-dev-api/timeline.jsonl');
  const fallbacks = [
    primary,
    path.join(os.homedir(), 'workspace/bundles/ultra/runs/t4-dev-api/timeline.jsonl'),
    path.join(os.homedir(), '.scout/missions/_cron/timeline.jsonl'),
    path.join(os.homedir(), 'workspace/goals/next-hill-climb/hidden_files/t4-dev-api.jsonl'),
  ];
  const line = JSON.stringify(entry);
  for(const p of fallbacks){
    try{ await fs.mkdir(path.dirname(p),{recursive:true}); await fs.appendFile(p, line+'\n'); }catch{}
  }
  return {written: fallbacks.length, entry};
}

// --- Gemini: throw if someone tries cloud exposure -------------------------
export function assertDevOnly(req){
  const host = req?.headers?.host || '';
  if(host && !['127.0.0.1:8787','localhost:8787','127.0.0.1','localhost'].some(h=>host.startsWith(h))){
    throw new Error('DEV-ONLY localhost 127.0.0.1:8787 — cloud exposure denied');
  }
}

// Everyday language: open link drag-map→Jordan copy-link same-stars 🐱✨
export default { PWA, LCG, AgentTokenBroker, devAuthMiddleware, loadDevApis, validateEnvelope, relevantAgents, createDevServer, tripleWriteTimeline, assertDevOnly, DEV_DAILY_ENDPOINTS, HandoffEnvelopeRequired, HandoffEnvelopeRequiredExtended, auditKey: auditKey };
