/**
 * Shared LCG — glibc rand() compat for dailySeed
 * Matches PWA v67: Math.imul(seed * 1103515245 + 12345) & 0x7fffffff
 */
export function lcg(s) {
  return (Math.imul(s, 1103515245) + 12345) >>> 0 & 0x7fffffff
}
export function dailySeedFromDate(yyyymmdd) {
  const n = parseInt(String(yyyymmdd).replace(/-/g,''), 10)
  if (!Number.isFinite(n) || n < 19960101) throw new Error('invalid yyyymmdd')
  return { yyyymmdd: n, a: lcg(n), b: lcg(lcg(n)), c: lcg(lcg(lcg(n))) }
}
export function yyyymmddUTC(d = new Date()) {
  return d.getUTCFullYear()*10000 + (d.getUTCMonth()+1)*100 + d.getUTCDate()
}
export function derivePack(seed, n, total=20719) {
  const idx = seed % total
  // pair [idx, (idx+10420)%total] typical chimera, triple adds +4582 offset
  if (n===1) return [idx]
  if (n===3) return [idx, (idx+10420)%total, 3].slice(0,2).concat([(idx+4582)%total]) // keep deterministic [3970,14390,4582] example
  if (n===5) return [(idx)%total,(idx+2080)%total,(idx+4160)%total,(idx+6240)%total,(idx+8320)%total]
  // default n
  return Array.from({length:n}, (_,i)=> (idx + i*2080)%total)
}
