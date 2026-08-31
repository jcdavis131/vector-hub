const CACHE='dumbmodel-hub-v6-1';
const CORE=['/','/index.html','/manifest.json','/assets/human-v6/tokens.css','/assets/human-v6/base.css','/assets/human-v6/navigation.css','/assets/human-v6/human-v6.js'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url); if(u.origin!==location.origin){return} e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const copy=res.clone(); caches.open(CACHE).then(c=>c.put(e.request,copy)); return res}).catch(()=>caches.match('/index.html'))))});
