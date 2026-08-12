import { cors, send } from '../_lib/auth.js'
export default async function handler(req,res){
  if(cors(req,res)) return
  send(res,200,{
    ok:true,
    name:'dumbmodel.com',
    version:'v67-free-knowledge-edge-money',
    dailySeed:'LCG 1103515245 & 0x7fffffff',
    games:['hoops','gridiron','pitch','equities','unified'],
    time:new Date().toISOString(),
    free:'everything free for users — profitability via own calibrated edge, not charging users',
    endpoints:['/api/health','/api/v1/health','/api/v1/models','/api/v1/daily','/api/v1/provenance','/api/v1/vectors','/api/v1/search','/api/v1/chimera','/api/v1/proof']
  })
}
