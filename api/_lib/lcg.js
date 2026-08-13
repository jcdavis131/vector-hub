/**
 * Shared LCG — glibc rand() compat for dailySeed — T4 ultra 1m
 * Matches PWA v67: Math.imul(seed * 1103515245 + 12345) & 0x7fffffff
 * hub.js vs api/_lib/lcg.js vs Python (seed*1103515245+12345) & 0x7fffffff agree
 * 20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695]
 */
export function lcg(s) {
  return (Math.imul(s, 1103515245) + 12345) >>> 0 & 0x7fffffff
}
export function dailySeedFromDate(yyyymmdd) {
  const n = parseInt(String(yyyymmdd).replace(/-/g,''), 10)
  if (!Number.isFinite(n) || n < 19960101) throw new Error('invalid yyyymmdd: '+yyyymmdd)
  const a = lcg(n)
  const b = lcg(a)
  const c = lcg(b)
  // Validate 20260812 case per T4 spec
  if(n===20260812){
    if(a!==1233799701) console.warn('[lcg] EXPECT 20260812 a=1233799701 got '+a)
    const idx = a % 20719
    if(idx!==3970) console.warn('[lcg] EXPECT idx3970 got '+idx)
  }
  return { yyyymmdd: n, a, b, c }
}
export function yyyymmddUTC(d = new Date()) {
  return d.getUTCFullYear()*10000 + (d.getUTCMonth()+1)*100 + d.getUTCDate()
}
export function derivePack(seed, n, total=20719) {
  // LCG chain deterministic same as hub.js unifiedChimeraDaily: a=lcg(seed), b=lcg(a), c=lcg(b)
  // unifiedChimeraDaily: idx=a%total, j=b%total, k=c%total => triple [3970,14390,4582] for 20260812→1233799701
  const a = lcg(seed)
  const b = lcg(a)
  const c = lcg(b)
  const d = lcg(c)
  const e = lcg(d)
  const f = lcg(e)
  const idx = a % total
  const j = b % total
  const k = c % total
  // distinctness same as hub.js: if j==idx j+1, if k==idx||k==j k+2
  let jj = j, kk = k
  if (jj === idx) jj = (jj + 1) % total
  if (kk === idx || kk === jj) kk = (kk + 2) % total
  if (n===1) return [idx]
  if (n===3) return [idx, jj, kk] // [3970,14390,4582] for 20260812
  if (n===5) return [idx, jj, kk, d % total, e % total] // five
  // default n: extend chain
  const arr = [idx, jj, kk]
  let cur = e
  while (arr.length < n) {
    cur = lcg(cur)
    const v = cur % total
    if (!arr.includes(v)) arr.push(v)
    else arr.push((v+1)%total)
  }
  return arr.slice(0,n)
}

// Python par equivalent (for provenance comment):
// def lcg(s): return (s*1103515245+12345) & 0x7fffffff
// 20260812→1233799701 idx3970 triple [3970,14390,4582] five [3970,14390,4582,13307,8695] — glibc LCG

// Node quick self-test (when run via node):
// import { lcg } from './lcg.js'; console.assert(lcg(20260812)===1233799701); console.assert(lcg(20260812)%20719===3970)
