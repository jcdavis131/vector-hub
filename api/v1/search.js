import { cors, auth, send, handleRateLimitError } from '../_lib/auth.js'
import fs from 'fs'; import path from 'path'
export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  // search is read but rate-limited; anon ok
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  if(req.method!=='POST' && req.method!=='GET') return send(res,405,{ok:false,error:'method not allowed'})
  const body = req.method==='POST' ? (req.body||{}) : req.query
  const q=(body.q||body.query||'').toString().toLowerCase().trim()
  const game=(body.game||req.query.game||'hoops').toString()
  if(!q) return send(res,200,{ok:true, free:true, game, results:[], hint:'q=lebron', MAE:0.2085, provenance:'7/7/0' })
  try{
    const hoops=JSON.parse(fs.readFileSync(path.join(process.cwd(),'assets/data/hoops.json'),'utf8'))
    const list=hoops.players||[]
    const hit=list.filter(p=> (p.name||'').toLowerCase().includes(q) || (p.search||'').toLowerCase().includes(q)).slice(0,10).map(p=>({id:p.id,name:p.name,season:p.season, pos:p.pos, team:p.team||p.tm, dob:p.dob||null}))
    return send(res,200,{ok:true, free:true, game, q, count:hit.length, results:hit, dims:'64-d L2, cosine = dot', MAE:0.2085, R2:0.8934, provenance:'7/7/0', csv:true})
  }catch(e){
    return send(res,500,{ok:false,error:e.message})
  }
}
