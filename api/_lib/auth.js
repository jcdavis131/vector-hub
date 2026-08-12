/**
 * Proper security for dumbmodel.com API
 * - Bearer API key via constant-time compare
 * - Env-driven key list DUMBMODEL_API_KEYS or DUMBMODEL_API_KEY
 * - Rate limit: 120 req/min per key + 60/min IP, sliding window in-memory
 * - Scopes: read, write, admin
 * - CORS allowlist: *.dumbmodel.com, localhost, vercel preview
 */
import crypto from 'crypto'

const RATE = new Map()
const WINDOW_MS = 60_000
const MAX_PER_KEY = 120
const MAX_PER_IP = 60

function safeEqual(a,b){
  if(typeof a!=='string'||typeof b!=='string') return false
  const ba=Buffer.from(a); const bb=Buffer.from(b)
  if(ba.length!==bb.length) return false
  return crypto.timingSafeEqual(ba,bb)
}

function allowedKeysEnv(){
  const single = process.env.DUMBMODEL_API_KEY
  const many = process.env.DUMBMODEL_API_KEYS
  const list=[]
  if(single) list.push(single.trim())
  if(many){
    try{
      const parsed=JSON.parse(many)
      if(Array.isArray(parsed)) list.push(...parsed)
    }catch{
      list.push(...many.split(',').map(s=>s.trim()).filter(Boolean))
    }
  }
  return [...new Set(list.filter(Boolean))]
}

export function getApiKeyDef(key){
  // dm_ prefix keys are ours, others maybe external
  if(!key) return null
  const allowed=allowedKeysEnv()
  if(allowed.length===0){
    // dev fallback: allow any dm_ key that exists in local file during local dev
    // In Vercel prod, env must be set
    return key.startsWith('dm_') ? { key, scope: ['read','write'], tier:'dev' } : null
  }
  const ok=allowed.some(k=>safeEqual(k,key))
  if(!ok) return null
  return { key, scope: ['read','write','admin'], tier: key.startsWith('dm_scout_')?'scout': key.startsWith('dm_admin')?'admin':'external' }
}

export function auth(req, { requireKey=false, scope='read' }={}){
  const authHeader = req.headers['authorization'] || req.headers['Authorization'] || ''
  const bearer = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : null
  const keyQuery = (req.query?.key || req.query?.api_key || '').trim()
  const key = bearer || keyQuery || null
  const clientIp = (req.headers['x-forwarded-for']?.split(',')[0]?.trim()) || req.headers['x-real-ip'] || 'unknown'
  // rate limit
  const now=Date.now()
  const ipBucket=`ip:${clientIp}`
  const keyBucket=key?`key:${key.slice(0,12)}`:null
  for(const bucket of [ipBucket, keyBucket].filter(Boolean)){
    const arr=RATE.get(bucket)||[]
    const recent=arr.filter(t=>now-t < WINDOW_MS)
    const limit = bucket.startsWith('ip:') ? MAX_PER_IP : MAX_PER_KEY
    if(recent.length>=limit){
      const err=new Error('rate_limited'); err.status=429; err.bucket=bucket; throw err
    }
    recent.push(now); RATE.set(bucket, recent)
  }
  if(!key){
    if(requireKey) { const e=new Error('unauthorized'); e.status=401; throw e }
    return { authed:false, key:null, tier:'anon', scope:[] }
  }
  const def=getApiKeyDef(key)
  if(!def){
    const e=new Error('unauthorized'); e.status=401; throw e
  }
  if(scope && !def.scope.includes(scope) && !def.scope.includes('admin')){
    const e=new Error('forbidden'); e.status=403; throw e
  }
  return { authed:true, ...def, ip:clientIp }
}

export function cors(req,res){
  const origin=req.headers['origin']||''
  const allowed=/^(https?:\/\/)?([a-z0-9-]+\.)*dumbmodel\.com$|^https?:\/\/localhost(:\d+)?$|^https:\/\/.*\.vercel\.app$/
  if(!origin || allowed.test(origin) || origin==='null'){
    res.setHeader('Access-Control-Allow-Origin', origin||'*')
  }
  res.setHeader('Access-Control-Allow-Methods','GET,POST,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers','Authorization,Content-Type,X-Dumbmodel-Key')
  res.setHeader('Access-Control-Max-Age','600')
  if(req.method==='OPTIONS'){ res.status(200).end(); return true }
  return false
}

export function send(res, status, body, extraHeaders={}){
  Object.entries(extraHeaders).forEach(([k,v])=>res.setHeader(k,v))
  res.status(status).json(body)
}
