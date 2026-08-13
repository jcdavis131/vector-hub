import { cors, send, handleRateLimitError } from './_lib/auth.js'
export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  try{
    const { auth } = await import('./_lib/auth.js')
    auth(req,{requireKey:false})
  }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  send(res,200,{
    ok:true,
    name:'dumbmodel.com',
    version:'v67-free-knowledge-edge-money',
    free:true,
    dailySeed:'LCG 1103515245 & 0x7fffffff',
    games:['hoops','gridiron','pitch','equities','unified'],
    time:new Date().toISOString(),
    free_detail:'everything free for users — profitability via own calibrated edge, not charging users',
    endpoints:['/api/v1/health','/api/v1/free','/api/v1/roster','/api/v1/models','/api/v1/daily','/api/v1/provenance','/api/v1/vectors','/api/v1/search','/api/v1/chimera','/api/v1/proof']
  })
}
