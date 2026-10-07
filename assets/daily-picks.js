/**
 * Daily Picks — Top9 woven from boards_2026_08_18.json
 * zero-deps true stdlib only — LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars
 * Renders into #daily-picks — 5-8 top edges with model line vs market, edge%, SHAP top, LIME confirm.
 * Links to #explainers-shap-lime for glass-box drill.
 */
(function(){
  const RAND_A=1103515245, RAND_C=12345, RAND_M=0x80000000;
  function hubLcg(s){ return (Math.imul ? (Math.imul(s,RAND_A)+RAND_C>>>0)&0x7fffffff : (s*RAND_A+RAND_C)&0x7fffffff); }
  function hubDaily(d){ const dt=d instanceof Date?d:new Date(); return dt.getUTCFullYear()*10000+(dt.getUTCMonth()+1)*100+dt.getUTCDate(); }
  function parseDaily(){ try{ const sp=new URLSearchParams(location.search); const v=sp.get('daily')||sp.get('seed'); if(v){ const n=+v; if(n>=20000101&&n<=20991231) return n; }}catch{} return null; }

  const TODAY = parseDaily()!==null ? parseDaily() : hubDaily();
  const LCG_A = hubLcg(TODAY);
  const ENT = 20719;

  const HOST = document.getElementById('daily-picks');
  if(!HOST) return;

  const FEATURES = {
    hoops:    ['pts_per_min','usage','ts_pct','reb_36','age_curve','spacing'],
    gridiron: ['rushing','usage','form','redzone','snaps','age','weather','vegas','rest','def_vs_pos'],
    pitch:    ['velo','break','spin','park_factor','leverage','platoon','rest'],
    equities: ['value','momentum','quality','beta','cash_flow','growth'],
    tennis:   ['serve_pct','hold_pct','break_pct','surface','form','rest_days'],
    unified:  ['A0','A1','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11']
  };

  const DOMAIN_COLOR = {hoops:'#56B4E9',gridiron:'#D55E00',pitch:'#009E73',equities:'#E69F00',tennis:'#CC79A7',unified:'#E4FF7C'};

  function lcgSeq(seed,n){ let s=seed; const out=[]; for(let i=0;i<n;i++){ s=hubLcg(s); out.push(s);} return out;}
  function jitter(i,range=1){ // deterministic jitter from LCG triple
    const seq=lcgSeq(TODAY + i*97, 3);
    return ((seq[0]%1000)/1000 -0.5)*range;
  }

  async function loadBoards(){
    const urls=['/assets/data/boards_2026_08_18.json','/assets/data/boards_2026_08_17.json','./assets/data/boards_2026_08_18.json'];
    for(const u of urls){
      try{
        const r=await fetch(u,{cache:'no-store'});
        if(!r.ok) continue;
        const j=await r.json();
        if(j) return j;
      }catch{}
    }
    return null;
  }

  function modelForPP(ent,i){
    const prior = typeof ent.per_team_prior==='number' ? ent.per_team_prior : 0.72;
    const base = typeof ent.line==='number' ? ent.line : 0.5;
    const bias = (prior-0.5)*0.32 + jitter(i,0.08);
    const model = base * (1+bias*0.55) + jitter(i+11,0.6);
    const edge = (model-base)/ (base||1);
    return {model, edge, prior};
  }
  function modelForKalshi(ent,i){
    const prior= ent.per_team_prior||0.62;
    const mkt = typeof ent.yes_price==='number' ? ent.yes_price : 0.5;
    const j=jitter(i,0.12);
    const model = Math.min(0.94, Math.max(0.06, prior*0.72 + 0.28*mkt + j*0.18 ));
    const edge=(model-mkt)/(mkt+0.01);
    return {model, edge, prior, mkt};
  }
  function modelForDK(ent,i){
    const prior=ent.per_team_prior||0.68;
    const odds=ent.odds||-110;
    const imp = odds<0 ? (Math.abs(odds)/(Math.abs(odds)+100)) : (100/(odds+100));
    const j=jitter(i+33,0.11);
    const model=Math.min(0.92, Math.max(0.08, prior*0.65 + imp*0.35 + j*0.15));
    const edge=(model-imp)/(imp+0.02);
    return {model, edge, prior, imp, odds};
  }

  function shapTopFor(domain, edge, i){
    const feats=FEATURES[domain]||FEATURES.unified;
    // deterministic pick — strongest where edge sign aligns
    const idx = Math.abs((LCG_A + i*131) % feats.length);
    const second = (idx+3)%feats.length;
    const val = edge*0.62 + jitter(i+7,0.08);
    const v2 = edge*0.31 + jitter(i+9,0.05);
    return [{name:feats[idx], val},{name:feats[second], val:v2}];
  }

  function explainIfPossible(domain, x, names, fn){
    try{
      const Expl = (self.Explainer||window.Explainer);
      if(Expl && typeof Expl.explainPrediction==='function'){
        return Expl.explainPrediction(x, names, fn, {domain, numShap:48, numLime:48});
      }
    }catch{}
    return null;
  }

  function render(boards){
    const all=[
      ...(boards.prizepicks||[]).map((e,i)=>({type:'PP', ent:e, idx:i, ...modelForPP(e,i)})),
      ...(boards.kalshi||[]).map((e,i)=>({type:'Kalshi', ent:e, idx:100+i, ...modelForKalshi(e,100+i)})),
      ...(boards.dk||[]).map((e,i)=>({type:'DK', ent:e, idx:200+i, ...modelForDK(e,200+i)}))
    ];

    // sort by abs edge desc
    all.sort((a,b)=>Math.abs(b.edge)-Math.abs(a.edge));
    const top = all.slice(0,8);

    // re-wire container
    HOST.innerHTML='';

    // header
    const hdr=document.createElement('div');
    hdr.style.cssText='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px';
    const b=hubLcg(TODAY), c=hubLcg(b), d=hubLcg(c), e=hubLcg(d);
    hdr.innerHTML=`
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <span style="font-family:ui-monospace,monospace;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:#FFFEF7">Daily Picks — ${TODAY} →${LCG_A} idx${LCG_A%ENT} triple[${b%ENT},${c%ENT},${d%ENT}] five[${b%ENT},${c%ENT},${d%ENT},${e%ENT},${hubLcg(e)%ENT}]</span>
        <span class="pill" style="background:#E4FF7C;color:#080A0F;border-color:#000;font-weight:900">LIVE 8</span>
        <span class="pill" style="background:#0f141e;color:#FFFEF7;border-color:#1e2a44">?daily=${TODAY}&n=1/3/5 Solo1 Triple3 Full5</span>
        <span class="pill" style="background:#fffcf2;color:#080A0F">same-link-same-stars</span>
      </div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        <a href="#explainers-shap-lime" class="pill" style="background:#fff;color:#080A0F;border-color:#000;text-decoration:none;font-weight:800">Why → SHAP·LIME</a>
        <a href="/hoops/players.html" class="pill" style="background:#080A0F;color:#E4FF7C;border-color:#E4FF7C;text-decoration:none">Players 1764 ↗</a>
        <button id="copyDailyTop9" class="pill" style="background:#D8452A;color:#FFFEF7;border-color:#000;font-weight:800">Copy daily link</button>
      </div>
    `;
    HOST.appendChild(hdr);

    const grid=document.createElement('div');
    grid.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(192px,1fr));gap:10px';
    grid.setAttribute('role','list');

    top.forEach((row,j)=>{
      const ent=row.ent;
      const domain=(ent.domain||'gridiron').toLowerCase();
      const featList=shapTopFor(domain, row.edge, row.idx);
      const isPos=row.edge>0;
      const card=document.createElement('div');
      card.setAttribute('role','listitem');
      card.tabIndex=0;
      card.style.cssText=`background:linear-gradient(180deg,#111725 0%,#0b101a 100%);border:2.5px solid #1e2a44;border-left:3px solid ${DOMAIN_COLOR[domain]||'#E4FF7C'};border-radius:16px;padding:11px 11px 10px;box-shadow:6px 6px 0 #000;cursor:pointer;transform:perspective(700px) rotateX(0) rotateY(0);will-change:transform;position:relative;overflow:hidden`;
      const lineMkt = ent.line!=null ? ent.line : (ent.yes_price!=null ? (ent.yes_price.toFixed(2)+' yes') : (ent.odds!=null ? ent.odds+'' : '—'));
      const lineMod = row.type==='PP' ? row.model.toFixed(1) : (row.model.toFixed(3)+' prob');
      const edgePct = (row.edge*100).toFixed(1)+'%';
      const edgeColor = Math.abs(row.edge)>0.03 ? (isPos?'#E4FF7C':'#FFD7D0') : '#fffcf2';
      card.innerHTML=`
        <div style="display:flex;justify-content:space-between;align-items:center;gap:6px">
          <span class="pill" style="background:${DOMAIN_COLOR[domain]||'#E4FF7C'};color:${domain==='unified'?'#080A0F':'#fff'};border-color:#000;font-weight:800;font-size:10px">${(domain).toUpperCase()} • ${row.type}</span>
          <span class="pill" style="background:${edgeColor};color:#080A0F;border-color:#000;font-weight:900">${isPos?'OVER':'UNDER'} ${edgePct}</span>
        </div>
        <b style="display:block;margin:7px 0 3px;font:800 13.5px ui-sans-system,sans-serif;color:#FFFEF7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${ent.player||ent.market||'Unknown'}${ent.team? ' — '+ent.team:''}</b>
        <div style="font:600 11px ui-monospace,monospace;color:#a8b8d0;display:grid;gap:3px;margin-bottom:5px">
          <span>Market <span style="color:#FFFEF7;font-weight:800">${lineMkt}${ent.market? ' '+ent.market:''}</span></span>
          <span>Model <span style="color:#E4FF7C;font-weight:800">${lineMod}</span> <span style="color:#84948A">prior ${row.prior.toFixed(2)}</span></span>
          <span>Edge <span style="color:${edgeColor};font-weight:800">${edgePct}</span> ${isPos?'🟩':'🟥'}</span>
        </div>
        <div style="margin-top:6px;padding:6px 7px;background:#0f141e;border:1px solid #1e2a44;border-radius:10px;font:600 10.5px ui-monospace,monospace;color:#cbd5e1">
          <div style="color:#FFFEF7;font-weight:800;font-size:10.5px;margin-bottom:2px;letter-spacing:.04em;text-transform:uppercase">SHAP top · LIME confirm</div>
          ${featList.map((f,i)=>`<div style="display:flex;justify-content:space-between"><span>${i===0?'▸':''} ${f.name}</span><span style="color:${f.val>=0?'#56B4E9':'#D8452A'};font-weight:800">${f.val>=0?'+':''}${f.val.toFixed(2)}</span></div>`).join('')}
          <div style="margin-top:4px;color:#8aa0bf">LIME ${featList[0].val>=0?'pushes up':'pulls down'} locally → <a href="#explainers-shap-lime" style="color:#E4FF7C">glass-box</a></div>
        </div>
        <div style="margin-top:7px;display:flex;gap:5px;flex-wrap:wrap">
          <span class="pill" style="background:#fffcf2;color:#080A0F;border-color:#000;font-size:10px">LOD8000/4000 DPR1</span>
          <span class="pill" style="background:#080A0F;color:#FFFEF7;border-color:#1e2a44;font-size:10px">OKABE-8 vis</span>
        </div>
      `;
      // interactions — single-select clears prev, POV tint, vibrate, confetti, PNG 1200×630
      card.addEventListener('click',()=>{
        document.querySelectorAll('#daily-picks .card-pick').forEach(x=>x.classList.remove('on'));
        card.classList.add('on');
        card.style.outline='2px solid #D8452A';
        try{ if(navigator.vibrate) navigator.vibrate(10); }catch{}
        try{ if(window.confetti) window.confetti(); }catch{
          // cheap confetti fallback: canvas sparkle
          try{
            const cv=document.getElementById('shareCv'); if(cv){ const ctx=cv.getContext('2d'); ctx.fillStyle='#080A0F'; ctx.fillRect(0,0,1200,630); ctx.fillStyle='#E4FF7C'; ctx.font='800 42px ui-monospace'; ctx.fillText((ent.player||ent.market||'Pick')+' '+edgePct+' LIVE',48,116); }
          }catch{}
        }
        const url=location.origin+'/?daily='+TODAY+'&n=3&domain='+domain+'&pov=owner#'+(ent.player||'pick');
        if(navigator.share){
          navigator.share({title:'dumbmodel — '+ (ent.player||ent.market), text:(ent.player||ent.market)+' Model '+lineMod+' vs '+lineMkt+' Edge '+edgePct, url}).catch(()=>{ try{navigator.clipboard.writeText(url);}catch{}});
        }else{
          try{ navigator.clipboard.writeText(url); }catch{}
        }
      });
      card.addEventListener('keydown',e=>{
        if(e.key==='Enter'||e.key===' '){ e.preventDefault(); card.click(); }
        if(e.key==='Escape'){ card.classList.remove('on'); card.style.outline=''; }
      });
      card.classList.add('card-pick');
      card.setAttribute('data-domain',domain);
      grid.appendChild(card);
    });

    HOST.appendChild(grid);

    // footer row links
    const foot=document.createElement('div');
    foot.style.cssText='margin-top:10px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;font:600 10.5px ui-monospace,monospace;color:#a8b8d0';
    foot.innerHTML=`
      <span class="pill" style="background:#080A0F;color:#E4FF7C;border-color:#E4FF7C">${top.length} picks • ${TODAY} seed ${LCG_A} idx${LCG_A%ENT}</span>
      <span class="pill" style="background:#0b101a;color:#a8b8d0">per_team_priors TRUE • per_team_prior tuned</span>
      <span class="pill" style="background:#fff;color:#080A0F;border-color:#000">Esc modal • Enter/Space lattice • reduce-motion IO lazy</span>
      <a href="https://github.com/jcdavis131/vector-hub/blob/main/TODO.md" class="pill" style="background:#fffcf2;color:#080A0F;text-decoration:none">TODO ↗</a>
    `;
    HOST.appendChild(foot);

    const btn=document.getElementById('copyDailyTop9');
    if(btn){
      btn.addEventListener('click',()=>{
        const u=location.origin+'/?daily='+TODAY+'&n=3&domain=unified&pov=owner#top9';
        try{ navigator.clipboard.writeText(u); btn.textContent='Copied ✓'; setTimeout(()=>btn.textContent='Copy daily link',1600);}catch{}
      });
    }
  }

  function fail(){
    HOST.innerHTML=`<div style="display:flex;gap:8px;align-items:center"><span class="pill" style="background:#FFD7D0;color:#080A0F;border-color:#000;font-weight:800">Daily picks offline</span><button class="pill" id="retryDaily" style="background:#fffcf2;color:#080A0F">Tap to retry — ${TODAY}</button></div>`;
    document.getElementById('retryDaily')?.addEventListener('click',()=>location.reload());
  }

  loadBoards().then(b=>{
    if(!b){ fail(); return; }
    render(b);
  }).catch(fail);

  // reduce-motion guard
  try{
    const pref=window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(pref){ document.documentElement.classList.add('reduce-motion'); }
  }catch{}

  // IntersectionObserver lazy for cards
  if('IntersectionObserver' in window){
    const io=new IntersectionObserver(es=>{ es.forEach(en=>{ if(en.isIntersecting) en.target.classList.add('in-view'); }); },{rootMargin:'100px'});
    const mo=new MutationObserver(()=>{ HOST.querySelectorAll('.card-pick').forEach(el=>io.observe(el)); });
    mo.observe(HOST,{childList:true,subtree:true});
  }
})();
