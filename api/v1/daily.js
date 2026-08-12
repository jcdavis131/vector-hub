import { cors, auth, send } from '../_lib/auth.js'
import { lcg, yyyymmddUTC, dailySeedFromDate } from '../_lib/lcg.js'

export default async function handler(req,res){
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){ return send(res,e.status||401,{ok:false,error:e.message}) }
  const qdaily = (req.query.daily||req.query.date||'').toString().replace(/-/g,'')
  const game = (req.query.game||'hoops').toString()
  const n = parseInt((req.query.n||'1').toString(),10)||1
  const yyyymmdd = qdaily || String(yyyymmddUTC())
  try{
    const { a,b,c } = dailySeedFromDate(yyyymmdd)
    const total = 20719
    const idx = a % total
    const pair = [idx, (idx+10420)%total]
    const triple = [idx, (idx+10420)%total, (idx+4582)%total]
    const five = [0,1,2,3,4].map(i=> (idx + i*2080)%total)
    const picks = n===1?[idx]: n===3?triple : n===5?five : Array.from({length:Math.min(n,5)},(_,i)=>(idx+i*2080)%total)
    return send(res,200,{
      ok:true,
      free:true,
      yyyymmdd: parseInt(yyyymmdd,10),
      dailySeed: a,
      lcg: 'seed*1103515245+12345 & 0x7fffffff',
      idx,
      total,
      same_link_same_stars: `?daily=${yyyymmdd}&n=${n}`,
      game,
      picks,
      pair,
      triple,
      five,
      fivePack: five,
      window: { DAILY_SEED: a, UNIFIED_CHIMERA_DAILY: {seed:a, entityCount:total, dims:64, idx, pair, triple}},
      proof:'If model cant win free daily, wont beat market — deterministic, no server dice',
      nextMidnightUTC: new Date(new Date().toISOString().slice(0,10)+'T23:59:59Z').toISOString()
    })
  }catch(e){
    return send(res,400,{ok:false,error:e.message, example:'?daily=20260812&game=hoops&n=1'})
  }
}
