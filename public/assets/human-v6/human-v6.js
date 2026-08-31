window.DumbModel=window.DumbModel||{};
window.DumbModel.HumanV6={
  Selection:{
    init(){}, update(d){ if(d&&d.daily){ const dp=document.getElementById('daily-pill'); if(dp) dp.textContent='daily '+d.daily; } }, clear(){}, destroy(){}
  },
  Search:{init(){}, query(){}, destroy(){}},
  Peers:{init(){}, update(){}, destroy(){}},
  Evidence:{init(){const b=document.getElementById('evidence-toggle'); if(b) b.addEventListener('click',()=>{ const e=document.getElementById('evidence'); if(e) e.hidden=!e.hidden });}, open(){}, close(){}, destroy(){}},
  Share:{
    init(){
      const btn=document.getElementById('share-btn');
      if(btn) btn.addEventListener('click',async()=>{
        const url=location.href;
        try{ await navigator.clipboard.writeText(url); btn.textContent='Copied ✓'; setTimeout(()=>btn.textContent='Copy link',1200);}catch{ prompt('Copy link',url); }
      });
    }, copy(){}, destroy(){}
  }
};
