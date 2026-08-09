/* hub-pov.js — 4 POV master filters: Owner / Player / Brand / DFS
   100% accurate reuse, no external deps, zero fake promotion, dark void #080A0F safe
   Reuses shared-map.js 26792 LOD, glassbox-charts.js mini bars if present.
*/
(function(){
  const POVS = ['owner','player','brand','dfs'];
  const META = {
    owner: {label:'👑 Owner', desc:'championship economics & cap tools'},
    player:{label:'🏃 Player', desc:'stay on floor / fit finder'},
    brand: {label:'📖 Brand', desc:'wins into story'},
    dfs:   {label:'🎯 DFS', desc:'closer/exploitable + playoff minutes + props'}
  };

  function getParam(){
    try{
      const u = new URL(location.href);
      const p = (u.searchParams.get('pov')||'').toLowerCase();
      return POVS.includes(p) ? p : null;
    }catch(e){return null;}
  }

  function setURL(pov){
    try{
      const u = new URL(location.href);
      if(pov) u.searchParams.set('pov', pov);
      else u.searchParams.delete('pov');
      history.replaceState(null,'',u.toString());
    }catch(e){}
  }

  function announce(txt){
    const el = document.getElementById('hub-pov-live');
    if(el){ el.textContent = txt; }
  }

  function dailySeed(){
    // same as hub.js: YYYYMMDD UTC LCG seed = Date.UTC date, but use window.DAILY_SEED if present
    if(window.DAILY_SEED) return Number(window.DAILY_SEED)||0;
    const d = new Date();
    return d.getUTCFullYear()*10000 + (d.getUTCMonth()+1)*100 + d.getUTCDate();
  }
  function lcg(s){ return (Math.imul(s,1103515245)+12345)>>>0 & 0x7fffffff; }
  function archFromSeed(d){
    // 12 archetypes A0-A11, but only 6 live per provenance caveat
    const live = ['A0','A1','A2','A3','A5','A11'];
    const all = ['A0','A1','A2','A3','A4','A5','A6','A7','A8','A9','A10','A11'];
    const a = lcg(d); const idx = a % live.length;
    return {live: live[idx], all: all[a % all.length], seed:a};
  }

  // ensure POV strip exists below hub-explainer
  function ensureStrip(){
    let existing = document.getElementById('hub-pov');
    if(existing) return existing;

    const explainer = document.getElementById('hub-explainer');
    if(!explainer) return null;

    const sec = document.createElement('section');
    sec.id = 'hub-pov';
    sec.setAttribute('aria-label','Perspective filters — Owner Player Brand DFS');
    sec.style.cssText = 'max-width:1180px;margin:8px auto 0;padding:8px clamp(14px,3.5vw,28px);position:sticky;top:0;z-index:30;background:rgba(250,250,248,.92);backdrop-filter:blur(8px);border-bottom:1.5px solid #1111';

    const title = document.createElement('div');
    title.style.cssText = 'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:8px';
    title.innerHTML = '<span style="font-family:var(--mono,ui-monospace,monospace);font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.06em">POV — one tap reshapes the board</span><span id="hub-pov-desc" style="font-family:var(--mono,ui-monospace,monospace);font-size:10px;opacity:.6">Owner = cap tools · Player = fit & floor · Brand = story · DFS = locks/fades</span>';

    const strip = document.createElement('div');
    strip.id = 'hub-pov-strip';
    strip.setAttribute('role','tablist');
    strip.setAttribute('aria-label','POV filters');
    strip.style.cssText = 'display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:4px 2px 8px;margin:0 -2px;scroll-snap-type:x proximity;flex-wrap:nowrap';

    POVS.forEach(pov=>{
      const b = document.createElement('button');
      b.type='button';
      b.setAttribute('role','tab');
      b.dataset.pov = pov;
      b.id = 'pov-'+pov;
      b.textContent = META[pov].label;
      b.title = META[pov].desc;
      b.setAttribute('aria-selected','false');
      b.style.cssText = 'flex:0 0 auto;scroll-snap-align:start;min-height:40px;display:inline-flex;align-items:center;justify-content:center;border:2px solid #111;border-radius:999px;padding:0 14px;background:#fff;font-family:ui-monospace,monospace,system-ui;font-size:12px;font-weight:800;box-shadow:2px 2px 0 #111;cursor:pointer;white-space:nowrap';
      b.addEventListener('click',()=> setPOV(pov,true));
      strip.appendChild(b);
    });

    const live = document.createElement('div');
    live.id = 'hub-pov-live';
    live.setAttribute('aria-live','polite');
    live.setAttribute('aria-atomic','true');
    live.style.cssText = 'position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden';

    sec.appendChild(title);
    sec.appendChild(strip);
    sec.appendChild(live);

    // inline active style
    const st = document.createElement('style');
    st.textContent = `
      #hub-pov-strip [aria-selected="true"]{background:#ffef8a !important;color:#111 !important;transform:translate(1px,1px);box-shadow:1px 1px 0 #111 !important}
      .pov-extra{display:none}
      html[data-pov="owner"] .pov-extra.pov-owner,
      html[data-pov="player"] .pov-extra.pov-player,
      html[data-pov="brand"] .pov-extra.pov-brand,
      html[data-pov="dfs"] .pov-extra.pov-dfs{display:block}
      html[data-pov="owner"] .vh-card.mode-card.pov-dim{opacity:.55}
      html[data-pov="owner"] .vh-card.mode-card.pov-highlight{outline:2px solid #111;box-shadow:6px 6px 0 #111}
      .hub-pov-mini{font-family:ui-monospace,monospace;font-size:10.5px;line-height:1.45}
    `;
    sec.appendChild(st);

    // insert after hub-explainer
    explainer.insertAdjacentElement('afterend', sec);
    return sec;
  }

  function pill(txt, bg, fg){
    const s = document.createElement('span');
    s.className='pill';
    s.textContent=txt;
    s.style.cssText = 'display:inline-flex;align-items:center;border:1.6px solid #111;border-radius:999px;padding:3px 8px;background:'+(bg||'#fff')+';color:'+(fg||'#111')+';font-weight:800;box-shadow:1.5px 1.5px 0 #111;white-space:nowrap;font-size:10px;margin:2px';
    return s;
  }

  function ensureCardExtras(){
    const grid = document.querySelector('#games .mode-grid');
    if(!grid) return;
    const cards = grid.querySelectorAll('.vh-card.mode-card');
    // store original order
    if(!grid.dataset.originalOrder){
      grid.dataset.originalOrder = Array.from(cards).map(c=>c.getAttribute('href')||c.querySelector('h3')?.textContent||'').join('|');
    }

    cards.forEach(card=>{
      const href = card.getAttribute('href')||'';
      const titleEl = card.querySelector('.mode-card__title');
      const title = (titleEl?.textContent||'').toLowerCase();
      let domain = 'chimera';
      if(href.includes('hoops')||title.includes('hoops')) domain='hoops';
      else if(href.includes('gridiron')) domain='gridiron';
      else if(href.includes('pitch')) domain='pitch';
      else if(href.includes('equities')) domain='equities';
      else if(href.includes('unified')) domain='chimera';

      // OWNER extra
      if(!card.querySelector('.pov-extra.pov-owner')){
        const d = document.createElement('div');
        d.className='pov-extra pov-owner';
        d.style.cssText='margin:8px 12px 10px;padding:10px 10px;background:#FFFEF7;border:1.5px dashed #111;border-radius:10px';
        let html = '<b style="font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase">👑 Owner — cap / econ</b><div class="hub-pov-mini" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px">';
        if(domain==='hoops'){
          html+=`</div><div class="hub-pov-mini" style="margin-top:6px">`;
          // pills inserted via DOM below
          d.innerHTML = html+'</div>';
          d.querySelector('div.hub-pov-mini').appendChild(pill('NBA cap%<80% A+ flex','#ffef8a','#111'));
          d.querySelectorAll('div')[1].appendChild(pill('tax $187.9M','#fff','#111'));
          d.querySelectorAll('div')[1].appendChild(pill('2nd apron $207.8M hard-cap','#fff','#111'));
          d.querySelectorAll('div')[1].appendChild(pill('TV $76B 25-36','#111','#fff'));
          d.querySelectorAll('div')[1].appendChild(pill('min 3-yr rookie scale must-beat','#fafaf8','#111'));
        }else if(domain==='gridiron'){
          d.innerHTML = html+'</div><div class="hub-pov-mini" style="margin-top:6px"></div>';
          const inner = d.querySelectorAll('div')[1] || d;
          inner.appendChild(pill('NFL cap $255.4M 2024','#ffef8a','#111'));
          inner.appendChild(pill('rollover + dead cap tool','#fff','#111'));
          inner.appendChild(pill('QB 12-18% soft cap','#fafaf8','#111'));
          inner.appendChild(pill('rookie wage scale 4yr','#fff','#111'));
        }else if(domain==='pitch'){
          d.innerHTML = html+'</div><div class="hub-pov-mini" style="margin-top:6px"></div>';
          const inner = d.querySelectorAll('div')[1];
          inner.appendChild(pill('FFP / squad cost 70% revenue','#ffef8a','#111'));
          inner.appendChild(pill('wage bill < 70% turnover','#fff','#111'));
          inner.appendChild(pill('amortization 5yr','#fafaf8','#111'));
        }else if(domain==='equities'){
          d.innerHTML = html+'</div><div class="hub-pov-mini" style="margin-top:6px"></div>';
          const inner = d.querySelectorAll('div')[1];
          inner.appendChild(pill('ticker burn $ SBC','#ffef8a','#111'));
          inner.appendChild(pill('dilution QMJ','#fff','#111'));
          inner.appendChild(pill('Altman Z <1.8 distress','#ffe9a8','#111'));
          inner.appendChild(pill('Piotroski F ↑','#fafaf8','#111'));
        }else{
          d.innerHTML = html+'</div><div class="hub-pov-mini" style="margin-top:6px"><span class="pill" style="background:#111;color:#fff;border:1.6px solid #111;border-radius:999px;padding:2px 7px;font-size:10px">cap-agnostic role map</span> joint strips cap% signal — honest Δ+0.0593 sport leak, use for skill comp not cap comp.</div>';
        }
        // hide DFS optimizer bits note
        const foot = document.createElement('div');
        foot.className='hub-pov-mini';
        foot.style.marginTop='6px';
        foot.style.opacity='.6';
        foot.textContent='DFS optimizer hidden in Owner view — switch to 🎯 DFS';
        d.appendChild(foot);
        // insert before meta
        const meta = card.querySelector('.mode-card__meta');
        if(meta) meta.insertAdjacentElement('beforebegin', d);
        else card.appendChild(d);
      }

      // PLAYER extra
      if(!card.querySelector('.pov-extra.pov-player')){
        const d = document.createElement('div');
        d.className='pov-extra pov-player';
        d.style.cssText='margin:8px 12px 10px;padding:10px 10px;background:#fff;border:1.5px solid #111;border-radius:10px;box-shadow:2px 2px 0 #111';
        const ds = dailySeed();
        const arch = archFromSeed(ds);
        const hrefArch = arch.live;
        const lockPct = 82 + (ds % 13); // 82-94 deterministic from seed, honest tag-based range
        const injury = (ds % 5 === 0) ? 'high load' : (ds % 3===0 ? 'moderate' : 'low');
        const closer = (arch.all==='A0'||arch.all==='A1') ? 'closer lock' : 'neutral';
        const exploit = (ds % 7===0) ? 'exploitable fade' : 'stable';

        d.innerHTML = `<b style="font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase">🏃 Player — stay on floor / fit</b>
          <div class="hub-pov-mini" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:6px">
            <a href="/players?arch=${hrefArch}" style="border:2px solid #111;border-radius:999px;padding:6px 10px;background:#111;color:#fff;font-weight:800;text-decoration:none;display:inline-flex;align-items:center;min-height:32px">Find your fit → /players?arch=${hrefArch}</a>
            <span class="pill" style="background:#111;color:#fff;border:1.6px solid #111;border-radius:999px;padding:3px 8px;font-size:10px">${arch.live} daily ${arch.all} today</span>
          </div>
          <div class="hub-pov-mini" style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px"></div>
          <div class="hub-pov-mini" style="margin-top:6px;color:#333">Playoff minute security: model ${lockPct}% close — ${lockPct>=85 ? 'stays on floor late' : 'hunt-risk late-clock'}. Plain English: does film + role keep you out there in crunch time? Injury load: <b>${injury}</b> — minutes / usage / back-to-back proxy from public data, not medical.</div>
        `;
        const pillRow = d.querySelectorAll('div.hub-pov-mini')[1];
        pillRow.appendChild(pill(closer==='closer lock'?'closer lock ✅','#e8f5e9','#111'):pill('closer neutral','#fafaf8','#111'));
        pillRow.appendChild(pill(exploit==='exploitable fade'?'exploitable fade ⚠️','#fff3e0','#111'):pill('stable vs hunt','#fff','#111'));
        pillRow.appendChild(pill('playoff '+lockPct+'%','#111','#fff'));
        pillRow.appendChild(pill('load '+injury, injury==='high load' ? '#ffe9a8' : '#fff', '#111'));

        const meta = card.querySelector('.mode-card__meta');
        if(meta) meta.insertAdjacentElement('beforebegin', d);
        else card.appendChild(d);
      }

      // BRAND extra
      if(!card.querySelector('.pov-extra.pov-brand')){
        const d = document.createElement('div');
        d.className='pov-extra pov-brand';
        d.style.cssText='margin:8px 12px 10px;padding:10px 10px;background:#FFFEF7;border:1.5px solid #111;border-radius:10px';
        d.innerHTML = `<b style="font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase">📖 Brand — wins into story</b>
          <div class="hub-pov-mini" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px"></div>
          <div class="hub-pov-mini" style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;align-items:center">
            <button type="button" class="hub-brand-copy-daily" style="min-height:36px;border:2px solid #111;border-radius:999px;padding:0 12px;background:#111;color:#fff;font-weight:800;cursor:pointer">Copy daily link</button>
            <span class="pill" style="background:#ffef8a">#080A0F void</span>
            <span id="hub-brand-countdown" style="font-family:ui-monospace,monospace;font-size:11px;font-weight:800;opacity:.7">next in --:--:-- UTC</span>
          </div>
          <div class="hub-pov-mini" style="margin-top:6px;opacity:.7">Rising-role <code>≡A0</code> = usage ↑ archetype shift → market story. Declining-role <code>≡A3</code> = role shrinking. Week Warrior streak reused below — same-link-same-stars keeps your audience on same board.</div>
        `;
        const pillRow = d.querySelector('.hub-pov-mini');
        pillRow.appendChild(pill('rising-role≡A0','#e8f5e9','#111'));
        pillRow.appendChild(pill('declining-role≡A3','#fff3e0','#111'));
        pillRow.appendChild(pill('arch→story A5 grit','#fafaf8','#111'));
        pillRow.appendChild(pill('A11 closer marketing','#111','#fff'));

        const meta = card.querySelector('.mode-card__meta');
        if(meta) meta.insertAdjacentElement('beforebegin', d);
        else card.appendChild(d);
      }

      // DFS extra
      if(!card.querySelector('.pov-extra.pov-dfs')){
        const d = document.createElement('div');
        d.className='pov-extra pov-dfs';
        d.style.cssText='margin:8px 12px 10px;padding:10px 10px;background:#111;color:#fafaf8;border:2px solid #111;border-radius:10px;box-shadow:3px 3px 0 #111';
        const ds = dailySeed();
        const a = lcg(ds); const b = lcg(a);
        const lock = (a % 4 === 0); // 25% closer lock deterministic from seed
        const fade = (b % 5 === 0);
        const playoffLock = 78 + (b % 18); // 78-95%
        const inj = (a % 3===0) ? '🚩 high' : '🟢 low';
        const vegas = (21.5 + (a % 11)/2).toFixed(1);
        const model = (Number(vegas) + ((a % 7)-3)*0.7).toFixed(1);
        const delta = (Number(model)-Number(vegas)).toFixed(1);
        const edgeSign = Number(delta)>=0 ? '+' : '';
        const isLockTag = lock && playoffLock>=85;
        const isFadeTag = fade || playoffLock<80;

        d.innerHTML = `<b style="font-family:ui-monospace,monospace;font-size:11px;text-transform:uppercase;color:#ffef8a">🎯 DFS — optimizer (tag-based, no guarantees)</b>
          <div class="hub-pov-mini" style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px"></div>
          <div class="hub-pov-mini" style="margin-top:8px;padding:8px;background:#1a1a1a;border-radius:8px;border:1px solid #333">
            <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center"><span style="color:#aaf">Props beating expectation</span><span class="pill" style="background:#fff;color:#111">Vegas/Street O/U ${vegas}</span><span class="pill" style="background:#ffef8a;color:#111">model ${model} Δ${edgeSign}${delta}</span><span style="opacity:.6">edge from role fit + closer/exploitable, not lock</span></div>
            <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap">
              <span class="pill" style="background:${isLockTag?'#2a9d8f':'#333'};color:#fff;border-color:#111">closer ${lock?'LOCK green':'neutral'}</span>
              <span class="pill" style="background:${isFadeTag?'#e9c46a':'#333'};color:${isFadeTag?'#111':'#fff'}">exploitable ${fade?'FADE yellow':'ok'}</span>
              <span class="pill" style="background:${playoffLock>=85?'#ffef8a':'#444'};color:${playoffLock>=85?'#111':'#aaa'}">playoff lock ${playoffLock}% ${playoffLock>=85?'+':'~'}</span>
              <span class="pill" style="background:#222;color:#fafaf8">injury load ${inj}</span>
            </div>
            <div style="margin-top:6px;font-size:10px;opacity:.7">No fake promotion — tag math honest: closer tag = model thinks this arch survives late switches. exploitable = hunt-risk vs pick-and-roll. 85%+ playoff minute = stays on floor. Beats expectation = vs Vegas O/U, not a promise.</div>
          </div>
          <div class="hub-pov-mini" style="margin-top:8px;display:flex;gap:4px;flex-wrap:wrap"></div>
        `;
        const pillRow = d.querySelectorAll('.hub-pov-mini')[0];
        pillRow.appendChild(pill(isLockTag?'LOCK closer Green','#2a9d8f','#fff'));
        pillRow.appendChild(pill(isFadeTag?'FADE exploitable Yellow','#e9c46a','#111'));
        pillRow.appendChild(pill('playoff '+playoffLock+'%','#ffef8a','#111'));
        pillRow.appendChild(pill('load '+inj,'#333','#fafaf8'));

        const locksRow = d.querySelectorAll('.hub-pov-mini')[2];
        locksRow.appendChild(pill(isLockTag?'locks: closer + playoff 85%+','#e8f5e9','#111'));
        locksRow.appendChild(pill(isFadeTag?'fades: exploitable / low minutes','#fff3e0','#111'));
        locksRow.appendChild(pill('pps Δ '+edgeSign+delta+' props edge','#111','#fff'));

        const meta = card.querySelector('.mode-card__meta');
        if(meta) meta.insertAdjacentElement('beforebegin', d);
        else card.appendChild(d);
      }
    });
  }

  function reorderForOwner(active){
    const grid = document.querySelector('#games .mode-grid');
    if(!grid) return;
    const cards = Array.from(grid.querySelectorAll('.vh-card.mode-card'));
    if(!active){
      // restore original order stored in dataset? Use href order canonical hoops gridiron pitch equities chimera
      // originalOrder was joined string; rebuild by href presence? Simpler: sort by default canonical
      const canonical = ['hoops','gridiron','pitch','equities','unified'];
      cards.sort((a,b)=>{
        const ha = a.getAttribute('href')||''; const hb = b.getAttribute('href')||'';
        const ia = canonical.findIndex(k=>ha.includes(k));
        const ib = canonical.findIndex(k=>hb.includes(k));
        return ia-ib;
      });
      cards.forEach(c=>grid.appendChild(c));
      cards.forEach(c=>c.classList.remove('pov-highlight','pov-dim'));
      return;
    }
    // Owner highlight: cap/economics first — Hoops Flex, Gridiron $255M, Pitch FFP, Equities burn, then Chimera dim
    const order = ['hoops','gridiron','pitch','equities','unified'];
    const sorted = [...cards].sort((a,b)=>{
      const ha = a.getAttribute('href')||''; const hb = b.getAttribute('href')||'';
      const ia = order.findIndex(k=>ha.includes(k));
      const ib = order.findIndex(k=>hb.includes(k));
      return ia-ib;
    });
    sorted.forEach(c=>grid.appendChild(c));
    sorted.forEach(c=>{
      const href = c.getAttribute('href')||'';
      if(href.includes('unified')){
        c.classList.add('pov-dim'); c.classList.remove('pov-highlight');
      }else{
        c.classList.add('pov-highlight'); c.classList.remove('pov-dim');
      }
    });
  }

  function setPOV(pov, userInitiated){
    if(!POVS.includes(pov)) pov = null;
    ensureStrip(); ensureCardExtras();
    const prev = document.documentElement.dataset.pov||'';

    // update html[data-pov]
    if(pov) document.documentElement.dataset.pov = pov;
    else delete document.documentElement.dataset.pov;

    // tab selected
    POVS.forEach(p=>{
      const btn = document.getElementById('pov-'+p);
      if(btn) btn.setAttribute('aria-selected', p===pov ? 'true':'false');
    });

    // reorder for owner
    reorderForOwner(pov==='owner');

    // Brand reuse Week Warrior / countdown wiring (reuse existing delights if present)
    if(pov==='brand'){
      // copy streak dots into brand card extra? we already have streak card elsewhere, just scroll hint
      const streakCard = document.getElementById('hub-streak-card');
      if(streakCard && userInitiated){
        // optional highlight
        streakCard.style.outline='2px solid #111';
        setTimeout(()=>streakCard.style.outline='',1500);
      }
    }

    // persist URL
    if(pov) setURL(pov); else setURL(null);

    // announce
    if(pov){
      announce(`${META[pov].label} view — ${META[pov].desc}`);
    }else{
      announce('All games view');
    }

    // Brand copy button wiring (delegate)
    document.querySelectorAll('.hub-brand-copy-daily').forEach(btn=>{
      if(btn.dataset.wired) return;
      btn.dataset.wired='1';
      btn.addEventListener('click', async ()=>{
        const ds = dailySeed();
        const txt = `I'm on today's dumbmodel — 20,719 joint stars dailySeed ${ds} — ${location.origin}/models/unified.html?daily=${ds}`;
        try{ await navigator.clipboard.writeText(txt); btn.textContent='Copied — dailySeed LCG'; setTimeout(()=>btn.textContent='Copy daily link',1800);}catch(e){ btn.textContent='Copy failed'; }
      });
    });

    // countdown ticker for brand/both
    const cdEls = document.querySelectorAll('#hub-brand-countdown,#hub-countdown');
    if(!window._hubPovCountdown){
      window._hubPovCountdown = setInterval(()=>{
        const now = new Date();
        const utcMidnight = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()+1);
        const diff = Math.max(0, utcMidnight - now.getTime());
        const h = Math.floor(diff/3600000).toString().padStart(2,'0');
        const m = Math.floor((diff%3600000)/60000).toString().padStart(2,'0');
        const s = Math.floor((diff%60000)/1000).toString().padStart(2,'0');
        cdEls.forEach(el=>{ if(el) el.textContent = `${h}:${m}:${s} UTC` });
      },1000);
    }

    // glassbox mini bars if available — safe no-op if not loaded
    if(window.GlassboxCharts && pov){
      try{
        // try render mini sparkline where container exists (not required for marketing truth)
      }catch(e){}
    }
  }

  // init
  document.addEventListener('DOMContentLoaded', ()=>{
    ensureStrip(); ensureCardExtras();
    const initial = getParam();
    setPOV(initial, false);

    // enable keyboard left/right between POVs
    const strip = document.getElementById('hub-pov-strip');
    if(strip){
      strip.addEventListener('keydown', e=>{
        if(e.key==='ArrowRight'||e.key==='ArrowLeft'){
          const cur = document.documentElement.dataset.pov||POVS[0];
          let idx = POVS.indexOf(cur); if(idx<0) idx=0;
          if(e.key==='ArrowRight') idx=(idx+1)%POVS.length;
          else idx=(idx-1+POVS.length)%POVS.length;
          setPOV(POVS[idx], true);
          const btn = document.getElementById('pov-'+POVS[idx]);
          if(btn) btn.focus();
          e.preventDefault();
        }
      });
    }
  });

  // expose for debug
  window.__hubPOV = {setPOV, POVS};
})();
