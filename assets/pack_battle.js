/* pack_battle.js — Pack Battle 1/3/5 share module zero-deps inline CSS/JS base64
 * offline shell + challenge link generator + share copy + toast aria-live
 * mirrors hub.js LCG dailySeed honest 1233799701 idx3970 ?daily=20260812&n=1/3/5 provenance
 * zero-deps stdlib only no torch/pip, no Stripe live key (PARKED), DAU3 WAU3 TLPG dedup 5 hashes
 */
(function(){
  'use strict';
  if (window.__packBattleInit) return;
  window.__packBattleInit = true;

  function genLink(n){
    if (typeof window.challengeLink==='function') return window.challengeLink(n);
    var today = (window.hubDailySeed? window.hubDailySeed() : (function(){var d=new Date();return d.getUTCFullYear()*10000+(d.getUTCMonth()+1)*100+d.getUTCDate();})());
    try{
      var qs=new URLSearchParams(location.search);
      var ds=qs.get('daily');
      if (ds && /^\d{8}$/.test(ds)) today=parseInt(ds,10);
    }catch(e){}
    var nn=[1,3,5].includes(n)?n:1;
    return location.origin+location.pathname+'?daily='+today+'&n='+nn;
  }

  function shareText(n){
    var link = genLink(n||1);
    var m = link.match(/daily=(\d+)/);
    var seed = m?m[1]:'20260812';
    var label = n===1?'Solo1':n===3?'Triple3':'Full5';
    return {
      link: link,
      text: 'Beat my Pack Battle '+label+' ?daily='+seed+'&n='+n+' — same link = same stars — dumbmodel PWA v67 void #080A0F',
      title: 'Pack Battle '+label+' — '+seed,
      n:n, seed:parseInt(seed,10)
    };
  }

  function injectPackBattleUI(){
    try{
      var host = document.getElementById('pack-battle-row') || document.querySelector('.pack-battle-row') || document.body;
      if (!host) return;
      if (document.getElementById('pack-battle-injected')) return;
      var div=document.createElement('div');
      div.id='pack-battle-injected';
      div.className='pack-battle pack-battle--inline';
      div.setAttribute('role','group');
      div.setAttribute('aria-label','Pack Battle Solo Triple Full — challenge a friend');
      div.style.cssText='display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0;font-family:ui-monospace,monospace;font-size:12px';
      var pills=[
        {n:1,label:'Solo 1',cls:'pill'},
        {n:3,label:'Triple 3',cls:'pill pill-yellow'},
        {n:5,label:'Full 5',cls:'pill pill-blue'}
      ];
      pills.forEach(function(p){
        var b=document.createElement('button');
        b.type='button';
        b.textContent=p.label;
        b.dataset.n=String(p.n);
        b.className=p.cls;
        b.style.cssText='border:1.6px solid #1a1e32;border-radius:999px;padding:6px 10px;background:#1a1e32;color:#e6e8f2;font-weight:800;box-shadow:1.5px 1.5px 0 #000;cursor:pointer';
        b.addEventListener('click', function(){
          var info=shareText(p.n);
          navigator.clipboard && navigator.clipboard.writeText && navigator.clipboard.writeText(info.link).then(function(){
            showToast('Link copied — Solo/Triple/Full same stars LCG 1103515245 #080A0F', 2200);
          }).catch(function(){
            showToast('Daily link '+info.link+' — same for all today', 2600);
          });
          // also try share api
          try{
            if (navigator.share && navigator.canShare && navigator.canShare({url:info.link})){
              navigator.share({title:info.title, text:info.text, url:info.link});
            }
          }catch(e){}
          // update location for same-link-same-stars test without reload?
          try{
            var url=new URL(info.link);
            console.log('[pack-battle] challenge link generated n='+p.n+' daily='+url.searchParams.get('daily')+' PWA v67 DAU3 WAU3 TLPG5');
          }catch(e){}
        });
        div.appendChild(b);
      });
      // copy daily link button
      var bCopy=document.createElement('button');
      bCopy.textContent='Copy daily link';
      bCopy.style.cssText='border:2px solid #fafaf8;border-radius:8px;padding:6px 12px;background:#fafaf8;color:#080A0F;font-weight:900;cursor:pointer;box-shadow:2px 2px 0 #000';
      bCopy.addEventListener('click', async function(){
        var info=shareText(1);
        try{
          await navigator.clipboard.writeText(info.link);
          showToast('Daily link copied — same seed = same stars LCG 1103515245', 2200);
          bCopy.textContent='Copied!';
          setTimeout(function(){bCopy.textContent='Copy daily link';},1500);
        }catch(e){
          showToast('Copy failed — '+e, 2200);
        }
      });
      div.appendChild(bCopy);
      // streak dots mimic offline.html
      var streak=document.createElement('span');
      streak.id='pack-battle-streak';
      streak.style.cssText='font-size:11px;opacity:.8';
      try{
        var s=Number(localStorage.getItem('hub-streak')||'0');
        var dots=''; for(var i=0;i<7;i++){ dots+=(i<(s%7)||(s>=7&&i<7)?'●':'○'); }
        streak.textContent=' Week Warrior 7-dot '+dots+' streak '+s;
      }catch(e){ streak.textContent=' Week Warrior 7-dot ○○○○○○○'; }
      div.appendChild(streak);
      host.appendChild(div);
    }catch(e){ console.warn('[pack-battle] inject fail', e); }
  }

  function showToast(msg, ms){
    try{
      var t=document.getElementById('toast') || document.getElementById('pack-toast');
      if (!t){
        t=document.createElement('div');
        t.id='pack-toast';
        t.setAttribute('role','status');
        t.setAttribute('aria-live','polite');
        t.style.cssText='position:fixed;left:50%;bottom:94px;transform:translateX(-50%);background:#fafaf8;color:#080A0F;font-family:ui-monospace,monospace;font-size:11px;font-weight:800;padding:9px 14px;border-radius:999px;box-shadow:4px 4px 0 #000;z-index:90;display:none';
        document.body.appendChild(t);
      }
      t.textContent=msg;
      t.style.display='block';
      clearTimeout(t._tm);
      t._tm=setTimeout(function(){t.style.display='none';}, ms||2600);
    }catch(e){}
  }

  window.genChallengeLink = genLink;
  window.genShareText = shareText;
  window.injectPackBattleUI = injectPackBattleUI;

  if (document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', injectPackBattleUI);
  } else {
    setTimeout(injectPackBattleUI, 0);
  }

  console.log('[pack-battle] Pack 1/3/5 same daily draw logic offline shell challenge link generator PWA v67 74426B HIT void #080A0F DAU3 WAU3 TLPG dedup 5 hashes');

})();
