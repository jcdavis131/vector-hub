import { cors, auth, send, handleRateLimitError } from '../_lib/auth.js'
import { lcg, yyyymmddUTC, dailySeedFromDate } from '../_lib/lcg.js'

export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  const qdaily = (req.query.daily||req.query.date||'').toString().replace(/-/g,'')
  const game = (req.query.game||'hoops').toString()
  const n = parseInt((req.query.n||'1').toString(),10)||1
  const yyyymmdd = qdaily || String(yyyymmddUTC())
  try{
    const { a,b,c } = dailySeedFromDate(yyyymmdd)
    const total = 20719
    const idx = a % total
    // LCG chain triple — same as hub.js unifiedChimeraDaily: b=lcg(a), c=lcg(b)
    let j = b % total
    let k = c % total
    if (j === idx) j = (j + 1) % total
    if (k === idx || k === j) k = (k + 2) % total
    const d = lcg(c), e = lcg(d)
    const pair = [idx, j]
    const triple = [idx, j, k] // 20260812→[3970,14390,4582] validated glibc
    const five = [idx, j, k, d % total, e % total]
    const picks = n===1?[idx]: n===3?triple : n===5?five : Array.from({length:Math.min(n,5)},(_,i)=>[idx,j,k,d%total,e%total][i]|| (lcg(e+i)*1%total))
    return send(res,200,{
      ok:true,
      free:true,
      yyyymmdd: parseInt(yyyymmdd,10),
      dailySeed: a,
      lcg: 'seed*1103515245+12345 & 0x7fffffff glibc Math.imul',
      idx,
      idx3970_check: a===1233799701 && idx===3970 ? 'PASS 20260812→1233799701 idx3970' : (parseInt(yyyymmdd,10)===20260812 ? 'FAIL' : 'n/a'),
      total,
      same_link_same_stars: `?daily=${yyyymmdd}&n=${n}`,
      game,
      picks,
      pair,
      triple,
      five,
      fivePack: five,
      chimera:{ triple, five, daily:true, entityCount:total, dims:64 },
      dailySeedCheck:{ yyyymmdd: parseInt(yyyymmdd,10), expect_a_for_20260812:1233799701, got_a:a, expect_idx_3970:3970, got_idx:idx, pass: parseInt(yyyymmdd,10)!==20260812 || (a===1233799701 && idx===3970) },
      window: { DAILY_SEED: parseInt(yyyymmdd,10), UNIFIED_CHIMERA_DAILY: {seed:parseInt(yyyymmdd,10), entityCount:total, dims:64, index:idx, lcg:{a,b,c}, pair, triple, toString:`UNIFIED-${yyyymmdd}-${idx}`} },
      proof:'If model cant win free daily, wont beat market — deterministic, no server dice — PWA v67 offline 13k shell void #080A0F',
      knowledge:{ MAE:0.2085, R2:0.8934 },
      nextMidnightUTC: new Date(new Date().toISOString().slice(0,10)+'T23:59:59Z').toISOString()
    })
  }catch(e){
    return send(res,400,{ok:false,error:e.message, example:'?daily=20260812&game=hoops&n=1'})
  }
}
