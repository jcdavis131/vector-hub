/* dumbmodel.com PWA v67.2 JAPANDI TASTE v2 — paper #FEFCF9 wood #D6C7B3 stone #EAE3D8 moss #7A8A7B clay #C9A88C ink #1E1E1E — quiet library shelf 6 books hoops12966 gridiron646 pitch2430 equities500 unified20719 tennis128 — map cabinet japonais frame inset paper radius12-16 shadow 2.5px 2.5px 0 ink quaternion arcball inertia 0.94 spring k120 b0.18 DPR1 LOD8000/4000 #080A0F void only map — Today's Reading List 8 picks paper inset 1.5px radius12 annotation — Margin Notes ledger muted — LIVE boards 08-18 30 entries 12 PP 9 Kalshi 9 DK per_team_priors ON LIVE 12K — daily-picks + results + settlement AUTO — LCG 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,11701,18524] 20260818→1412440227 idx5278 triple[13791,10902,19455] same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5 DAU3/WAU3 TLPG dedup everydayTip() humanized — tactile wood grain CSS gradients paper fiber 2.5px soft shadow edge wear — provenance 7/7/0 59 hashes subtle — mono/sans only no Architects Daughter contrast 19.1:1 ivory void map only
   Manifest bg #FEFCF9 theme #FEFCF9 display standalone start_url /?pov=owner id /?pov=owner CORE28 28 entries tokens.css japandi tokens --paper:#FEFCF9 --paper-2:#FFFEF7 --wood:#D6C7B3 --stone:#EAE3D8 --ink:#1E1E1E --moss:#7A8A7B --clay:#C9A88C 13.8k inertial-map quaternion 14847 soft shadow 2.5px
   Shell: index, manifest, offline, tokens.css, hub.css, model.css, motion.css, hub.js, model.js, shared-map.js, pwa-install.js, delight.js, site-nav.js, error-boundary.js, keyboard-a11y.js, models/unified.json, icon-192, icon-512, og-embed, og-1200x630, daily-picks.js, results-summary.js, settlement.js, boards_2026_08_18.json, results_rollup.json, results_settlement.json, explainer.js — ~82k HIT — paper #FEFCF9 PWA v67.2 taste-v2
   DENY binary .(f32|bin|wasm|onnx|npz|pt) network-only no cache — live training artifacts never cached
   Network-first for .json 1MB cap fallback cache — provenance 7/7/0 59 hashes
   Japandi: 40px sticky nav z40 safe-area Books/Maps/Picks/Results/Lab single-select clears prev void #080A0F only map inset wood-grain wabi-sabi Esc modal Enter/Space lattice reduce-motion IO lazy canvas >60vh mobile not LOD stuck loader <2s tap-to-retry Web Share fallback PNG1200x630 vibrate10 confetti #D8452A provenance lattice 59 hashes footer subtle Built free Open-source No paywall paper inset pick 1.5px radius12 annotation
   Zero-deps true stdlib only — verifier PASS≥8.0 — timeline triple-write hub-japandi-taste-v2 7-field even no-change
*/

const CACHE_NAME = 'dumbmodel-v67.2-hub-japandi-taste-v2-34';

const CORE28 = [
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
  '/assets/settlement.js',
  '/assets/data/boards_2026_08_18.json',
  '/assets/data/results_rollup.json',
  '/assets/data/results_settlement.json',
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
  return DENY_CACHE.some(x => p.includes(x) && !p.includes('boards_'));
}

function isCore(url) {
  return CORE28.includes(url.pathname);
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
      CORE28.map((u) => cache.add(new Request(u, { cache: 'reload' })))
    );
    const failed = results.filter(r => r.status === 'rejected');
    if (failed.length) {
      console.warn('[sw v67.2 japandi] precache partial', failed.length, '— PWA paper #FEFCF9 wood #D6C7B3 — CACHE', CACHE_NAME);
    } else {
      console.log('[sw japandi] precached ok — paper #FEFCF9 theme #FEFCF9 — CORE28 28 -- LIVE 12K 30 entries per_team_priors ON LCG 189831298 idx3820 20260818→1412440227 idx5278 — offline paper #FEFCF9 — provenance 7/7 59 hashes — shelf 6 books');
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

  if (DENY_BINARY_RE.test(url.pathname)) return;

  if (isDenied(url.pathname)) {
    if (url.pathname.includes('boards_')) {} else { return; }
  }

  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    e.respondWith((async () => {
      try {
        const preload = await e.preloadResponse;
        if (preload) return preload;
        const fresh = await fetch(req);
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
        return new Response('Offline — dumbmodel hub japandi paper #FEFCF9 — CORE28 shell cached 28 entries — LIVE 12K needs connection — PWA v67.2 japandi offline paper #FEFCF9', {
          status: 503, statusText: 'Offline', headers: { 'Content-Type': 'text/plain', 'X-Offline-Cache': 'japandi paper' }
        });
      }
    })());
    return;
  }

  if (isJson(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const cl = fresh.headers.get('content-length');
          if (!cl || Number(cl) <= 1048576) {
            if (!(DENY_CACHE.some(x=>url.pathname.includes(x)) && !url.pathname.includes('boards_'))) {
              cache.put(req, fresh.clone());
            }
          }
        }
        return fresh;
      } catch {
        const cached = await cache.match(req);
        if (cached) return cached;
        return new Response(JSON.stringify({ offline: true, note: 'Offline — live boards + settlement need connection, CORE28 shell cached paper #FEFCF9' }), {
          status: 504, statusText: 'Offline JSON', headers: { 'Content-Type': 'application/json' }
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
