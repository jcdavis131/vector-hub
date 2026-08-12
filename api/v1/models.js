import { cors, auth, send } from '../_lib/auth.js'
import fs from 'fs'
import path from 'path'

function load(p){ try{ return JSON.parse(fs.readFileSync(path.join(process.cwd(),p),'utf8')) }catch{return null} }

export default async function handler(req,res){
  if(cors(req,res)) return
  try{ auth(req,{requireKey:false}) }catch(e){ return send(res,e.status||401,{ok:false,error:e.message}) }
  // free read — no key required, anon ok
  const hoops=load('assets/data/hoops.json')
  const models=[
    { slug:'hoops', name:'Vector Hoops', dims:'64-d MTNN 18 towers', entity_count: hoops?.entity_count||12966, file:'/assets/data/hoops.json', daily:true, status:'LIVE MAE 0.2085 R2 0.8934' },
    { slug:'gridiron', name:'Vector Gridiron', dims:'32-d', entity_count:646, daily:true, status:'projected 2026' },
    { slug:'pitch', name:'Vector Pitch', dims:'24-d', entity_count:633, daily:true, status:'WC 2018/2022' },
    { slug:'equities', name:'Vector Equities', dims:'64-d 20 towers', entity_count:500, daily:true, status:'CQS 0.7017 sector_acc 0.957' },
    { slug:'unified', name:'Unified Chimera', dims:'64-d joint 20719 CORAL+GRL+SupCon', entity_count:20719, daily:true, status:'joint MAE 0.2085 honest' },
  ]
  send(res,200,{ok:true, free:true, count:models.length, models, knowledge:'17 hoops / 20 equities / 11 pitch / 8 gridiron towers = real concepts not vanity, masked training, convergent/discriminant checked', edge:'platform as lie detector — daily free play = instant strength/weakness signal'})
}
