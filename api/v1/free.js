import { cors, send, handleRateLimitError } from '../_lib/auth.js'
import { auth } from '../_lib/auth.js'

export default async function handler(req,res){
  res.req = req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  send(res,200,{
    ok:true,
    free:true,
    platform:'dumbmodel.com free for users — profitability via own calibrated edge, not charging users',
    version:'v67-free-knowledge-edge-money',
    games:['hoops','gridiron','pitch','equities','unified'],
    dailySeed:'LCG 1103515245 & 0x7fffffff — 20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695] same as hub.js',
    LCG:{ a:1233799701, idx:3970, triple:[3970,14390,4582], five:[3970,14390,4582,13307,8695], total:20719 },
    endpoints:[
      '/api/health',
      '/api/v1/health',
      '/api/v1/free',
      '/api/v1/roster',
      '/api/v1/models',
      '/api/v1/daily',
      '/api/v1/chimera',
      '/api/v1/provenance',
      '/api/v1/vectors',
      '/api/v1/search',
      '/api/v1/proof'
    ],
    knowledge:{ hoops:{MAE:0.2085,R2:0.8934}, equities:{CQS:0.7017, sector_acc:0.957}, towers:'17/20/11/8' },
    edge:{ IC:0.007, purity:0.68, recall_at_10:1.0 },
    money:{ kill_switch:'1% day loss → halt', bankroll:'family ops ≠ trading', funnel:'games free → Kalshi 0.25 Kelly 1% max/play 3 concurrent → equity paper → tiny 0DTE spreads ONLY after 60d OOS IC>0.03 Sharpe>1.2 win>55% DD<12%' },
    provenance:'7/7/0 honest verifyProvenance() auto DOMContentLoaded+8s idle',
    PWA:{ version:'v67', shell:'CORE20', offline:'13k void #080A0F', hit:'74k HIT', cache:'dumbmodel-v67-hub-5games-chimera' },
    vercel_headers:{ 'Cache-Control':'no-store, no-cache, must-revalidate', 'Pragma':'no-cache', 'X-Content-Type-Options':'nosniff', 'X-Frame-Options':'DENY', 'Referrer-Policy':'strict-origin', 'Allow':'GET,POST,OPTIONS' }
  })
}
