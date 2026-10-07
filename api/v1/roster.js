import { cors, auth, send, handleRateLimitError } from '../_lib/auth.js'
import fs from 'fs'
import path from 'path'

function load(rel){
  try{ return JSON.parse(fs.readFileSync(path.join(process.cwd(), rel),'utf8')) }catch{ return null }
}

export default async function handler(req,res){
  res.req = req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res, e.status||401, {ok:false, error:e.message})
  }
  const game = (req.query.game||'hoops').toString()
  const format = (req.query.format||'').toString()
  try{
    const hoops = load('assets/data/hoops.json')
    const players = hoops?.players || []
    // roster is free, anon ok — paginated lite
    const limit = Math.min(parseInt((req.query.limit||'50').toString(),10)||50, 200)
    const offset = parseInt((req.query.offset||'0').toString(),10)||0
    const slice = players.slice(offset, offset+limit).map(p=>({
      id: p.id, name: p.name, season: p.season, team: p.team||p.tm,
      pos: p.pos, dob: p.dob||null,
      entity_idx: p.idx ?? p.id
    }))
    const data = {
      ok:true,
      free:true,
      game,
      entity_count: hoops?.entity_count||players.length||12966,
      dims:'64-d MTNN 18 towers masked cat([x·m,m]) 17 towers',
      MAE:0.2085, R2:0.8934, vs_naive:'~0.45-0.6',
      offset, limit, count:slice.length, total: players.length,
      roster: slice,
      daily:true, provenance:'7/7/0', same_link_same_stars:'?daily=YYYYMMDD&n=1',
      endpoint:'/api/v1/roster', format: format||'json'
    }
    return send(res,200,data)
  }catch(e){
    return send(res,500,{ok:false, error:e.message})
  }
}
