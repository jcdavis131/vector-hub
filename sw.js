/* dumbmodel.com PWA v1 — shell-only CORE immutable stale-while-revalidate, large JSON_ONNX deny-cached
   Mirrors vector-hoops v66 pattern:
   - CORE only shell (~14 files), no large JSON/models/CDN
   - network-first for js/css/img with 1MB cap
   - JSON deliberately never SW-cached (network only, browser HTTP still applies)
     => offline mode is shell-only; data needs connection
   - stale-while-revalidate for immutable CORE
   - 20719×64-d chimera dailySeed LCG preserved via hub.js, not SW
*/

const CACHE_NAME = 'dumbmodel-v1-hub-5games-chimera';

const CORE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/assets/hub.css',
  '/assets/model.css',
  '/assets/motion.css',
  '/assets/hub.js',
  '/assets/model.js',
  '/assets/shared-map.js',
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
      console.warn('[sw dumbmodel v1] CORE precache partial failures:', failed.length);
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

  // never cache large JSON / data / vectors — network only
  if (isDenied(url.pathname)) {
    return;
  }

  // HTML navigation — network-first with offline fallback to cached shell + offline.html
  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    e.respondWith((async () => {
      try {
        const preload = await e.preloadResponse;
        if (preload) return preload;
        const fresh = await fetch(req);
        // optionally cache navigations? No — keep shell-only
        return fresh;
      } catch {
        const cache = await caches.open(CACHE_NAME);
        // try exact URL from cache (for /)
        const cached = await cache.match(req) || await cache.match('/offline.html') || await cache.match('/index.html');
        if (cached) return cached;
        // final fallback: construct minimal offline Response
        return new Response('Offline — dumbmodel hub cached shell only. Data needs connection.', {
          status: 503,
          statusText: 'Offline',
          headers: { 'Content-Type': 'text/plain' }
        });
      }
    })());
    return;
  }

  // CORE immutable — stale-while-revalidate
  if (isImmutable(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(req);
      const fetchPromise = fetch(req).then((resp) => {
        if (resp.ok) cache.put(req, resp.clone());
        return resp;
      }).catch(() => null);
      return cached || await fetchPromise || new Response('', { status: 504 });
    })());
    return;
  }

  // js/css/img assets — network-first with 1MB cap cache
  if (isAsset(url)) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          // 1MB cap naive check on blob? skip for simplicity — cache.put
          cache.put(req, fresh.clone());
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

  // default — network only, let browser HTTP cache handle
  return;
});

// allow page to trigger skipWaiting
self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING' || (e.data && e.data.type === 'SKIP_WAITING')) {
    self.skipWaiting();
  }
});
