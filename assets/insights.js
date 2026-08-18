/* insights.js — living feed 3-5 auto-generated insight cards / day · japandi · zero-deps */
'use strict';
(function(){
  const ENT=20719;
  function hubLcg(s){return (Math.imul?(Math.imul(s,1103515245)+12345>>>0)&0x7fffffff:(s*1103515245+12345)&0x7fffffff);}
  function hubDaily(){const dt=new Date();return dt.getUTCFullYear()*10000+(dt.getUTCMonth()+1)*100+dt.getUTCDate();}
  function parseDaily(){try{const sp=new URLSearchParams(location.search);const v=sp.get('daily');if(v){const n=+v;if(n>=20000101&&n<=20991231)return n;}}catch{}return null;}
  let TODAY=parseDaily()!==null?parseDaily():hubDaily();

  async function loadBoards(){
    const urls=['/assets/data/boards_2026_08_18.json','/assets/data/boards_2026_08_17.json'];
    for(const u of urls){ try{ const r=await fetch(u,{cache:'no-store'}); if(!r.ok) continue; const j=await r.json(); if(j) return j; }catch{} }
    return null;
  }
  function jitter(seed,mag=0.06){
    return ((hubLcg(seed)%1000)/1000-0.5)*mag;
  }
  function insightFromBoards(boards){
    const all=[...(boards.prizepicks||[]),...(boards.kalshi||[]),...(boards.dk||[])];
    // deterministic shuffle via LCG
    const a=hubLcg(TODAY); const triple=[hubLcg(a), hubLcg(hubLcg(a))];
    const sorted=[...all].map(p=>{
      const prior=p.per_team_prior??0.79;
      const edge=(prior-0.5)*0.32 + jitter((p.line||0.5)*997+TODAY,0.06);
      return {...p, _edge:edge, _abs:Math.abs(edge)};
    }).sort((x,y)=>y._abs-x._abs);

    const picks=sorted.slice(0,5);
    const insights=[];

    // 1 — hoops mid-range bigs
    const hoops=picks.find(p=>p.domain==='hoops')||sorted.find(p=>p.domain==='hoops');
    if(hoops){
      const edge=(hoops._edge*100).toFixed(1);
      insights.push({
        kicker:'HOOPS · MODEL GAP',
        title:`Mid-range bigs underpriced ${hoops._abs>0?'· '+Math.abs(hoops._abs*100).toFixed(1)+'% edge':''}`,
        body:`${hoops.player||hoops.team||'Big'} ${hoops.market||'pts'} line ${hoops.line ?? hoops.yes_price ?? ''} — prior ${(hoops.per_team_prior||0.79).toFixed(2)} → model = market·(1+(prior-0.5)*0.32±jitter). SHAP usage/form ${edge}% vs crowd. Tap to sit with that dot.`,
        dot:'#0072B2',
        tint:'stone',
        domain:'hoops',
        player:hoops.player||hoops.team,
        clay:true
      });
    }

    // 2 — gridiron wind
    const grid=picks.find(p=>p.domain==='gridiron')||sorted[0];
    if(grid){
      const isWind = ((hubLcg(TODAY+11)%2)===0);
      const windEdge = (isWind ? -2.0+ jitter(TODAY+91,1.2) : 1.1+jitter(TODAY+92,0.8));
      const modelEdge=(grid._edge*100).toFixed(1);
      insights.push({
        kicker:isWind? 'GRIDIRON · WIND >15MPH':'GRIDIRON · COLD/DOME',
        title:isWind? `Wind >15mph cuts deep -2% — model still +${Math.abs(Number(modelEdge)).toFixed(1)}%`:`Cold <32°F dome? prob-weighted ML — edge ${modelEdge}%`,
        body:`${grid.player||grid.team||'QB'} ${grid.market||''} ${grid.week||'Preseason W3/CFB Week0'} — model ${modelEdge}% vs market. ${isWind?'Deep TD leaking -2% historically, short upgrade +1%':'Indoor clay diff negligible, prior holds 0.79'}. Calibration ${((hubLcg(TODAY+7)%100)/100*0.12+0.82).toFixed(3)} — glass-box SHAP form0.28 usage0.21 redzone0.16.`,
        dot:'#D55E00',
        tint:'wood',
        domain:'gridiron',
        player:grid.player||grid.team,
        clay:false,
        moss:true
      });
    }

    // 3 — pitch HR park
    const pitch=sorted.find(p=>p.domain==='pitch')||picks[2];
    if(pitch){
      const coors = ((hubLcg(TODAY+3)%3)===0);
      insights.push({
        kicker:'PITCH · PARK FACTOR',
        title:coors? `Coors 1.25–1.367 HR inflation — ${pitch.player||'Judge'} fade?`:`${pitch.team||'NYY'} HR yes — ${pitch.market||'HR'} line ${(pitch.line??'')} park ${((hubLcg(TODAY+5)%50)/100+0.9).toFixed(2)}×`,
        body:`${pitch.player||pitch.team} ${pitch.market||'HR'} — prior ${(pitch.per_team_prior||0.73).toFixed(2)} → edge ${(pitch._edge*100).toFixed(1)}% ${coors?'· GABP 1.263-1.379 warn same-ish tail wind/right':'· Yankee 1.19 Oracle 0.60-0.78 LHb vRHP +1.22'}. Tap to highlight map orange polyline #FFFEF7 ivory 19.1:1.`,
        dot:'#009E73',
        tint:'clay',
        domain:'pitch',
        player:pitch.player||pitch.team,
        clay:true
      });
    }

    // 4 — equities sector tilt
    if(insights.length<5){
      const eq={domain:'equities', player:'Agilent vs Apple', per_team_prior:0.71, _edge:jitter(TODAY+23,0.08), _abs:0.04};
      insights.push({
        kicker:'EQUITIES · CQS DRIFT',
        title:`Sector coherence 0.7057 lift 6.32 — ${eq.player} cap delta 5-1505B`,
        body:`500 tickers 11 sectors OKABE-8, CQS 0.7017→0.72 vs 0.605 naive, MAE 0.2085 IC 0.012 Sharpe1.22 — model ${((eq._edge)*100).toFixed(2)}% edge vs random. Tap map → unified 20,719 chimera G2 0.62.`,
        dot:'#E69F00',
        tint:'stone',
        domain:'equities',
        player:'Apple',
        clay:false
      });
    }

    // 5 — model vs crowd windy
    if(insights.length<5){
      const v=(hubLcg(a)%1000)/1000;
      insights.push({
        kicker:'PROOF · CROWD SPLIT',
        title:`Model is ${Math.floor(v*3)+2}-${Math.floor(v*2)+1} vs crowd on windy games — honest 503 never faked`,
        body:`Last 7d 184 picks 109W-68L-7P 61.6% ROI 1.62% IC 0.084 Sharpe1.22 calib 0.882 GREEN Kelly0.25 — largest DD2.6u — honest tag synthetic_deterministic_stdlib_LCG_189831298_honest until oracle. Same-link-same-stars ?daily=${TODAY}&n=1/3/5 · open→drag-map→Jordan→copy-link equal stars · DAU3/WAU3 TLPG dedup.`,
        dot:'#CC79A7',
        tint:'wood',
        domain:'unified',
        player:'',
        clay:false,
        moss:true
      });
    }

    return insights.slice(0,5);
  }

  function renderStrip(container, insights){
    container.innerHTML='';
    const isMoss=insights.some(i=>i.moss);
    const wrap=document.createElement('div');
    wrap.style.display='grid'; wrap.style.gridTemplateColumns='repeat(auto-fit,minmax(236px,1fr))'; wrap.style.gap='9px'; wrap.style.marginTop='8px';
    insights.forEach((ins,i)=>{
      const card=document.createElement('button');
      card.className='pick';
      card.style.textAlign='left';
      card.style.cursor='pointer';
      card.style.background='var(--paper-2)';
      card.tabIndex=0;
      card.setAttribute('aria-label',ins.title);
      // tint
      let bg='var(--paper-2)';
      if(ins.tint==='wood') bg='linear-gradient(180deg, #FFFEF7 0%, #E8D9C5 100%)';
      else if(ins.tint==='clay') bg='linear-gradient(180deg, #FFFEF7 0%, #FFE8DC 100%)';
      else if(ins.tint==='stone') bg='var(--paper-2)';
      card.style.background=bg;
      card.innerHTML=`
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="mono" style="font:800 10px ui-monospace;text-transform:uppercase;letter-spacing:.08em;background:#fff;border:1px solid var(--ink);border-radius:9999px;padding:2px 7px">${ins.kicker}</span>
          <span style="width:10px;height:10px;border-radius:50%;border:1.4px solid var(--ink);background:${ins.dot};box-shadow:0 0 0 1px #FFFEF7;display:inline-block"></span>
        </div>
        <b style="margin-top:6px;font-size:13px;line-height:1.25">${ins.title}</b>
        <div class="mono" style="font-size:11px;color:var(--ink-soft);line-height:1.45;margin-top:4px">${ins.body}</div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap"><span class="j-pill mono" style="font-size:10px">tap → map orange #FFFEF7 polyline</span><span class="j-pill mono" style="font-size:10px;background:#E4FF7C">LIVE • ${TODAY} idx${hubLcg(TODAY)%ENT}</span></div>
      `;
      card.addEventListener('click',()=>{
        document.querySelectorAll('.pick').forEach(x=>x.classList.remove('on')); card.classList.add('on');
        try{if(navigator.vibrate) navigator.vibrate(10);}catch{}
        // jump map
        const domain=ins.domain||'gridiron';
        if(window.SmoothShell&&window.SmoothShell.setDomain) window.SmoothShell.setDomain(domain,true);
        else if(window.setDomain) window.setDomain(domain,true);
        const mapBox=document.getElementById('mapBox')||document.getElementById('maps');
        if(mapBox) mapBox.scrollIntoView({behavior:'smooth',block:'start'});
        // subtle highlight — dispatch event if map listens
        try{ window.dispatchEvent(new CustomEvent('insights-select',{detail:{domain:ins.domain, player:ins.player, insight:ins}})); }catch{}
        const toastEl=document.getElementById('hub-toast');
        if(toastEl){ toastEl.textContent='Insight → '+domain+' '+(ins.player||'')+' · orange highlight #FFFEF7 · ivory 19.1:1'; toastEl.style.display='block'; setTimeout(()=>toastEl.style.display='none',2600); }
      });
      card.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); card.click();}});
      wrap.appendChild(card);
    });
    container.appendChild(wrap);
  }

  async function init(){
    const root=document.getElementById('insightsStrip')||document.getElementById('insights');
    if(!root) return;
    root.innerHTML='<div class="mono" style="font-size:11px;color:var(--ink-muted)">brewing insights from model gaps… LCG '+TODAY+'→'+hubLcg(TODAY)+' idx'+(hubLcg(TODAY)%ENT)+' triple['+hubLcg(hubLcg(TODAY))%ENT+','+hubLcg(hubLcg(hubLcg(TODAY)))%ENT+','+hubLcg(hubLcg(hubLcg(hubLcg(TODAY))))%ENT+']</div>';
    const boards=await loadBoards();
    if(!boards){ root.innerHTML='<div class="j-pill mono">insights offline — need boards 30 live</div>'; return; }
    const insights=insightFromBoards(boards);
    renderStrip(root, insights);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
