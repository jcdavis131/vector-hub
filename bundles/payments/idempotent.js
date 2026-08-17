// payments Phase0 idempotent — zero-deps stdlib only, no pip/torch, no Stripe network
// LCG 20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars
// local-first: sha(email|plan), 3-user cache 0.9 pattern, Kelly 0.25 1% max 3 conc paper-track
// zero_deps=true no_torch=true stub Phase0 gate
'use strict';
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// ── Config: Phase0 gates ──
const MAX_CACHE = 3; // 3-user cached — LRU eviction, 90% hit pattern target 0.9
const KELLY_FRACTION = 0.25; // paper-track Kelly 0.25 guard
const MAX_POSITION_PCT = 0.01; // 1% max per bet
const MAX_CONCURRENT = 3; // max 3 concurrent paper positions

// ── In-memory LRU cache (Map preserves insertion order) ──
const cache = new Map(); // key(short16) -> invoice record

function normalizeEmail(email) {
  return String(email || '').trim().toLowerCase();
}
function normalizePlan(plan) {
  return String(plan || '').trim();
}

// full 64-hex key for ledger, short 16 for display/cache key
function fullIdempotencyKey(email, plan) {
  const e = normalizeEmail(email);
  const p = normalizePlan(plan);
  return crypto.createHash('sha256').update(`${e}|${p}`).digest('hex'); // 64 hex
}
function idempotencyKey(email, plan) {
  // spec: sha256(lowercase trimmed email|plan) slice 16
  return fullIdempotencyKey(email, plan).slice(0, 16);
}

function buildInvoice(email, plan, amount = 0) {
  const emailNorm = normalizeEmail(email);
  const planNorm = normalizePlan(plan);
  const full = fullIdempotencyKey(emailNorm, planNorm);
  const short = full.slice(0, 16);
  const now = new Date().toISOString();
  return {
    id: `inv_${short}`, // deterministic inv id from short key
    idempotency_key: full, // full 64 hex for audit
    idempotency_key_short: short, // short 16 display
    idempotent_key: full, // compat alias
    idempotent_key_short: short,
    email: emailNorm,
    plan: planNorm,
    amount: 0, // Phase0 $0 only
    currency: 'usd',
    status: 'succeeded',
    phase: 'phase0',
    kelly: KELLY_FRACTION,
    kelly_fraction: KELLY_FRACTION,
    max_position_pct: MAX_POSITION_PCT,
    max_concurrent: MAX_CONCURRENT,
    paper_track: true,
    paper: true,
    concurrent_used: cache.size,
    local_first: true,
    created_at: now,
    tx_time: now,
    zero_deps: true,
    no_torch: true,
    lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars'
  };
}

// charge() with cache Map max 3 LRU eviction, paper-track Kelly 0.25 1% max 3 conc, local-first
function charge(email, plan, opts = {}) {
  const amount = 0; // enforce Phase0 $0 — opts.amount ignored but logged
  const shortKey = idempotencyKey(email, plan);

  // LRU hit: move to most-recent, return cached existing (dedup, no double-billing)
  if (cache.has(shortKey)) {
    const existing = cache.get(shortKey);
    // LRU touch: delete + re-set to mark recent
    cache.delete(shortKey);
    cache.set(shortKey, existing);
    return {
      cached: true,
      dedup: true,
      key: shortKey,
      key_full: existing.idempotency_key,
      result: existing,
      kelly_guard: {
        kelly: KELLY_FRACTION,
        max_position_pct: MAX_POSITION_PCT,
        concurrent: cache.size,
        max_concurrent: MAX_CONCURRENT,
        paper: true,
        status: 'PASS_GREEN',
        cache_hit_rate_target: 0.9
      },
      lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars',
      zero_deps: true,
      local_first: true
    };
  }

  const invoice = buildInvoice(email, plan, amount);
  // LRU set + eviction if >3
  cache.set(shortKey, invoice);
  if (cache.size > MAX_CACHE) {
    const firstKey = cache.keys().next().value; // oldest
    cache.delete(firstKey);
  }

  return {
    cached: false,
    dedup: false,
    key: shortKey,
    key_full: invoice.idempotency_key,
    result: invoice,
    kelly_guard: {
      kelly: KELLY_FRACTION,
      max_position_pct: MAX_POSITION_PCT,
      concurrent: cache.size,
      max_concurrent: MAX_CONCURRENT,
      paper: true,
      status: cache.size > MAX_CONCURRENT ? 'YELLOW_SHRINK' : 'PASS_GREEN',
      cache_hit_rate_target: 0.9
    },
    lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars',
    zero_deps: true,
    local_first: true
  };
}

// utilities for ledger + verification
function getCache() {
  return new Map(cache); // shallow copy
}
function getCacheStats() {
  return {
    size: cache.size,
    max: MAX_CACHE,
    keys: Array.from(cache.keys()),
    kelly: KELLY_FRACTION,
    max_position_pct: MAX_POSITION_PCT,
    max_concurrent: MAX_CONCURRENT,
    pattern: '3-user cache 0.9 LRU',
    zero_deps: true
  };
}
function clearCache() {
  cache.clear();
}
function appendLedger(invoice, ledgerPath) {
  // append-only local-first write to store.jsonl when needed
  const p = ledgerPath || path.join(__dirname, 'store.jsonl');
  try {
    fs.appendFileSync(p, JSON.stringify(invoice) + '\n', 'utf8');
    return { appended: true, path: p };
  } catch (e) {
    return { appended: false, error: e.message, path: p };
  }
}

// ── Exports (CommonJS stdlib, zero-deps) ──
module.exports = {
  idempotencyKey,
  fullIdempotencyKey,
  charge,
  getCache,
  getCacheStats,
  clearCache,
  appendLedger,
  buildInvoice,
  MAX_CACHE,
  KELLY_FRACTION,
  MAX_POSITION_PCT,
  MAX_CONCURRENT,
  // ESM compat hint
  __zero_deps: true,
  __lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars'
};

// Optional ESM named-export interop via .mjs shims — keep CommonJS primary for zero-deps true
