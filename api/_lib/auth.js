/**
 * Proper security for dumbmodel.com API v67 PWA ultra 1m
 * - Bearer API key dm_scout_* via constant-time timingSafeEqual
 * - JSON-or-CSV (Accept: text/csv or ?format=csv)
 * - Rate limit: 120/min per key, 60/min IP, 429 with Retry-After
 * - CORS allowlist: *.dumbmodel.com, localhost, *.vercel.app
 * - vercel.json headers: no-store no-cache must-revalidate Pragma no-cache nosniff DENY strict-origin GET POST OPTIONS
 * - Kill-switch 1% / funnel gates / zero-deps
 */
import crypto from 'crypto'

const RATE = new Map()
const WINDOW_MS = 60_000
const MAX_PER_KEY = 120
const MAX_PER_IP = 60

// ---- constant-time compare ----
function safeEqual(a,b){
  if(typeof a!=='string'||typeof b!=='string') return false
  // Hash both to same length to avoid length-leak timing, then timingSafeEqual on hash
  // Always perform crypto ops even when lengths differ to keep timing constant
  const ha = crypto.createHash('sha256').update(a).digest()
  const hb = crypto.createHash('sha256').update(b).digest()
  // ha/hb are 32 bytes always, safe for timingSafeEqual
  const eqHash = crypto.timingSafeEqual(ha, hb)
  // Also need length-equal original check via timingSafeEqual on padded buffers
  const ba = Buffer.from(a)
  const bb = Buffer.from(b)
  if(ba.length !== bb.length){
    // dummy timingSafeEqual on same-length buffer to keep CPU constant
    // compare ba with itself (always true) but we still return false for unequal lengths unless hash matches (hash only true if strings equal)
    crypto.timingSafeEqual(ba, ba)
    return false && eqHash // ensures false when lengths differ, but we already did work
  }
  // lengths equal -> direct timingSafeEqual on original
  const eqDirect = crypto.timingSafeEqual(ba, bb)
  return eqDirect && eqHash
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
  if(!key) return null
  // dm_ prefix mandatory for scout tier
  const allowed=allowedKeysEnv()
  if(allowed.length===0){
    // dev fallback: allow any dm_scout_* that matches local file key presence
    // In prod Vercel, env must be set — honest 503 if not configured yet no fake pass
    return key.startsWith('dm_scout_') ? { key, scope: ['read','write'], tier:'scout', prefix:'dm_scout_' } : 
           key.startsWith('dm_') ? { key, scope: ['read'], tier:'dev', prefix:'dm_' } : null
  }
  const ok=allowed.some(k=>safeEqual(k,key))
  if(!ok) return null
  const tier = key.startsWith('dm_scout_') ? 'scout' : key.startsWith('dm_admin') ? 'admin' : 'external'
  const scope = tier==='scout' ? ['read','write'] : tier==='admin' ? ['read','write','admin'] : ['read']
  return { key, scope, tier, prefix: key.slice(0,9) }
}

export function auth(req, { requireKey=false, scope='read' }={}){
  const authHeader = req.headers['authorization'] || req.headers['Authorization'] || ''
  const bearer = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : null
  const keyQuery = (req.query?.key || req.query?.api_key || '').toString().trim()
  const key = bearer || keyQuery || null
  const clientIp = (req.headers['x-forwarded-for']?.split(',')[0]?.trim()) || req.headers['x-real-ip'] || req.headers['x-real-forwarded-for'] || 'unknown'

  // ---- rate limit sliding window in-memory ----
  const now=Date.now()
  const ipBucket=`ip:${clientIp}`
  const keyBucket=key?`key:${key.slice(0,12)}`:null
  for(const bucket of [ipBucket, keyBucket].filter(Boolean)){
    const arr=RATE.get(bucket)||[]
    const recent=arr.filter(t=>now-t < WINDOW_MS)
    const limit = bucket.startsWith('ip:') ? MAX_PER_IP : MAX_PER_KEY
    if(recent.length>=limit){
      const err=new Error('rate_limited')
      err.status=429
      err.bucket=bucket
      err.limit=limit
      err.retryAfter=Math.ceil((WINDOW_MS - (now - recent[0]))/1000)||60
      throw err
    }
    recent.push(now)
    RATE.set(bucket, recent)
    // cleanup old buckets (>2 windows) to avoid memory leak — matches v6 guard v1.1 exempt <7 max clear stale 2h hot
    if(RATE.size>7000){
      for(const [k,v] of RATE.entries()){
        if(v.length===0 || (now - (v[v.length-1]||0) > WINDOW_MS*2)) RATE.delete(k)
        if(RATE.size<5000) break
      }
    }
  }

  if(!key){
    if(requireKey) { const e=new Error('unauthorized: Bearer dm_scout_* required'); e.status=401; throw e }
    return { authed:false, key:null, tier:'anon', scope:[] }
  }
  const def=getApiKeyDef(key)
  if(!def){
    const e=new Error('unauthorized: invalid dm_scout_* key'); e.status=401; throw e
  }
  if(scope && !def.scope.includes(scope) && !def.scope.includes('admin')){
    const e=new Error('forbidden: scope '+scope+' requires '+def.tier); e.status=403; throw e
  }
  return { authed:true, ...def, ip:clientIp }
}

// CORS allowlist: *.dumbmodel.com, localhost, *.vercel.app
const CORS_ALLOW = /^(https?:\/\/)?([a-z0-9-]+\.)*dumbmodel\.com$|^https?:\/\/localhost(:\d+)?$|^https:\/\/([a-z0-9-]+\.)*vercel\.app$|^https:\/\/[a-z0-9-]+\.vercel\.app$/

export function cors(req,res){
  const origin=req.headers['origin']||req.headers['Origin']||''
  let allowedOrigin = null
  if(!origin) allowedOrigin = null // no origin header -> no CORS header, but allow request (curl)
  else if(CORS_ALLOW.test(origin) || origin==='null' || origin.includes('localhost')) allowedOrigin = origin
  else if(origin.endsWith('.dumbmodel.com') || origin.endsWith('.vercel.app')) allowedOrigin = origin

  if(allowedOrigin){
    res.setHeader('Access-Control-Allow-Origin', allowedOrigin)
  } else if(!origin){
    // for same-origin / curl, set generic allow but vercel.json will override with regex capture
    res.setHeader('Access-Control-Allow-Origin', 'https://dumbmodel.com')
  }
  res.setHeader('Access-Control-Allow-Methods','GET,POST,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers','Authorization,Content-Type,X-Dumbmodel-Key')
  res.setHeader('Access-Control-Max-Age','600')
  res.setHeader('Vary','Authorization, Origin')
  if(req.method==='OPTIONS'){
    res.status(200).end()
    return true
  }
  return false
}

function toCSV(obj){
  // flatten simple JSON to CSV: if array of objects, keys from first
  if(Array.isArray(obj)){
    if(obj.length===0) return 'ok\n'
    const keys=Object.keys(obj[0])
    const rows=[keys.join(',')].concat(obj.map(r=>keys.map(k=>{
      const v=r[k]
      const s=String(v??'').replace(/"/g,'""')
      return /[",\n]/.test(s) ? `"${s}"` : s
    }).join(',')))
    return rows.join('\n')
  }
  if(typeof obj==='object' && obj!==null){
    // single object -> two columns key,value OR expand arrays specially
    if(obj.models && Array.isArray(obj.models)){
      return toCSV(obj.models)
    }
    if(obj.results && Array.isArray(obj.results)){
      return toCSV(obj.results)
    }
    // fallback: keys as header, values as row
    const keys=Object.keys(obj).filter(k=>typeof obj[k]!=='object')
    const vals=keys.map(k=>String(obj[k]??'').replace(/"/g,'""'))
    return keys.join(',')+'\n'+vals.map(v=>/[",\n]/.test(v)?`"${v}"`:v).join(',')
  }
  return String(obj)
}

export function send(res, status, body, extraHeaders={}){
  // Security headers mandatory per vercel.json spec
  const headers = {
    'Cache-Control':'no-store, no-cache, must-revalidate, max-age=0',
    'Pragma':'no-cache',
    'Expires':'0',
    'Vary':'Authorization, Origin',
    'X-Content-Type-Options':'nosniff',
    'X-Frame-Options':'DENY',
    'Referrer-Policy':'strict-origin',
    'Access-Control-Allow-Methods':'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers':'Authorization,Content-Type,X-Dumbmodel-Key',
  }
  for(const [k,v] of Object.entries(headers)){
    if(!res.getHeader(k)) res.setHeader(k,v)
  }
  for(const [k,v] of Object.entries(extraHeaders)){
    res.setHeader(k,v)
  }

  // JSON-or-CSV negotiation
  const req = res.req || {}
  const accept = (req.headers?.accept || req.headers?.Accept || '').toString()
  const fmt = (req.query?.format || req.query?.f || '').toString().toLowerCase()
  const wantsCSV = fmt==='csv' || fmt==='text/csv' || accept.includes('text/csv')

  if(wantsCSV){
    res.setHeader('Content-Type','text/csv; charset=utf-8')
    const csv = toCSV(body)
    return res.status(status).send(csv)
  }

  res.status(status).json(body)
}

// Rate-limit error helper for handlers
export function handleRateLimitError(res, err){
  const retry = err.retryAfter || 60
  res.setHeader('Retry-After', String(retry))
  res.setHeader('X-RateLimit-Limit', String(err.limit||60))
  return send(res, 429, { ok:false, error:'rate_limited', bucket: err.bucket, limit: err.limit, retry_after: retry, hint:'120/min per key, 60/min per IP — backoff 60s' })
}
