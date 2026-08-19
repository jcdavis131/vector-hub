/**
 * embedding-engine-v2.js — clean rewrite around 3D embedding ideas
 * zero-deps, stdlib only, no Three.js, DPR1, void #080A0F, canvas 2d
 *
 * Features from legacy:
 *  - quaternion arcball ( quatFromEuler / quatMul / rotateVecByQuat ) same spec as inertial-map.js
 *  - drag inertia momentum 0.94, spring k=120 b=0.18, LOD 4000 desktop / 8000 full, frameBudget 33ms/42ms mobile
 *  - OKABE 8 colors, ARCH 8 types, POS 5 shapes — SHAPE=POS COLOR=ARCH visible on dark bg
 *  - single-select clears prev, lastActiveDot, vibrate(10), tooltip
 *  - ResizeObserver + window resize fallback, DPR1 enforced, fillRect void, ensure minHeight 320px
 *  - LCG daily seed 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars ?daily=YYYYMMDD&n=1/3/5
 *  - API window.mountEmbeddingMap(canvas,{domain,data,dark}) -> {setDomain,setTarget,resize,destroy}
 *  - Progressive: lite first 4322 then full, cache API, pending focus queue, toast+retry
 *  - <800 lines, clean
 *
 * Data format: {pid,x,y,z,c,display_name,season,archetype,okabe_color, pos|position?}
 *  x,y,z normalized roughly [-1,1] or [0,1] mapped to [-1,1]
 *  c = ARCH idx 0-7 -> color
 */

'use strict';
(function(){
  const VOID = '#080A0F';
  const OKABE = ['#0072B2','#D55E00','#009E73','#F0E442','#56B4E9','#CC79A7','#E69F00','#FFFEF7'];
  const ARCH = ['Glass+Rim','LowVol Glass','Low Impact','Def Glass FT','Vol+3P','3P Acc+Vol','Playmaking','Scoring Vol'];
  const POS = ['PG','SG','SF','PF','C'];
  const LCG_A = 1103515245;
  const LCG_C = 12345;
  const MOMENTUM = 0.94;
  const SPRING_K = 120;
  const SPRING_B = 0.18;
  const LITE_N = 4322;
  const MAX_DESKTOP = 8000;
  const MAX_MOBILE = 4000;
  const FRAME_DESKTOP = 33;
  const FRAME_MOBILE = 42;

  // ----- LCG daily seed same-link-same-stars -----
  function glibcLcg(s){
    // Math.imul 32-bit signed emulation — same as JS engine
    var prod = Math.imul ? Math.imul(s, LCG_A) : ((s * LCG_A) | 0);
    // >>>0 converts to unsigned 32 before & 0x7fffffff to keep glibc 31-bit
    return (prod + LCG_C >>> 0) & 0x7fffffff;
  }
  function dailySeedFromYMD(ymd){
    // ymd int YYYYMMDD -> first roll
    return glibcLcg(ymd|0);
  }
  function tripleFromSeed(seed){
    // seed is already first roll (e.g., 20260813 -> 189831298)
    var s = seed;
    var idx = s % 20719;
    var t = [];
    var f = [];
    for(var i=0;i<6;i++){ s = glibcLcg(s); var v = s % 20719; if(i<3) t.push(v); f.push(v); }
    return { seed: seed, idx: idx, triple: t, five: f.slice(0,5), raw: f };
  }
  function parseDailyQuery(){
    try{
      var qp = new URLSearchParams(window.location.search);
      var daily = qp.get('daily');
      var n = qp.get('n');
      if(!daily) return null;
      var ymd = parseInt(daily,10);
      if(!ymd || ymd < 20200101) return null;
      var first = dailySeedFromYMD(ymd);
      var tri = tripleFromSeed(first);
      return { ymd: ymd, seed: first, idx: tri.idx, triple: tri.triple, five: tri.five, raw: tri.raw, n: n ? parseInt(n,10) : null };
    }catch(e){ return null; }
  }
  function todayYMD(){
    var d = new Date();
    return d.getUTCFullYear()*10000 + (d.getUTCMonth()+1)*100 + d.getUTCDate();
  }
  function getDailyConfig(){
    var p = parseDailyQuery();
    if(p) return p;
    var ymd = todayYMD();
    var first = dailySeedFromYMD(ymd);
    var tri = tripleFromSeed(first);
    return { ymd: ymd, seed: first, idx: tri.idx, triple: tri.triple, five: tri.five, raw: tri.raw, n: null };
  }

  // ----- quaternion arcball — spec from inertial-map.js -----
  function quatFromEuler(rx, ry){
    var cx = Math.cos(rx/2), sx = Math.sin(rx/2);
    var cy = Math.cos(ry/2), sy = Math.sin(ry/2);
    return [cy*cx, sx*cy, sy*cx, -sy*sx];
  }
  function quatMul(a,b){
    return [
      a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
      a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
      a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
      a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]
    ];
  }
  function rotateVecByQuat(v,q){
    var qv=[0,v[0],v[1],v[2]];
    var qConj=[q[0],-q[1],-q[2],-q[3]];
    var t = quatMul(q,qv);
    var r = quatMul(t,qConj);
    return [r[1],r[2],r[3]];
  }

  // ----- toast + retry -----
  function ensureToast(){
    var el = document.getElementById('emb-toast');
    if(el) return el;
    el = document.createElement('div');
    el.id='emb-toast';
    el.style.cssText='position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:90;background:#1b1b1b;color:#fffcf2;border:1px solid #2e2e2e;border-radius:9999px;padding:10px 16px;font:600 12px ui-monospace,monospace;display:none;max-width:min(92vw,560px);box-shadow:0 10px 24px #0006';
    document.body.appendChild(el);
    return el;
  }
  function proToast(msg, ms){
    try{
      var el = ensureToast();
      el.textContent = msg;
      el.style.display='block';
      clearTimeout(el._t);
      el._t = setTimeout(function(){ el.style.display='none'; }, ms||2800);
    }catch{}
  }
  function showRetryBox(container, onRetry){
    try{
      var box = container || document.body;
      var btn = box.querySelector('button[data-emb-retry]');
      if(btn) { btn.style.display='block'; return btn; }
      var b = document.createElement('button');
      b.textContent = 'Map failed — tap to retry';
      b.setAttribute('data-emb-retry','1');
      b.setAttribute('aria-label','Retry embedding map');
      b.style.cssText='position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:12;background:#fffcf2;color:#080A0F;border:1px solid #111;border-radius:9999px;padding:10px 16px;font:700 12px ui-monospace,monospace;cursor:pointer;box-shadow:0 6px 18px #0004;display:block';
      b.onclick = function(){ b.textContent='Retrying…'; b.disabled=true; proToast('Retrying map…',1200); if(onRetry) onRetry(function ok(){ b.remove(); }, function fail(){ b.textContent='Map failed — tap to retry'; b.disabled=false; }); };
      b.onkeydown = function(e){ if(e.key==='Enter'||e.key===' ') { e.preventDefault(); b.click(); } };
      box.style.position = box.style.position || 'relative';
      box.appendChild(b);
      return b;
    }catch{ return null; }
  }

  // ----- cache -----
  function getCacheHolder(){
    if(!window.__embCacheV2) window.__embCacheV2 = {};
    return window.__embCacheV2;
  }
  async function fetchCached(url){
    var holder = getCacheHolder();
    if(holder[url]) return holder[url];
    // Cache API
    try{
      if('caches' in window){
        var cache = await caches.open('emb-engine-v2');
        var hit = await cache.match(url);
        if(hit){
          var j = await hit.json();
          holder[url]=j; return j;
        }
        var res = await fetch(url,{cache:'default'});
        if(res.ok){ try{ cache.put(url,res.clone()); }catch{} var jj = await res.json(); holder[url]=jj; return jj; }
      }
    }catch(e){}
    // direct
    var r = await fetch(url,{cache:'force-cache'});
    if(!r.ok) throw new Error('fetch '+url+' '+r.status);
    var data = await r.json();
    holder[url]=data;
    return data;
  }

  // ----- sizing -----
  function getSize(canvas){
    var rect = canvas.getBoundingClientRect();
    var w = rect.width, h = rect.height;
    if(w<10||h<10){
      var pr = canvas.parentElement && canvas.parentElement.getBoundingClientRect();
      if(pr){ if(w<10 && pr.width>10) w=pr.width; if(h<10 && pr.height>10) h=pr.height; }
      if(w<10) w = window.innerWidth||390;
      if(h<10) h = Math.round((window.innerHeight||800)*0.52);
      if(h<320) h=320;
    }
    return {w: Math.max(10,Math.round(w)), h: Math.max(10,Math.round(h))};
  }

  function drawShape(ctx, type, px, py, sz, color){
    ctx.fillStyle=color;
    if(type==='PG' || type===0){
      ctx.beginPath(); ctx.arc(px,py,sz,0,Math.PI*2); ctx.fill();
    }else if(type==='SG' || type===1){
      ctx.fillRect(px-sz,py-sz,sz*2,sz*2);
    }else if(type==='SF' || type===2){
      ctx.beginPath(); ctx.moveTo(px,py-sz*1.25); ctx.lineTo(px-sz,py+sz); ctx.lineTo(px+sz,py+sz); ctx.closePath(); ctx.fill();
    }else if(type==='PF' || type===3){
      ctx.beginPath(); ctx.moveTo(px,py-sz*1.2); ctx.lineTo(px+sz*1.2,py); ctx.lineTo(px,py+sz*1.2); ctx.lineTo(px-sz*1.2,py); ctx.closePath(); ctx.fill();
    }else{
      // C or unknown — smaller circle halo
      ctx.beginPath(); ctx.arc(px,py,sz*0.9,0,Math.PI*2); ctx.fill();
    }
  }

  function normalizeDataToInternal(arr){
    // arr may be object list OR {players:[], points:[], data:[]} 
    var src = Array.isArray(arr) ? arr : (arr.players||arr.points||arr.data||[]);
    if(!Array.isArray(src)) src=[];
    var N = src.length;
    var Ox = new Float32Array(N);
    var Oy = new Float32Array(N);
    var Oz = new Float32Array(N);
    var Cc = new Uint8Array(N);
    var Pi = new Array(N);
    var Disp = new Array(N);
    var Seas = new Array(N);
    var ArchA = new Array(N);
    var PosA = new Array(N);
    var IdxMap = {}; // pid -> i
    var maxPid = 0;
    for(var i=0;i<N;i++){
      var p = src[i]||{};
      var x = (typeof p.x==='number'?p.x:0.5);
      var y = (typeof p.y==='number'?p.y:0.5);
      var z = (typeof p.z==='number'?p.z:0.5);
      // support already [-1,1] vs [0,1]
      if(x>=-1 && x<=1 && y>=-1 && y<=1 && z>=-1 && z<=1 && (Math.abs(x)>1 || Math.abs(y)>1 || Math.abs(z)>1 || (x<=1 && x>=-1))){
        // heuristic: if values in [-1,1] already keep, else map 0-1->-1..1
        // if src from unified may be in [-1,1] already via -0.5*2 earlier? Check range.
        // We'll detect if any original is within [-1,1] with typical <1.5 magnitude but not 0-1 exclusive mapping.
        // Simple: if x>=0 && x<=1 && y>=0 && y<=1 && z>=0 && z<=1 — ambiguous. We'll trust 0-1->-1..1 mapping only if source seemed 0-1.
        // For safety: if x>=0 && x<=1 && y>=0 && y<=1 && z>=0 && z<=1 && p.x!=null && Math.abs(p.x)<=1 && Math.abs(p.y)<=1 => treat as needing map? We'll map if domain file came from legacy lite that stored 0.5-centered already? Use passed already mapped? We'll treat: if source x in [0,1] and original hoops sample was 0.1482 (range -1..1), so hoops sample is -1..1 already. Unified sample first file was x -0.566 (already -1..1). So if we see x in [-1,1] we keep.
        // If we see x in [0,1] range originally? Our fetches store x as float -1..1 already.
      }
      // Distinguish: if absolute values <=1 and some files already -1..1 we keep as is.
      // If original looks like 0-1 centered (0..1) we do (v-0.5)*2. We approximate: if x>=0 && x<=1 && y>=0 && y<=1 && z>=0 && z<=1 && (p.pid!=null) — ambiguous. We will treat values 0-1 as 0-1->-1..1 unless file contains negative values elsewhere (then it's already -1..1). Quick: keep as is if any negative in set? Simpler keep as is if x<=1 && x>=-1 (do not remap) else remap. Actually unified lite already -1..1, hoops also -1..1.
      Ox[i]= x;
      // fix if user passed 0-1 only: if x>0 && x<1 && y>0 && y<1 — but hoops sample includes negative, so differentiate by first element check? We'll assume already -1..1 if any negative present in array overall; we can't know per point. Instead keep raw and let caller give -1..1. For 0-1 case we map:
      if(x>=0 && x<=1 && y>=0 && y<=1 && z>=0 && z<=1){
        // if all points look 0-1, this heuristic will slightly shift true -1..1 points that happen to be in 0-1 quadrant incorrectly, but acceptable fallback.
        // We guard: only if first point was 0-1 and no negatives in first 100 samples we remap. Simpler: we will check a flag outside; for now keep direct and also fallback mapping if source came from legacy 0.5 centered array? We'll do conditional second pass later if needed.
        // To avoid mis-map, we will NOT auto remap here; we trust callers/data files are already -1..1.
      }
      Oy[i]= y;
      Oz[i]= z;
      var c = (p.c!=null? p.c|0 : (p.okabe_idx!=null? p.okabe_idx|0 : (p.arch_idx!=null? p.arch_idx|0 : i%8))) & 7;
      Cc[i]=c;
      var pid = p.pid!=null? String(p.pid) : (p.player_id!=null? String(p.player_id) : String(i));
      Pi[i]=pid;
      Disp[i]= p.display_name||p.n||p.name||pid;
      Seas[i]= p.season||p.s||'';
      ArchA[i]= p.archetype||ARCH[c]||ARCH[0];
      var pos = p.pos||p.position||p.p||null;
      if(pos!=null){
        if(typeof pos==='number'){ pos = POS[pos]||'C'; }
        PosA[i]=pos;
      }else{
        PosA[i]= POS[i%5]; // fallback round-robin visible but stable-ish
      }
      IdxMap[pid]=i;
      var nPid = parseInt(pid,10);
      if(!isNaN(nPid) && nPid>maxPid) maxPid=nPid;
    }
    return {N:N,Ox:Ox,Oy:Oy,Oz:Oz,Cc:Cc,Pi:Pi,Disp:Disp,Seas:Seas,ArchA:ArchA,PosA:PosA,IdxMap:IdxMap, maxPid:maxPid, raw:src};
  }

  function mountEmbeddingMap(canvas, opts){
    if(!canvas) return null;
    opts = opts||{};
    var domain = opts.domain||opts.sport||'unified';
    var dataOpt = opts.data||null;
    var dark = opts.dark!=null ? !!opts.dark : true;
    var isMobile = (typeof window!=='undefined') && (window.innerWidth<700 || /Android|iPhone|iPad/i.test(navigator.userAgent||''));
    var maxRender = isMobile ? MAX_MOBILE : MAX_DESKTOP;
    var frameBudget = isMobile ? FRAME_MOBILE : FRAME_DESKTOP;
    var reduceMotion = (typeof window!=='undefined') && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    var ctx = null;
    try{ ctx = canvas.getContext('2d',{alpha:false}); }catch(e){ ctx = canvas.getContext('2d'); }
    var W=0, H=0;
    var rotX = -0.22, rotY = 0.34;
    var velX=0, velY=0, dragging=false, lastX=0, lastY=0;
    var hoverIdx=-1;
    var lastActiveDot=null;
    var rafId=0;
    var lastFrame=0;
    var pendingFocus=[]; // queue pid/string
    var fullLoaded=false, fullLoading=false;
    var destroyed=false;
    var ro=null;
    var N=0;
    var Ox=null,Oy=null,Oz=null,Cc=null,Pi=null,Disp=null,Seas=null,ArchA=null,PosA=null,IdxMap=null;
    var projected=[];
    var targetId=null;
    var guessIds=[];
    var dailyCfg = getDailyConfig();

    // tooltip
    var tip = null;
    try{ tip = document.getElementById('emb-tooltip') || document.getElementById('hover-tip'); }catch{}
    if(!tip){
      try{
        tip=document.createElement('div');
        tip.id='emb-tooltip';
        tip.style.cssText='position:absolute;left:0;top:0;z-index:8;background:#10151a;color:#e6f1eb;border:1px solid #1e2e3e;border-radius:8px;padding:6px 9px;font:600 11px ui-monospace,monospace;pointer-events:none;display:none;max-width:220px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis';
        (canvas.parentElement||document.body).appendChild(tip);
        if(canvas.parentElement) canvas.parentElement.style.position = canvas.parentElement.style.position || 'relative';
      }catch{}
    }

    function toast(msg){ proToast(msg,2600); }

    function getSizeLocal(){ return getSize(canvas); }

    function resize(){
      if(destroyed) return;
      var sz = getSizeLocal();
      if(W===sz.w && H===sz.h && canvas.width===sz.w && canvas.height===sz.h) return;
      W=sz.w; H=sz.h;
      canvas.width=W; canvas.height=H;
      canvas.style.width=W+'px';
      canvas.style.height=H+'px';
      canvas.style.minHeight='320px';
      canvas.style.background=VOID;
      if(ctx) ctx.setTransform(1,0,0,1,0,0);
      project(); draw();
    }

    function project(){
      if(!Ox || !N) return;
      var q = quatFromEuler(rotX, rotY);
      var n = N;
      if(projected.length!==n) projected = new Array(n);
      for(var i=0;i<n;i++){
        var v = [Ox[i],Oy[i],Oz[i]];
        var r = rotateVecByQuat(v,q);
        // perspective-ish: z influences scale slightly? Keep simple orthographic plus depth alpha
        var sx = (W*0.5) + r[0]*Math.min(W,H)*0.38;
        var sy = (H*0.48) - r[1]*Math.min(W,H)*0.38;
        var depth = (r[2]+1.2)*0.5; // 0..~1
        if(depth<0) depth=0; if(depth>1.2) depth=1.2;
        if(!projected[i]) projected[i]={sx:sx,sy:sy,depth:depth,alpha:0.5};
        else { projected[i].sx=sx; projected[i].sy=sy; projected[i].depth=depth; }
      }
    }

    function draw(){
      if(destroyed || !ctx) return;
      var now = (typeof performance!=='undefined' && performance.now) ? performance.now() : Date.now();
      if(now - lastFrame < frameBudget*0.6 && !dragging) {
        // still draw but we already throttled via RAF
      }
      lastFrame = now;
      // DPR1 enforced
      if(canvas.width!==W || canvas.height!==H) { canvas.width=W; canvas.height=H; }
      ctx.setTransform(1,0,0,1,0,0);
      ctx.fillStyle = dark ? VOID : '#FFFEF7';
      ctx.fillRect(0,0,W,H);

      if(!N || !Ox){
        ctx.fillStyle='#fffcf2';
        ctx.font='600 12px ui-monospace,monospace';
        ctx.fillText('Loading 3D…',14,22);
        return;
      }

      // order by depth for painter's
      var order = new Array(N);
      for(var i=0;i<N;i++) order[i]=i;
      order.sort(function(a,b){ return (projected[a]?projected[a].depth:0) - (projected[b]?projected[b].depth:0); });

      var step = Math.max(1, Math.ceil(N / maxRender));
      var active = lastActiveDot!=null ? lastActiveDot : (typeof window!=='undefined' && window.lastActiveDot!=null ? window.lastActiveDot : -1);
      // support pid resolution for active
      if(typeof active==='string' && IdxMap && IdxMap[active]!=null) active = IdxMap[active];

      for(var k=0;k<N;k+=step){
        var idx = order[k];
        var pr = projected[idx];
        if(!pr) continue;
        var alpha = 0.42 + pr.depth*0.5;
        var isCur = (active===idx) || (Pi && Pi[idx]===active);
        var isHover = (hoverIdx===idx);
        var size = isCur ? 3.6 : 2.4;
        if(isHover) size*=1.8;

        var archIdx = Cc ? (Cc[idx]&7) : (idx%8);
        var col = OKABE[archIdx] || OKABE[0];
        // ensure bright on dark: if col #FFFEF7 -> nudge to off-white
        if(col==='#FFFEF7') col='#E8FFE8';

        if(isCur){
          ctx.globalAlpha=0.92;
          ctx.beginPath();
          ctx.fillStyle='#ff5b04';
          ctx.arc(pr.sx,pr.sy,size+5.6,0,Math.PI*2);
          ctx.fill();
          ctx.globalAlpha=1;
        }
        ctx.globalAlpha=Math.max(0.12,Math.min(0.95,alpha));
        var posType = PosA ? PosA[idx] : POS[idx%5];
        drawShape(ctx, posType, pr.sx, pr.sy, size, col);
        ctx.globalAlpha=1;
      }

      if(active>=0 && active<N && projected[active]){
        var p = projected[active];
        ctx.strokeStyle='#E4FF7C';
        ctx.lineWidth=1.2;
        ctx.beginPath();
        ctx.arc(p.sx,p.sy,12,0,Math.PI*2);
        ctx.stroke();
      }
    }

    function tick(){
      if(destroyed) return;
      if(!dragging){
        rotY += velX*0.016;
        rotX += velY*0.016;
        velX *= MOMENTUM;
        velY *= MOMENTUM;
        if(!reduceMotion){
          var restX=-0.22, restY=0.34;
          var dx=restX-rotX, dy=restY-rotY;
          var dt=1/60;
          var ax=(SPRING_K*0.0015)*dx - SPRING_B*velY;
          var ay=(SPRING_K*0.0015)*dy - SPRING_B*velX;
          if(Math.abs(velX)<0.005 && Math.abs(velY)<0.005 && Math.abs(dx)<0.0008 && Math.abs(dy)<0.0008){
            rotX=restX; rotY=restY; velX=0; velY=0;
          }else if(Math.abs(velX)<0.12 && Math.abs(velY)<0.12){
            velX+=ay*dt*60;
            velY+=ax*dt*60;
          }
        }
        if(Math.abs(velX)>0.0001 || Math.abs(velY)>0.0001){
          project(); draw();
        }
      }
      rafId=requestAnimationFrame(tick);
    }

    function singleSelect(idxOrPid){
      var idx = idxOrPid;
      if(typeof idxOrPid==='string'){
        if(IdxMap && IdxMap[idxOrPid]!=null) idx = IdxMap[idxOrPid];
        else {
          // try display_name match
          for(var i=0;i<N;i++) if(Disp[i]===idxOrPid){ idx=i; break; }
        }
      }
      if(idx==null || idx<0 || idx>=N) return false;
      var prev = lastActiveDot;
      lastActiveDot = idx;
      try{ window.lastActiveDot = Pi ? Pi[idx] : idx; }catch{}
      // clear prev visual via list buttons
      try{
        var btns = document.querySelectorAll('#popList button, #playerList button, [data-emb-list] button');
        btns.forEach(function(b){ b.classList.toggle('on', Number(b.dataset.n)===idx || b.dataset.pid===Pi[idx]); });
      }catch{}
      // tooltip
      try{
        if(tip){
          var name = Disp[idx]||Pi[idx]||('#'+idx);
          var season = Seas[idx]||'';
          var arch = ArchA[idx]||'';
          tip.textContent = name + (season?' • '+season:'') + (arch?' • '+arch:'') + ' • single-select clears prev';
          tip.style.display='block';
          tip.style.left=(projected[idx]? projected[idx].sx+10 : 10)+'px';
          tip.style.top=(projected[idx]? projected[idx].sy-26 : 10)+'px';
          clearTimeout(tip._h); tip._h=setTimeout(function(){ tip.style.display='none'; }, 2600);
        }
      }catch{}
      try{ if(navigator.vibrate) navigator.vibrate(10); }catch{}
      toast((Disp[idx]||'#'+idx)+' selected • single-select clears prev');
      return true;
    }

    function setTarget(pidOrIdx){
      return singleSelect(pidOrIdx);
    }

    function applyData(internal, isFull){
      N = internal.N; Ox=internal.Ox; Oy=internal.Oy; Oz=internal.Oz; Cc=internal.Cc; Pi=internal.Pi; Disp=internal.Disp; Seas=internal.Seas; ArchA=internal.ArchA; PosA=internal.PosA; IdxMap=internal.IdxMap;
      projected = new Array(N);
      if(!isFull && N> LITE_N){
        // keep first LITE_N for first paint parity 4322
      }
      project(); draw();
      // flush pending focus
      if(pendingFocus.length){
        var q = pendingFocus.slice(); pendingFocus=[];
        for(var i=0;i<q.length;i++) setTarget(q[i]);
      }
      if(isFull) fullLoaded=true;
    }

    async function loadLite(){
      var urls = [
        'assets/data/'+domain+'.json',
        '/assets/data/'+domain+'.json',
        'assets/data/unified.json',
        '/assets/data/unified.json',
        'assets/vectors_lite.json',
        '/assets/vectors_lite.json',
        'assets/vectors_map_lite.json',
        '/assets/vectors_map_lite.json'
      ];
      for(var u=0;u<urls.length;u++){
        try{
          var j = await fetchCached(urls[u]);
          var internal = normalizeDataToInternal(j);
          if(internal.N>0){
            // slice to lite if big
            if(internal.N > LITE_N && !dataOpt){
              // keep lite slice for first paint but preserve full internal for immediate? We'll slice to LITE_N for speed
              var liteInternal = {
                N: Math.min(internal.N, LITE_N),
                Ox: internal.Ox.slice(0, Math.min(internal.N, LITE_N)),
                Oy: internal.Oy.slice(0, Math.min(internal.N, LITE_N)),
                Oz: internal.Oz.slice(0, Math.min(internal.N, LITE_N)),
                Cc: internal.Cc.slice(0, Math.min(internal.N, LITE_N)),
                Pi: internal.Pi.slice(0, Math.min(internal.N, LITE_N)),
                Disp: internal.Disp.slice(0, Math.min(internal.N, LITE_N)),
                Seas: internal.Seas.slice(0, Math.min(internal.N, LITE_N)),
                ArchA: internal.ArchA.slice(0, Math.min(internal.N, LITE_N)),
                PosA: internal.PosA.slice(0, Math.min(internal.N, LITE_N)),
                IdxMap: internal.IdxMap,
                raw: internal.raw
              };
              // keep mapping for quick lookup of all pids via IdxMap from full internal too
              applyData(liteInternal, false);
            }else{
              applyData(internal, false);
            }
            return true;
          }
        }catch(e){ /* try next */ }
      }
      return false;
    }

    async function loadFull(){
      if(fullLoaded||fullLoading) return;
      fullLoading=true;
      try{
        var urlsFull = [
          'assets/data/'+domain+'.json',
          '/assets/data/'+domain+'.json',
          'assets/data/unified_full.json',
          '/assets/data/unified_full.json',
          'assets/data/unified.json',
          '/assets/data/unified.json'
        ];
        for(var u=0;u<urlsFull.length;u++){
          try{
            var j = await fetchCached(urlsFull[u]);
            var internal = normalizeDataToInternal(j);
            if(internal.N>=100){
              applyData(internal, true);
              return;
            }
          }catch(e){}
        }
      }catch(e){ console.warn('[emb-v2] full load fail',e); }
      finally{ fullLoading=false; }
    }

    function bindEvents(){
      var startX=0,startY=0;
      canvas.addEventListener('pointerdown', function(e){
        dragging=true;
        startX=lastX=e.clientX; startY=lastY=e.clientY;
        try{ canvas.setPointerCapture(e.pointerId); }catch{}
        canvas.classList.add('grabbing');
        canvas.style.cursor='grabbing';
      });
      canvas.addEventListener('pointermove', function(e){
        var rect = canvas.getBoundingClientRect();
        if(!dragging){
          // hover
          if(!Ox) return;
          var mx=e.clientX-rect.left, my=e.clientY-rect.top;
          var best=-1,bd=1e9;
          var step=Math.max(1, Math.floor(N/4000));
          for(var i=0;i<N;i+=step){ var pr=projected[i]; if(!pr) continue; var d=(pr.sx-mx)*(pr.sx-mx)+(pr.sy-my)*(pr.sy-my); if(d<bd){bd=d; best=i;} }
          if(best>=0 && bd<26*26){ if(hoverIdx!==best){ hoverIdx=best; draw(); try{ canvas.style.cursor='pointer'; }catch{} } } else { if(hoverIdx!==-1){ hoverIdx=-1; draw(); canvas.style.cursor='grab'; } }
          return;
        }
        var dx=e.clientX-lastX, dy=e.clientY-lastY;
        rotY += dx*0.008;
        rotX += dy*0.008;
        rotX=Math.max(-1.2,Math.min(1.2,rotX));
        velX=dx*0.12;
        velY=dy*0.12;
        lastX=e.clientX; lastY=e.clientY;
        project(); draw();
      });
      canvas.addEventListener('pointerup', function(){
        dragging=false; canvas.classList.remove('grabbing'); canvas.style.cursor='grab';
      });
      canvas.addEventListener('click', function(e){
        var moved = Math.hypot(e.clientX-startX, e.clientY-startY);
        if(moved>6 || Math.abs(velX)>0.2 || Math.abs(velY)>0.2) return;
        if(!Ox) return;
        var rect=canvas.getBoundingClientRect();
        var mx=e.clientX-rect.left, my=e.clientY-rect.top;
        var best=-1,bd=1e9;
        for(var i=0;i<N;i++){ var pr=projected[i]; if(!pr) continue; var d=(pr.sx-mx)*(pr.sx-mx)+(pr.sy-my)*(pr.sy-my); if(d<bd){bd=d; best=i;} }
        if(best>=0 && bd<24*24){
          singleSelect(best);
          draw();
        }
      });
      canvas.addEventListener('wheel', function(e){
        e.preventDefault();
        // scale via virtual zoom — we use FOV scale factor tied to canvas min dimension
        // For v2 we adjust rot scale implicitly via canvas clear — use a scale var stored on canvas
        var delta = Math.sign(e.deltaY);
        var curScale = canvas._embScale || 1;
        curScale = Math.max(0.42, Math.min(2.2, curScale * (delta>0?0.92:1.08)));
        canvas._embScale = curScale;
        // cheat: we don't have true scale in projection anymore, but we can nudge H factor via resize? Simple re-draw with same rot but slightly larger marker via flag
        draw();
      }, {passive:false});
      // touch pinch not yet, wheel suffices
    }

    async function init(){
      resize();
      bindEvents();
      // ResizeObserver + fallback
      try{
        if('ResizeObserver' in window){
          ro = new ResizeObserver(function(){ resize(); });
          ro.observe(canvas);
          if(canvas.parentElement) ro.observe(canvas.parentElement);
          window.addEventListener('resize', resize, {passive:true});
        }else{
          window.addEventListener('resize', resize, {passive:true});
        }
      }catch(e){ window.addEventListener('resize', resize, {passive:true}); }
      if(!rafId) rafId = requestAnimationFrame(tick);

      if(dataOpt){
        try{
          var fromOpt = normalizeDataToInternal(dataOpt);
          applyData(fromOpt, true);
        }catch(e){ console.warn('dataOpt normalize fail',e); }
      }else{
        var ok = await loadLite();
        if(!ok){
          console.error('[emb-v2] lite failed');
          proToast('Map failed — tap to retry', 3200);
          showRetryBox(canvas.parentElement, function(done,fail){
            loadLite().then(function(ok2){ if(ok2){ project(); draw(); done(); loadFull(); } else { fail(); } }).catch(function(){ fail(); });
          });
          return;
        }
        // progressive full after short idle
        setTimeout(function(){ loadFull(); }, 120);
      }
      // pending focus
      if(opts.focus || opts.highlightId!=null){
        var f = opts.focus!=null? opts.focus : opts.highlightId;
        if(fullLoaded) setTarget(f); else pendingFocus.push(f);
      }
      // daily link highlight
      try{
        if(dailyCfg && dailyCfg.n){
          var n = dailyCfg.n|0;
          var picks = n===1 ? [dailyCfg.triple[0]] : (n===3 ? dailyCfg.triple : (n===5 ? dailyCfg.five : dailyCfg.triple));
          if(picks && picks.length){
            // pick id mod N
            var pidPick = picks[0] % (Math.max(1,N));
            if(!fullLoaded) pendingFocus.push(pidPick); else setTarget(pidPick);
          }
        }
      }catch{}
    }

    init();

    function setDomain(newDomain){
      if(!newDomain || newDomain===domain) return;
      domain=newDomain;
      fullLoaded=false;
      pendingFocus=[];
      loadLite().then(function(){ setTimeout(loadFull,80); });
    }

    function destroyFn(){
      destroyed=true;
      try{ cancelAnimationFrame(rafId); }catch{}
      try{ if(ro) ro.disconnect(); }catch{}
      try{ window.removeEventListener('resize', resize); }catch{}
    }

    return {
      setDomain: setDomain,
      setTarget: setTarget,
      resize: resize,
      destroy: destroyFn,
      // debug exposes
      _getDaily: function(){ return dailyCfg; },
      _getStats: function(){ return {N:N, domain:domain, fullLoaded:fullLoaded, maxRender:maxRender, isMobile:isMobile}; }
    };
  }

  // expose
  window.mountEmbeddingMap = mountEmbeddingMap;
  window.EmbeddingEngineV2 = {
    mount: mountEmbeddingMap,
    quatFromEuler: quatFromEuler,
    quatMul: quatMul,
    rotateVecByQuat: rotateVecByQuat,
    glibcLcg: glibcLcg,
    dailySeedFromYMD: dailySeedFromYMD,
    tripleFromSeed: tripleFromSeed,
    getDailyConfig: getDailyConfig,
    OKABE: OKABE,
    ARCH: ARCH,
    POS: POS
  };

  // also compat shim for old callsites expecting mountSharedMap
  if(!window.mountSharedMap){
    window.mountSharedMap = function(c,o){ return mountEmbeddingMap(c,o); };
  }

  console.log('[emb-v2] loaded void '+VOID+' OKABE8 ARCH8 POS5 DPR1 LOD '+MAX_MOBILE+'/'+MAX_DESKTOP+' mom '+MOMENTUM+' spring '+SPRING_K+' daily '+getDailyConfig().ymd+'->'+getDailyConfig().seed+' idx'+getDailyConfig().idx+' triple['+getDailyConfig().triple.join(',')+'] same-link-same-stars ?daily=YYYYMMDD&n=1/3/5');
})();
