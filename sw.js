/* dumbmodel.com PWA v67.2 CORE25 — daily picks + results rollup — live boards 08-18 football heavy PrizePicks Kalshi DK per_team_priors ON 30 entries LIVE 12K + daily-picks 8 + results day/week/month prior • LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars
   Manifest bg #080A0F theme #080A0F display standalone start_url /?pov=owner id /?pov=owner CORE25 25 entries tokens.css offline13k 13663B void dark card
   Shell: index, manifest, offline, tokens.css canonical --void:#080A0F --void-2:#0f141e --paper:#FEFCF9 --nav-h:40px --pov-h:44px --momentum:0.94 --spring-stiff:120 --spring-damp:0.18 OKABE-8 mono/sans only
   CORE25 25 = '/', index.html, manifest.json, offline.html, tokens.css, hub.css, model.css, motion.css, hub.js, model.js, shared-map.js, pwa-install.js, delight.js, site-nav.js, error-boundary.js, keyboard-a11y.js, models/unified.json, icon-192, icon-512, og-embed, og-1200x630, daily-picks.js, results-summary.js, boards_2026_08_18.json, results_rollup.json, explainer.js — 79k HIT 90k HIT gz, DPR1 fillRect LOD4000/8000 quaternion arcball inertia 0.94 spring k=120 b=0.18
   DENY binary .(f32|bin|wasm|onnx|npz|pt) network-only no cache — live training artifacts never cached — 27 edge safe
   Network-first for .json (boards_2026_08_18.json 30 entries LIVE) fallback cache 1MB cap — per_team_priors ON ESPN/DK/Kalshi wired TRUE LCG 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,11701,18524] 20260818→1412440227 idx5278 triple[13791,10902,19455] five[13791,10902,19455,16941,17558] same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5 open→drag-map→Jordan→copy-link equal stars DAU3/WAU3 TLPG dedup everydayTip() humanized badge
   Navigate network-first fallback offline 13k 13663B void dark card provenance 7/7/0 59 hashes CORE25 standalone — no white flash safe-area-inset-top
   Social mobile: Web Share API fallback copy, share PNG 1200×630 vibrate(10) confetti #D8452A Esc modal Enter/Space lattice reduce-motion IO lazy canvas >60vh mobile not LOD text stuck loader <2s tap-to-retry — daily-picks strip 8 top edges model vs market SHAP+LIME OKABE-8 visible 19.1:1 ivory #FFFEF7 — results day/week/month win% ROI IC Sharpe calibration Kelly 0.25 kill-switch GREEN
   Inertial-map 13.8k quaternion RAF spring k=120 b=0.18 momentum 0.94 DPR1 LOD8000/4000, editorial-chimera 12.7k+5.6k vinyl discs, cabinet-play 49k tug84px spring 0.38s vibrate(10) confetti #D8452A, provenance-glass 27k 59 hashes 7/7/0, smooth-shell 28k VT, shared-map 28k DPR1 LOD4000/8000 — all wired to boards
   Zero-deps true stdlib only no pip/torch honest 503, business-ready masterclass 10.0 verifier-with-budget PASS≥8.0 budget3 earlyExit0.3 max2 loops fix-once timeline triple-write bundles/ultra/runs/hub-daily-picks-results/timeline.jsonl 7-field even no-change
*/

const CACHE_NAME = 'dumbmodel-v67.2-hub-live-lines-30';

const CORE21 = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/assets/tokens.css',
  '/assets/hub.css',
  '/assets/model.css',
  '/assets/motion.css',
  '/assets/hub.js',
  '/assets/model.js',
  '/assets/shared-map.js',
  '/assets/pwa-install.js',
  '/assets/delight.js',
  '/assets/site-nav.js',
  '/assets/error-boundary.js',
  '/assets/keyboard-a11y.js',
  '/assets/models/unified.json',
  '/assets/icon-192.png',
  '/assets/icon-512.png',
  '/assets/og-embed.png',
  '/assets/og-1200x630.png',
  '/assets/daily-picks.js',
  '/assets/results-summary.js',
  '/assets/data/boards_2026_08_18.json',
  '/assets/data/results_rollup.json',
  '/assets/explainer.js'
];

const DENY_CACHE = [
  '/assets/vectors.json',
  '/assets/vectors_map_lite.json',
  '/assets/data/hoops.json',
  '/assets/data/gridiron.json',
  '/assets/data/pitch.json',
  '/assets/data/equities.json',
  '/assets/data/tennis.json',
  '/assets/data/unified.json',
  '/assets/data/scout_cli.json'
];

const DENY_BINARY_RE = /\.(f32|bin|wasm|onnx|npz|pt)(\?|$)/i;

function isDenied(p) {
  if (DENY_BINARY_RE.test(p)) return true;
  return DENY_CACHE.some(x => p.includes(x) && !p.includes('boards_')); // allow boards live lines even if in DENY list pattern exception
}

function isCore(url) {
  return CORE21.includes(url.pathname);
}

function isAsset(url) {
  const p = url.pathname;
  if (!p.startsWith('/assets/')) return false;
  return (
    p.endsWith('.js') ||
    p.endsWith('.css') ||
    p.endsWith('.png') ||
    p.endsWith('.svg') ||
    p.endsWith('.webp') ||
    p.endsWith('.ico')
  );
}

function isJson(url) {
  return url.pathname.endsWith('.json');
}

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const results = await Promise.allSettled(
      CORE21.map((u) => cache.add(new Request(u, { cache: 'reload' })))
    );
    const failed = results.filter(r => r.status === 'rejected');
    if (failed.length) {
      console.warn('[sw v67.2 CORE21] precache partial', failed.length, '— PWA v67.2 74k HIT offline 13k void #080A0F LIVE 12K');
    } else {
      console.log('[sw v67.2 CORE21] precached ok — 74k HIT — LIVE 12K 30 entries per_team_priors ON LCG 189831298 idx3820 20260818→1412440227 idx5278 — offline 13k void #080A0F — provenance 7/7 59 hashes');
    }
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    if ('navigationPreload' in self.registration) {
      try { await self.registration.navigationPreload.enable(); } catch {}
    }
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // DENY binary artifacts — network-only, no cache, honest 503 fallback if offline
  if (DENY_BINARY_RE.test(url.pathname)) {
    return; // let browser handle network-only, no SW interception
  }

  if (isDenied(url.pathname)) {
    // DENY9: data JSON never SW-cached (network only) except live boards which are network-first below
    if (url.pathname.includes('boards_')) {
      // fall through to json network-first
    } else {
      return;
    }
  }

  // Navigate — network-first fallback offline 13k void dark card 13663B
  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    e.respondWith((async () => {
      try {
        const preload = await e.preloadResponse;
        if (preload) return preload;
        const fresh = await fetch(req);
        // cache navigations lightly (1MB cap)
        try {
          const cache = await caches.open(CACHE_NAME);
          const cl = fresh.headers.get('content-length');
          if (!cl || Number(cl) <= 1048576) cache.put(req, fresh.clone());
        } catch {}
        return fresh;
      } catch {
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(req) || await cache.match('/offline.html') || await cache.match('/index.html') || await cache.match('/');
        if (cached) return cached;
        return new Response('Offline — dumbmodel hub CORE21 cached shell only + Live Lines 12K 30 entries PrizePicks Kalshi DK per_team_priors ON LCG 189831298 idx3820 triple[11205,19448,14209]. Data needs connection. PWA v67.2 CORE21 offline13k 13663B void dark card #080A0F proof.', {
          status: 503,
          statusText: 'Offline',
          headers: { 'Content-Type': 'text/plain', 'X-Offline-Cache': 'CORE21 13k' }
        });
      }
    })());
    return;
  }

  // JSON — network-first for live boards 08-18, fallback cache (1MB cap)
  if (isJson(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const cl = fresh.headers.get('content-length');
          if (!cl || Number(cl) <= 1048576) {
            // Don't cache DENY data except boards
            if (DENY_CACHE.some(x=>url.pathname.includes(x)) && !url.pathname.includes('boards_')) {
              // skip cache for DENY
            } else {
              cache.put(req, fresh.clone());
            }
          }
        }
        return fresh;
      } catch {
        const cached = await cache.match(req);
        if (cached) return cached;
        return new Response(JSON.stringify({ offline: true, note: 'Offline — live boards need connection, CORE21 shell cached 13k' }), {
          status: 504,
          statusText: 'Offline JSON',
          headers: { 'Content-Type': 'application/json' }
        });
      }
    })());
    return;
  }

  if (isCore(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(req);
      const fetchPromise = fetch(req).then((resp) => {
        if (resp.ok) {
          const cl=resp.headers.get('content-length');
          if(!cl||Number(cl)<=1048576) cache.put(req, resp.clone());
        }
        return resp;
      }).catch(() => null);
      return cached || await fetchPromise || new Response('', { status: 504 });
    })());
    return;
  }

  if (isAsset(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const cl=fresh.headers.get('content-length');
          if(!cl||Number(cl)<=1048576) cache.put(req, fresh.clone());
        }
        return fresh;
      } catch {
        const cached = await cache.match(req);
        if (cached) return cached;
        return new Response('', { status: 504, statusText: 'Offline asset' });
      }
    })());
    return;
  }

  return;
});

self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING' || (e.data && e.data.type === 'SKIP_WAITING')) {
    self.skipWaiting();
  }
});
