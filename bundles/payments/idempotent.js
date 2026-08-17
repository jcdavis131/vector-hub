// bundles/payments/idempotent.js — Phase0 idempotent $0 ledger zero-deps stdlib only
// LCG 20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars everyday chain
// Zero-deps true — Node crypto stdlib only, no pip/torch/Stripe network, local-first
const crypto = require('crypto');
const MAX_CACHE = 3;
const cache = new Map();
function idempotencyKey(email, plan) {
  const normEmail = String(email||'').trim().toLowerCase();
  const normPlan  = String(plan||'').trim().toLowerCase();
  const base = `${normEmail}|${normPlan}`;
  const full = crypto.createHash('sha256').update(base).digest('hex');
  const short = full.slice(0,16);
  return {full, short, base, normEmail, normPlan};
}
function fullIdempotencyKey(e,p){return idempotencyKey(e,p).full;}
function shortIdempotencyKey(e,p){return idempotencyKey(e,p).short;}
const kelly={fraction:0.25,max_position_pct:0.01,max_concurrent:3,paper:true,status:'PASS_GREEN',kellyFraction:0.25};
function touchCache(k){ if(!cache.has(k)) return; const v=cache.get(k); cache.delete(k); cache.set(k,v); }
function charge(email,plan){
  const {full,short,normEmail,normPlan}=idempotencyKey(email,plan);
  if(cache.has(short)){ touchCache(short); const ex=cache.get(short); return {cached:true,dedup:true,idempotency_key:full,idempotency_key_short:short,email:normEmail,plan:normPlan,amount:0,currency:'usd',status:'succeeded',phase:'phase0',kelly_guard:{...kelly,note:'cached dedup'},invoice:ex,zero_deps:true,local_first:true} }
  if(cache.size>=MAX_CACHE){ const oldest=cache.keys().next().value; cache.delete(oldest); }
  const invoice={idempotency_key:full,idempotency_key_short:short,email:normEmail,plan:normPlan,amount:0,currency:'usd',status:'succeeded',phase:'phase0',created_at:new Date().toISOString(),kelly_fraction:kelly.fraction,max_position_pct:kelly.max_position_pct,max_concurrent:kelly.max_concurrent,paper:true,lcg:'20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars'};
  cache.set(short,invoice);
  return {cached:false,dedup:false,idempotency_key:full,idempotency_key_short:short,email:normEmail,plan:normPlan,amount:0,currency:'usd',status:'succeeded',phase:'phase0',kelly_guard:{...kelly,note:'fresh $0 Kelley0.25'},invoice,zero_deps:true,local_first:true};
}
function getCache(){return Array.from(cache.entries()).map(([k,v])=>({short:k,full:v.idempotency_key||v.idempotency_key_short,email:v.email,plan:v.plan}));}
function getCacheStats(){return {size:cache.size,max:MAX_CACHE,keys:Array.from(cache.keys()),hit_target:0.9,lcg:'20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars'};}
function clearCache(){cache.clear();return {cleared:true,zero_deps:true};}
const LCG_BADGE='20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars';
const EVERYDAY_CHAIN='?daily=20260813&n=1/3/5 Solo1 Triple3 Full5 open→drag-map→Jordan→copy-link equal stars';
module.exports={idempotencyKey,fullIdempotencyKey,shortIdempotencyKey,charge,getCache,getCacheStats,clearCache,MAX_CACHE,kelly,ZERO_DEPS:true,NO_TORCH:true,LCG_BADGE,EVERYDAY_CHAIN,everyday_chain:EVERYDAY_CHAIN,same_link_same_stars:true};
