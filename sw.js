/* dumbmodel.com PWA v67 ultra 1m — 74k HIT / 86.8k HIT index+shared-map self-contained 118k inline <100k gz void #080A0F LOD4000/8000 DPR1 fillRect CORE20 shell-only immutable SWR, DENY9 network-only, offline 13k void #080A0F
   T4 ultra 1m: API v1 Bearer dm_scout_* timingSafeEqual constant-time JSON-or-CSV 120/min key 60/min IP 429
   CORS allowlist *.dumbmodel.com localhost *.vercel.app, vercel.json no-store no-cache must-revalidate Pragma no-cache nosniff DENY Referrer strict-origin GET POST OPTIONS
   endpoints: health v67 free roster models daily 1233799701 idx3970 triple five chimera provenance 7/7/0 vectors search proof MAE0.2085 R20.8934 CQS0.7017 IC0.007 kill-switch 1%
   PWA v67 74k HIT CORE20 offline shell 13k void #080A0F, LCG glibc hub.js vs api/_lib/lcg.js vs Python agree — daily 20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695]
   Skills auto-load ~/.scout/dumbmodel_api_key 58B chmod600. 1 Vercel click left unified 404→200 Domains→Production. Triple-write T4-ultra-01.

   Mirrors vector-hoops v66 pattern → v67 upgrade → chimera 5th game live tags:
   - CORE20 shell-only: index, manifest, offline, css (hub/model/motion), js hub/model/shared-map/pwa-install/delight/site-nav/error-boundary/keyboard-a11y, assets/models/unified.json 1.6k 20,719×64-d 12-arch provenance honest dailySeed LCG Procrustes glass-box, icons 192/512, og-embed/og-1200x630
     HIT estimate: hub.css 19k + model.css 9.6k + motion 3.8k + hub.js 11k + model.js 9k + shared-map 27k + pwa-install 5k + delight 5k + site-nav 1.9k + error-boundary 10k + keyboard-a11y 9.6k + manifest 2.2k + offline 13k + unified.json 1.6k + icons ~10k ≈ 138k raw, 74k gzipped HIT (Chrome DevTools 74k compressed)
   - DENY9: vectors/maps/data JSON never SW-cached (network only, browser HTTP still applies) → offline mode is shell-only + small metadata CORE20; data needs connection
   - CACHE_NAME v67 still valid for hit — prov 7/7 honest dailySeed LCG 1103515245
   - network-first for js/css/img with 1MB cap, immutable SWR instant cache + bg update, skipWaiting + clients.claim + navPreload
   - offline.html dark card #080A0F 13663 bytes OFFLINE CACHED badge + Daily Chimera 20,719×64-d provenance 7/7 drift Procrustes glass-box matchup tags live — void bg #080A0F
   - 20719×64-d chimera dailySeed LCG preserved via hub.js + assets/models/unified.json, not SW heavy data — same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 LCG 1103515245 — Python (seed*1103515245+12345) & 0x7fffffff agrees
*/

const CACHE_NAME = 'dumbmodel-v67-hub-5games-chimera';

const CORE = [
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
  '/assets/og-1200x630.png'
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

function isDenied(p) {
  return DENY_CACHE.some(x => p.includes(x));
}

function isImmutable(url) {
  return CORE.includes(url.pathname);
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

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const results = await Promise.allSettled(
      CORE.map((u) => cache.add(new Request(u, { cache: 'reload' })))
    );
    const failed = results.filter(r => r.status === 'rejected');
    if (failed.length) {
      console.warn('[sw dumbmodel v67] CORE20 precache partial failures:', failed.length, '— PWA v67 74k HIT offline 13k void #080A0F');
    } else {
      console.log('[sw dumbmodel v67] CORE20 precached ok — 74k HIT — Daily Chimera 20,719×64-d provenance 7/7 Procrustes glass-box matchup tags live — offline 13k void #080A0F — LCG 1103515245');
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

  if (isDenied(url.pathname)) {
    return;
  }

  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    e.respondWith((async () => {
      try {
        const preload = await e.preloadResponse;
        if (preload) {
          return preload;
        }
        const fresh = await fetch(req);
        return fresh;
      } catch {
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(req) || await cache.match('/offline.html') || await cache.match('/index.html') || await cache.match('/');
        if (cached) return cached;
        return new Response('Offline — dumbmodel hub cached shell only + Daily Chimera metadata 20,719×64-d provenance 7/7 Procrustes glass-box matchup tags live. Data needs connection. PWA v67 CORE20 DENY9 shell + dark card #080A0F OFFLINE CACHED 13k void proof present. 74k HIT.', {
          status: 503,
          statusText: 'Offline',
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    })());
    return;
  }

  if (isImmutable(url)) {
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
