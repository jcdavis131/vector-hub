import { cors, auth, send } from '../_lib/auth.js'
import fs from 'fs'; import path from 'path'
export default async function handler(req,res){
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){return send(res,e.status||401,{ok:false,error:e.message})}
  const game=(req.query.game||'hoops').toString()
  const id=parseInt((req.query.id||'0').toString(),10)
  const lite=(req.query.lite||'true')!=='false'
  const mapFile = game==='unified' ? 'assets/vectors_map_lite.json' : `assets/data/${game}.json`
  try{
    const full=JSON.parse(fs.readFileSync(path.join(process.cwd(),'assets/data/hoops.json'),'utf8'))
    // hoops is different shape; for vector endpoint we return meta + similarity hint
    if(game==='hoops' && full){
      const players=full.players||[]
      const p=players[id]||players[id%players.length]
      return send(res,200,{ok:true, game, id, id_mod:id%players.length, dims:64, l2:true, cosine:'dot of L2 unit', player:p? {name:p.name||p.id, season:p.season}:null, proof:'masked cat([x·m,m]) 17 towers → 64-d'})
    }
    return send(res,200,{ok:true, game, note:'lite map uses shared-map.js LOD 4000 mobile 8000 desktop DPR1 fillRect', entity_count: full?.entity_count||12966, sample_id:id})
  }catch(e){
    return send(res,500,{ok:false,error:e.message})
  }
}
