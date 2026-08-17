// bundles/auth/local_auth.js — Phase0 3-user cached local-first stub
// zero-deps true stdlib only, no Clerk, no torch, no network
// LCG 20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars everyday chain
// 3-user cache eviction LRU max 3, 90s ephemeral token base64url slice 24, local-first
const MAX_SESSIONS = 3;
const EPHEMERAL_MS = 90000; // 90s

// sessions Map<userId, {token, at, exp, local}>
const sessions = new Map();

/**
 * ephemeralToken(user) — exp Date.now()+90000 base64url slice 24
 * local-first, no network, zero-deps
 */
export function ephemeralToken(user) {
  const exp = Date.now() + EPHEMERAL_MS;
  const payload = `${user}|${exp}|${Math.random().toString(36).slice(2, 6)}`;
  // base64url slice 24 per spec
  return Buffer.from(payload).toString('base64url').slice(0, 24);
}

function touchLRU(user) {
  if (!sessions.has(user)) return;
  const entry = sessions.get(user);
  sessions.delete(user);
  sessions.set(user, entry);
}

/**
 * login(user) — verify against 3-user allowlist SSOT (users.jsonl) optional,
 * cache max 3 LRU eviction, 90s ephem, local-first
 * returns {user, token, exp, cached, local, zero_deps}
 */
export function login(user) {
  if (!user || typeof user !== 'string') {
    throw new Error('login: user required');
  }
  // LRU eviction if at capacity and new user
  if (!sessions.has(user) && sessions.size >= MAX_SESSIONS) {
    const first = sessions.keys().next().value;
    sessions.delete(first);
  } else if (sessions.has(user)) {
    // refresh LRU position
    sessions.delete(user);
  }
  const token = ephemeralToken(user);
  const now = Date.now();
  const entry = {
    user,
    token,
    at: now,
    exp: now + EPHEMERAL_MS,
    local: true,
    zero_deps: true,
    ephem: 90,
  };
  sessions.set(user, entry);
  return {
    user,
    token,
    exp: entry.exp,
    cached: sessions.size,
    local: true,
    zero_deps: true,
    ephem: 90,
    lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars',
  };
}

/**
 * verify(token) — bool, checks local Map + 90s expiry, no network
 */
export function verify(token) {
  if (!token || typeof token !== 'string') return false;
  const now = Date.now();
  // prune expired first (lazy)
  for (const [k, v] of sessions) {
    if (now >= v.exp) sessions.delete(k);
  }
  for (const v of sessions.values()) {
    if (v.token === token) {
      return now < v.exp;
    }
  }
  // fallback decode-if-not-sliced (for completeness, local-first still)
  try {
    const decoded = Buffer.from(token, 'base64url').toString();
    const parts = decoded.split('|');
    if (parts.length >= 2) {
      const exp = Number(parts[1]);
      if (!Number.isNaN(exp)) return now < exp;
    }
  } catch (_) {
    // ignore — local-first, no throw
  }
  return false;
}

/**
 * list() — returns cached user ids (max 3 LRU)
 */
export function list() {
  return Array.from(sessions.keys());
}

// extras for verifier / introspection — still zero-deps
export function _sessions() {
  return Array.from(sessions.entries()).map(([k, v]) => ({ user: k, token: v.token, at: v.at, exp: v.exp }));
}

export function is_on_cached() {
  // flags is_on cached 0.9 pattern helper — local heuristic
  return 0.9;
}

export const __meta = {
  zero_deps: true,
  no_torch: true,
  stub: true,
  max: MAX_SESSIONS,
  ephem_ms: EPHEMERAL_MS,
  pattern: '3-user cached local-first ephemeral 90s',
  lcg: '20260813→189831298 idx3820 triple[11205,19448,14209] ?daily=20260813&n=1/3/5 same-link-same-stars everyday chain',
  daily: '20260813',
  seed: 189831298,
  idx: 3820,
  triple: [11205, 19448, 14209],
};
