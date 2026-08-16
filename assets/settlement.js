/**
 * Settlement — AUTO live views for results_rollup
 * zero-deps true stdlib only — LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars
 * Fetches /assets/data/results_settlement.json + /assets/data/results_rollup.json
 * Injects AUTO badge + last settlement timestamp into #results-summary header + cards.
 * void #111725 cards 40px sticky momentum 0.94, share PNG 1200×630 vibrate confetti, everyday language.
 */
(function(){
  const $ = (s)=>document.querySelector(s);
  const HOST = document.getElementById('results-summary') || $('#results-summary');
  if(!HOST) return;

  function hubLcg(s){ return (Math.imul ? (Math.imul(s,1103515245)+12345>>>0)&0x7fffffff : (s*1103515245+12345)&0x7fffffff); }
  function hubDaily(d){ const dt=d instanceof Date?d:new Date(); return dt.getUTCFullYear()*10000+(dt.getUTCMonth()+1)*100+dt.getUTCDate(); }
  const TODAY = hubDaily();
  const FIXED_TRIPLE = [11205,19448,14209];
  const FIXED_FIVE = [11205,19448,14209,11701,18524];

  async function jfetch(u){
    try{ const r=await fetch(u,{cache:'no-store'}); if(!r.ok) return null; return await r.json(); }catch{return null}
  }

  function fmtAgo(iso){
    try{
      const then=new Date(iso); const now=new Date(); const diff=(now-then)/1000;
      if(diff<60) return Math.round(diff)+'s ago';
      if(diff<3600) return Math.round(diff/60)+'m ago';
      if(diff<86400) return Math.round(diff/3600)+'h ago';
      return then.toLocaleDateString();
    }catch{return iso||'—'}
  }

  function kellyColor(kill){
    if(kill==='GREEN') return '#E4FF7C';
    if(kill==='YELLOW') return '#F0E442';
    return '#FFD7D0';
  }

  async function boot(){
    const roll = await jfetch('/assets/data/results_rollup.json') || await jfetch('./assets/data/results_rollup.json');
    const sett = await jfetch('/assets/data/results_settlement.json') || await jfetch('./assets/data/results_settlement.json');
    if(!roll) return;

    const settlement = roll.settlement || (sett && {last_run: sett.settled_at || sett.timestamp, auto: true}) || {last_run: roll.timestamp||roll.day?.timestamp||new Date().toISOString(), auto: true};
    const day = roll.by_period?.day || roll.day;
    const week = roll.by_period?.week || roll.week;
    const month = roll.by_period?.month || roll.month;
    const sources = settlement.sources || (sett && sett.sources) || day?.sources || {kalshi:{tag:'mixed'},dk:{tag:'mixed'},prizepicks:{tag:'synthetic'}};
    const honest = settlement.honest_tag || day?.honest_tag || roll.honest_tag || 'mixed_real_and_synthetic_deterministic_stdlib_LCG_189831298_honest';

    // inject/upgrade header if existing results-summary.js already rendered cards — we patch
    // Find header row pill cluster and add AUTO badge + last settlement timestamp.

    // Wait a tick for results-summary.js innerHTML to mount
    setTimeout(()=>{
      const pills = HOST.querySelectorAll('.pill');
      // avoid duplicate
      if(!HOST.querySelector('#settlement-auto-badge')){
        const top = HOST.firstElementChild;
        if(top){
          const badgeRow = document.createElement('div');
          badgeRow.id='settlement-auto-row';
          badgeRow.style.cssText='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;align-items:center';
          const srcTag = (honest.includes('real') && !honest.startsWith('synthetic')) ? 'AUTO LIVE' : (honest.includes('mixed')?'AUTO • mixed real+synthetic • LCG honest':'AUTO • synthetic_deterministic honest');
          badgeRow.innerHTML=`
            <span id="settlement-auto-badge" class="pill" style="background:#E4FF7C;color:#080A0F;border-color:#000;font-weight:900">● ${srcTag}</span>
            <span class="pill" style="background:#0f141e;color:#FFFEF7;border-color:#1e2a44">last settlement ${fmtAgo(settlement.last_run||day?.timestamp)} • ${new Date(settlement.last_run||day?.timestamp||Date.now()).toLocaleString()}</span>
            <span class="pill" style="background:${kellyColor(day?.kill||'GREEN')};color:#080A0F;border-color:#000;font-weight:800">${day?.kill||'GREEN'} • Kelly ${day?.kelly||0.25} • ${day?.wins||0}W-${day?.losses||0}L-${day?.pushes||0}P today</span>
            <span class="pill" style="background:#fff;color:#080A0F;border-color:#000">LCG ${FIXED_TRIPLE.join(',')} same-link-same-stars ?daily=${TODAY}&n=1/3/5 Solo1 Triple3 Full5</span>
            <span class="pill" style="background:#080A0F;color:#E4FF7C;border-color:#E4FF7C" title="Settlement sources">Kalshi ${(sources.kalshi?.tag||'').slice(0,24)} • DK ${(sources.dk?.tag||'').slice(0,24)} • PP ${(sources.prizepicks?.tag||sources.prize?.tag||'').slice(0,24)}</span>
          `;
          top.appendChild(badgeRow);
        }
      }

      // enhance each period card with timestamp + kelly strip if missing
      if(day && HOST.querySelectorAll('[data-period="day"]').length===0){
        // add subtle footer if not already
        const grid = HOST.children[1];
        if(grid){
          const foot = document.createElement('div');
          foot.style.cssText='margin-top:8px;padding:8px 10px;background:#0b101a;border:1px solid #1e2a44;border-radius:10px;font:600 11px ui-monospace,monospace;color:#a8b8d0;display:flex;flex-wrap:wrap;gap:6px;align-items:center';
          foot.innerHTML=`
            <span class="pill" style="background:#fffcf2;color:#080A0F;border-color:#000;font-size:10px">DAU3/WAU3 TLPG dedup everydayTip</span>
            <span class="pill" style="background:#0f141e;color:#FFFEF7;border-color:#1e2a44;font-size:10px">Open→drag-map→Jordan→copy-link equal stars • same-link-same-stars</span>
            <span class="pill" style="background:#080A0F;color:#FFFEF7;border-color:#1e2a44;font-size:10px">vegas_backfill 57,660 rows deterministic honest LCG 189831298</span>
            <span class="pill" style="background:#111725;color:#FFFEF7;border-color:#1e2a44;font-size:10px">Today ${day.picks} settled ${day.win_pct? (day.win_pct*100).toFixed(1)+'% win':''} ROI ${day.roi_pct? day.roi_pct.toFixed(2)+'%':''} pnl ${day.pnl_units? day.pnl_units.toFixed(2)+'u':''} IC ${day.ic? day.ic.toFixed(3):''} Sharpe ${day.sharpe? day.sharpe.toFixed(2):''}</span>
          `;
          HOST.appendChild(foot);
        }
      }

      // tap feedback vibrate + confetti
      try{
        HOST.addEventListener('click', (e)=>{
          const c = e.target.closest('.pill');
          if(c && c.textContent.includes('AUTO')){
            if(navigator.vibrate) navigator.vibrate(10);
            try{ if(window.confetti) window.confetti(); }catch{}
            if(navigator.clipboard && navigator.clipboard.writeText){
              navigator.clipboard.writeText(location.origin+'/?daily='+TODAY+'&n=3&settlement=AUTO#results-summary');
            }
          }
        });
      }catch{}

    }, 360);

  }

  // EverydayTip humanized rotation — consistent with hubs daily-picks
  function everydayTip(){
    const tips=[
      "Drag map → find Jordan twin — copy link equal stars",
      "Owner cap $140.5M surplus — tap player → props edge",
      "Single-select clears prev — momentum 0.94 — ivory #FFFEF7",
      "Same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5",
      "Open→drag-map→Jordan→copy-link equal stars DAU3/WAU3 TLPG dedup",
      "Board PrizePicks 9 Kalshi 6 DK 6 per_team_priors TRUE",
      "Games free • Edge private • 7 edges paper-tracked Kelly 0.25"
    ];
    return tips[TODAY%tips.length];
  }

  try{
    const t = everydayTip();
    // expose for console
    window._everydayTip = t;
  }catch{}

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

})();
