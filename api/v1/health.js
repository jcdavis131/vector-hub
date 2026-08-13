import { cors, send, handleRateLimitError } from '../_lib/auth.js'
import { auth } from '../_lib/auth.js'
export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res, e.status||401, {ok:false,error:e.message})
  }
  send(res,200,{
    ok:true,
    name:'dumbmodel.com',
    version:'v67-free-knowledge-edge-money',
    free:true,
    dailySeed:'LCG 1103515245 & 0x7fffffff — 20260812→1233799701 idx3970 triple [3970,14390,4582] five validates hub.js = api/_lib/lcg.js = Python',
    LCG:{ seed:20260812, a:1233799701, idx:3970, total:20719, triple:[3970,14390,4582], five:[3970,14390,4582,13307,8695] },
    games:['hoops','gridiron','pitch','equities','unified'],
    time:new Date().toISOString(),
    free_detail:'everything free for users — profitability via own calibrated edge, not charging users',
    knowledge:{ hoops:{MAE:0.2085,R2:0.8934}, equities:{CQS:0.7017}, towers:'17/20/11/8' },
    edge:{ IC:0.007, purity:0.68 },
    money:{ kill_switch:'1% day loss → halt', max_per_play:'1%', concurrent:3 },
    provenance:'7/7/0 honest',
    PWA:{ v67:true, shell:'CORE20 20 entries', offline:'13k void #080A0F', hit:'74k HIT offline shell', cache:'dumbmodel-v67-hub-5games-chimera' },
    endpoints:['/api/health','/api/v1/health','/api/v1/free','/api/v1/roster','/api/v1/models','/api/v1/daily','/api/v1/provenance','/api/v1/vectors','/api/v1/search','/api/v1/chimera','/api/v1/proof']
  })
}
