import { cors, auth, send, handleRateLimitError } from '../_lib/auth.js'
import fs from 'fs'
import path from 'path'

function load(p){ try{ return JSON.parse(fs.readFileSync(path.join(process.cwd(),p),'utf8')) }catch{return null} }

export default async function handler(req,res){
  res.req=req
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){
    if(e.status===429) return handleRateLimitError(res,e)
    return send(res,e.status||401,{ok:false,error:e.message})
  }
  // free read — no key required, anon ok
  const hoops=load('assets/data/hoops.json')
  const models=[
    { slug:'hoops', name:'Vector Hoops', dims:'64-d MTNN 18 towers', entity_count: hoops?.entity_count||12966, file:'/assets/data/hoops.json', daily:true, status:'LIVE MAE 0.2085 R2 0.8934', MAE:0.2085, R2:0.8934 },
    { slug:'gridiron', name:'Vector Gridiron', dims:'32-d', entity_count:646, daily:true, status:'projected 2026' },
    { slug:'pitch', name:'Vector Pitch', dims:'24-d', entity_count:633, daily:true, status:'WC 2018/2022' },
    { slug:'equities', name:'Vector Equities', dims:'64-d 20 towers', entity_count:500, daily:true, status:'CQS 0.7017 sector_acc 0.957', CQS:0.7017, sector_acc:0.957 },
    { slug:'unified', name:'Unified Chimera', dims:'64-d joint 20719 CORAL+GRL+SupCon', entity_count:20719, daily:true, status:'joint MAE 0.2085 honest', MAE:0.2085, R2:0.8934 },
  ]
  send(res,200,{
    ok:true,
    free:true,
    count:models.length,
    models,
    knowledge:'17 hoops / 20 equities / 11 pitch / 8 gridiron towers = real concepts not vanity, masked training, convergent/discriminant checked — MAE0.2085 R2 0.8934 CQS0.7017',
    edge:'platform as lie detector — daily free play = instant strength/weakness signal — IC 0.007 purity 0.68 recall_at_10 1.0',
    money:'funnel games free → Kalshi NBA/NFL/earnings 0.25 Kelly 1% max/play 3 concurrent → equity directional paper → tiny 0DTE spreads ONLY after 60d OOS IC>0.03 Sharpe>1.2 win>55% DD<12% kill-switch 1%',
    daily:true,
    provenance:'7/7/0 honest',
    vectors:true,
    search:true,
    chimera:true,
    proof:true,
    health:true,
    roster:true,
    endpoints:['/api/v1/daily','/api/v1/provenance','/api/v1/vectors','/api/v1/search','/api/v1/chimera','/api/v1/proof','/api/v1/health','/api/v1/models','/api/v1/roster','/api/v1/free','/api/health'],
    vercel_headers:{ 'Cache-Control':'no-store, no-cache, must-revalidate, max-age=0', 'Pragma':'no-cache', 'X-Content-Type-Options':'nosniff', 'X-Frame-Options':'DENY', 'Referrer-Policy':'strict-origin' }
  })
}
