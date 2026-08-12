import { cors, auth, send } from '../_lib/auth.js'
export default async function handler(req,res){
  if(cors(req,res)) return
  let authed=false; try{ const a=auth(req,{requireKey:false}); authed=a.authed }catch{}
  // This endpoint can be anon for free proof, but trading actions require key
  const requireKey = (req.query.trading||'')!=='';
  try{
    if(requireKey) auth(req,{requireKey:true, scope:'write'})
  }catch(e){ return send(res,e.status||401,{ok:false,error:'trading proof requires write-scoped API key'}) }
  send(res,200,{
    ok:true,
    free:true,
    knowledge:{
      hoops:{ MAE:0.2085, R2:0.8934, vs_naive:'~0.45-0.6', embeds:'12,966×64-d 3.3M f32 L2' },
      equities:{ CQS:0.7017, baseline:0.605, PASS:true, sector_acc:0.957, FYs:4831 },
      towers:'17 hoops / 20 equities / 11 pitch / 8 gridiron = real concepts not vanity'
    },
    edge:{
      IC:'0.007 >0 bias 0.0 isotonic',
      purity:0.68, recall_at_10:1.0,
      human_vs_model:'free daily play = instant strength/weakness signal, no fake metrics',
      crowd_baseline:'If top-decile <53% vs crowd → auto shrink size'
    },
    money:{
      funnel:'games (free) → Kalshi NBA/NFL/earnings 0.25 Kelly 1% max/play 3 concurrent → equity directional paper → tiny 0DTE spreads ONLY after 60d OOS IC>0.03 Sharpe>1.2 win>55% DD<12%',
      risk:{ kill_switch:'1% day loss → halt', bankroll:'family ops ≠ trading', options:'long spreads only, no naked', advice:'not financial advice' },
      cost:'Vercel hobby free + Cloudflare free + PostHog free = $0/mo, no headcount until edge covers 3mo'
    },
    authed,
    timestamp:new Date().toISOString()
  })
}
