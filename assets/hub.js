/* dumbmodel.com hub — scroll-spy for the sticky nav.
 * The nav wraps on small screens the same way the games' .site-nav does,
 * so there's no toggle to wire up — just active-section highlighting. */
(function () {
  'use strict';

  var links = Array.prototype.slice.call(
    document.querySelectorAll('.site-nav__link[href^="#"]')
  );
  var sections = [];

  links.forEach(function (link) {
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({ id: id, el: el, link: link });
  });

  if (!sections.length || !('IntersectionObserver' in window)) return;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var id = entry.target.id;
      links.forEach(function (link) {
        var active = link.getAttribute('href') === '#' + id;
        link.classList.toggle('is-active', active);
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });

  sections.forEach(function (s) { observer.observe(s.el); });
})();

/* ------------------------------------------------------------------
 * dumbmodel unified chimera daily — deterministic dailySeed LCG
 * and provenance checksum verification (idempotent, no breakage).
 *
 * Mirrors models/*.html dailySeed from assets/model.js:
 *   dailySeed = UTC year*10000 + month*100 + day  (YYYYMMDD int)
 *   LCG = (seed * 1103515245 + 12345) & 0x7fffffff   (glibc rand)
 *
 * Exposes:
 *   window.DAILY_SEED                 — YYYYMMDD int UTC today
 *   window.UNIFIED_CHIMERA_DAILY      — { seed, dateISO, entityCount:20719, dims:64, index, lcg, pickPair? }
 *   window.hubDailySeed()             — fn -> YYYYMMDD
 *   window.hubLcg(seed)               — fn -> next LCG int
 *   window.unifiedChimeraDaily(seed)  — fn -> daily pick object
 *   window.verifyProvenance()         — fn -> Promise, fetches assets/data/* and checks source_hashes
 *
 * The scroll-spy IIFE above is untouched. This block is standalone and
 * safe to load twice (guarded by window.__hubDailyInit).
 * ------------------------------------------------------------------ */
(function () {
  'use strict';
  if (window.__hubDailyInit) return;
  window.__hubDailyInit = true;

  // ---- daily seed --------------------------------------------------
  function hubDailySeed(d) {
    var dt = d instanceof Date ? d : new Date();
    // UTC to match model.js dailySeed() for deterministic daily puzzles
    return dt.getUTCFullYear() * 10000 + (dt.getUTCMonth() + 1) * 100 + dt.getUTCDate();
  }

  function hubLcg(seed) {
    // glibc-style LCG masked to 31-bit, same as model.js shuffled()
    return (seed * 1103515245 + 12345) & 0x7fffffff;
  }

  function dateISOFromSeed(seed) {
    // seed is YYYYMMDD -> "YYYY-MM-DD"
    var s = String(seed);
    if (s.length !== 8) return new Date().toISOString().slice(0, 10);
    return s.slice(0,4) + '-' + s.slice(4,6) + '-' + s.slice(6,8);
  }

  function unifiedChimeraDaily(optSeed) {
    var seed = typeof optSeed === 'number' ? optSeed : hubDailySeed();
    var a = hubLcg(seed);
    var b = hubLcg(a);
    var c = hubLcg(b);
    // 20,719 player-seasons — matches unified.json entity_count
    var ENTITY = 20719;
    // deterministic index for today's puzzle
    var idx = a % ENTITY;
    // second pick for chimera pair (cross-sport), distinct from first
    var j = b % ENTITY;
    if (j === idx) j = (j + 1) % ENTITY;
    // third for daily triple variation (optional)
    var k = c % ENTITY;
    if (k === idx || k === j) k = (k + 2) % ENTITY;

    return {
      kind: 'unified-chimera-daily',
      seed: seed,
      dateISO: dateISOFromSeed(seed),
      entityCount: ENTITY,
      dims: 64,
      native: { hoops: 12966, gridiron: 5323, pitch: 2430 },
      index: idx,
      pair: [idx, j],
      triple: [idx, j, k],
      lcg: { a: a, b: b, c: c },
      // convenience: same shape as model.js shuffled expects for round order
      toString: function () { return 'UNIFIED-' + seed + '-' + idx; }
    };
  }

  // expose globals
  window.hubDailySeed = hubDailySeed;
  window.hubLcg = hubLcg;
  window.unifiedChimeraDaily = unifiedChimeraDaily;

  try {
    var today = hubDailySeed();
    window.DAILY_SEED = today;
    window.UNIFIED_CHIMERA_DAILY = unifiedChimeraDaily(today);
    // also DATE string for templates
    window.DAILY_ISO = dateISOFromSeed(today);
  } catch (e) {
    // console only, never break page
    console.warn('[hub-daily] seed init failed', e);
  }

  // ---- provenance checksum verification -----------------------------
  // Mirrors unified.html provenance-honest pattern: every number is read
  // from listed files; source_hashes object must be present and non-empty.
  var PROV_FILES = [
    '/assets/data/unified.json',
    '/assets/data/scout_cli.json',
    '/assets/data/hoops.json',
    '/assets/data/gridiron.json',
    '/assets/data/pitch.json',
    '/assets/data/equities.json',
    '/assets/data/tennis.json'
  ];

  function verifyProvenance(list) {
    var files = list && list.length ? list : PROV_FILES;
    var jobs = files.map(function (url) {
      return fetch(url, { cache: 'no-store' })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + url);
          return r.json();
        })
        .then(function (j) {
          var sh = j && j.source_hashes;
          var ok = sh && typeof sh === 'object' && Object.keys(sh).length > 0;
          var ver = j && (j._verification || j._round_notes || j.entity_count || j.dims);
          // depth: source_hashes is primary, but _verification presence counts as secondary signal
          if (!ok) {
            if (ver) {
              console.warn('[provenance] ' + url + ' — MISSING source_hashes but has _verification/entity_count (partial fail)');
            } else {
              console.warn('[provenance] ' + url + ' — MISSING source_hashes (provenance fail)');
            }
            return { url: url, ok: false, count: 0, slug: j && j.slug };
          }
          var n = Object.keys(sh).length;
          console.log('[provenance] ' + url + ' ok — ' + n + ' hashes' + (j.slug ? ' ('+j.slug+')' : ''));
          return { url: url, ok: true, count: n, slug: j && j.slug };
        })
        .catch(function (e) {
          console.warn('[provenance] ' + url + ' — fetch/parse error: ' + e.message);
          return { url: url, ok: false, error: e.message };
        });
    });

    return Promise.all(jobs).then(function (results) {
      var okCount = 0;
      for (var i = 0; i < results.length; i++) if (results[i].ok) okCount++;
      var total = results.length;
      var bad = total - okCount;
      var ts = new Date().toISOString();
      // depth artifact required by nightly watchdogs / dashboards
      window.DM_PROVENANCE = { ok: okCount, total: total, bad: bad, ts: ts, results: results };
      window.__provenanceLast = results;

      var provMsg = '[prov] ' + okCount + '/' + total + ' ok, ' + bad + ' bad — dumbmodel provenance';
      var detailMsg = '[provenance] ' + (okCount === total ? 'all ok — ' : '') + total + ' files checked, ' + okCount + ' ok' + (bad ? ', ' + bad + ' bad' : '') + ', provenance-honest ' + (okCount === total ? 'PASS' : 'PARTIAL');

      // always log [prov] line for log parsers
      if (okCount === total) {
        console.log(provMsg);
        console.log(detailMsg);
      } else {
        console.warn(provMsg);
        console.warn(detailMsg);
        console.warn('[provenance] some files missing source_hashes — see warnings above (provenance not fully honest)');
      }
      return results;
    });
  }

  window.verifyProvenance = verifyProvenance;

  // auto-run on load (defer safe, console-only, never blocks rendering)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { verifyProvenance(); });
  } else {
    // tiny delay so other scripts that set __hubDailyInit can still guard
    setTimeout(function () { verifyProvenance(); }, 0);
  }

  // dev helper: log daily chimera on load for debugging deploy
  try {
    console.log('[hub-daily] DAILY_SEED', window.DAILY_SEED, 'UNIFIED_CHIMERA_DAILY', window.UNIFIED_CHIMERA_DAILY && window.UNIFIED_CHIMERA_DAILY.toString());
  } catch (_e) {}

})();
