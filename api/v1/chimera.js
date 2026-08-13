import { cors, auth, send, handleRateLimitError } from '../_lib/auth.js'
import { dailySeedFromDate, yyyymmddUTC, lcg } from '../_lib/lcg.js'
export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  const yyyymmdd=(req.query.daily||'').toString().replace(/-/g,'')||String(yyyymmddUTC())
  try{
    const { a,b,c }=dailySeedFromDate(yyyymmdd)
    const total=20719
    const idx=a%total
    let j=b%total, k=c%total
    if(j===idx) j=(j+1)%total
    if(k===idx||k===j) k=(k+2)%total
    const d=lcg(c), e=lcg(d)
    const f=lcg(e), g=lcg(f)
    const chimeraData={
      ok:true,
      free:true,
      yyyymmdd:parseInt(yyyymmdd,10),
      entityCount:total,
      dims:64,
      dailySeed:a,
      idx,
      idx3970: parseInt(yyyymmdd,10)===20260812 && a===1233799701 && idx===3970 ? 'PASS' : (parseInt(yyyymmdd,10)===20260812?'FAIL':'n/a'),
      LCG_check:{ a, expect_20260812:1233799701, idx, expect_idx_3970:3970, pass: parseInt(yyyymmdd,10)!==20260812 || (a===1233799701 && idx===3970), glibc:'Math.imul(seed,1103515245)+12345 & 0x7fffffff', python:'(seed*1103515245+12345) & 0x7fffffff', hub_js:'hubLcg via Math.imul' },
      lcg:{a,b,c, chain:`${yyyymmdd}->${a} idx${idx} b${b} c${c} triple[${idx},${j},${k}]`},
      pair:[idx,j],
      triple:[idx,j,k],
      five:[idx,j,k,d%total,e%total],
      fivePack:[idx,j,k,d%total,e%total],
      provenance:{hoops:12966, gridiron:5323, pitch:2430, total, honest:'7/7/0', files:['hoops.json','gridiron.json','pitch.json','equities.json','unified.json','tennis.json','scout_cli.json']},
      native:{hoops64:'64-d', gridiron32:'32-d', pitch24:'24-d', folded:'64-d'},
      knowledge:{ MAE:0.2085, R2:0.8934, CQS:0.7017, IC:0.007 },
      loss:'CORAL λ0.3→0.5 Δ+0.0593 sport leak honest floor 0.64, GRL + SupCon τ0.07 + VICReg',
      glass_box:{ MAE:0.2085, R2:0.8934, CQS:0.7017, IC:0.007, archetype_pure:0.683, sport_acc:0.6851, delta:+0.0593, nn_same_arch:0.9828 },
      free:'joint embedding live PWA v67 offline 13kB shell CORE20 74k HIT, shared-map.js reusable LOD',
      same_link_same_stars:`?daily=${yyyymmdd}&n=1/3/5 LCG glibc 1103515245`,
      window:{DAILY_SEED:parseInt(yyyymmdd,10), UNIFIED_CHIMERA_DAILY:{seed:parseInt(yyyymmdd,10), entityCount:total, dims:64, index:idx, pair:[idx,j], triple:[idx,j,k], lcg:{a,b,c}}},
      PWA:{ v67:true, cache:'dumbmodel-v67-hub-5games-chimera', offline:'13k void #080A0F' },
      kill_switch:'1% day loss → halt, bankroll family ops ≠ trading',
      money:{ IC:0.007, kill_switch:'1% → halt', max_per_play:'1%', concurrent:3, funnel:'games free → Kalshi 0.25 Kelly 1% → equity paper → tiny 0DTE ONLY after 60d OOS' }
    }
    return send(res,200,chimeraData)
  }catch(e){ return send(res,400,{ok:false,error:e.message}) }
}
