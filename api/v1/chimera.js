import { cors, auth, send } from '../_lib/auth.js'
import { dailySeedFromDate, yyyymmddUTC, lcg } from '../_lib/lcg.js'
export default async function handler(req,res){
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){return send(res,e.status||401,{ok:false,error:e.message})}
  const yyyymmdd=(req.query.daily||'').toString().replace(/-/g,'')||String(yyyymmddUTC())
  try{
    const { a }=dailySeedFromDate(yyyymmdd)
    const total=20719
    const idx=a%total
    const chimeraData={
      yyyymmdd:parseInt(yyyymmdd,10),
      entityCount:total,
      dims:64,
      dailySeed:a,
      idx,
      pair:[idx,(idx+10420)%total],
      triple:[idx,(idx+10420)%total,(idx+4582)%total],
      five:[0,1,2,3,4].map(i=>(idx+i*2080)%total),
      provenance:{hoops:12966, gridiron:5323, pitch:2430, total},
      native:{hoops64:'64-d', gridiron32:'32-d', pitch24:'24-d', folded:'64-d'},
      loss:'CORAL λ0.3→0.5 Δ+0.0593 sport leak honest floor 0.64, GRL + SupCon τ0.07 + VICReg',
      free:'joint embedding live PWA v67 offline 13kB shell, shared-map.js reusable LOD'
    }
    return send(res,200,{ok:true, ...chimeraData})
  }catch(e){ return send(res,400,{ok:false,error:e.message}) }
}
