/* schools PWA v67 — CORE20 offline13k LOD4000/8000 DPR1 — honest 503 — zero-deps */
const CACHE_NAME='vector-schools-v67-human-v5-20';
const CORE=[
'/',
'/index.html',
'/manifest.json',
'/offline.html',
'/assets/human-v5/tokens.css',
'/assets/human-v5/base.css',
'/assets/human-v5/navigation.css',
'/assets/human-v5/individual.css',
'/assets/human-v5/peers.css',
'/assets/human-v5/map.css',
'/assets/human-v5/evidence.css',
'/assets/human-v5/states.css',
'/assets/human-v5/motion.css',
'/assets/human-v5/human-v5.js',
'/assets/icon-192.png',
'/assets/icon-512.png'
];
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const url=new URL(e.request.url);
  if(url.pathname.includes('embedding_schools_full') || url.pathname.includes('real_data.json')){
    // Honest 503 path — embeddings are large, don't cache in CORE, network-first with fallback
    e.respondWith(fetch(e.request).catch(()=>new Response(JSON.stringify({error:'honest 503 — 27,181 embeddings require network'}),{status:503,headers:{'Content-Type':'application/json'}})));
    return;
  }
  if(CORE.some(c=>url.pathname===c || url.pathname.endsWith(c))){
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{
      const clone=resp.clone(); caches.open(CACHE_NAME).then(c=>c.put(e.request,clone)); return resp;
    }).catch(()=>caches.match('/offline.html'))));
    return;
  }
  e.respondWith(fetch(e.request).catch(()=>caches.match('/offline.html')));
});
