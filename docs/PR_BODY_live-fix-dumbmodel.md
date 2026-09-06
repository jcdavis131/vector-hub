# weekend/live-fix-dumbmodel

**What and why.** Fixes six live-fetch/honesty defects on dumbmodel.com identified by the
L1 audit against `origin/main@59d7ebb0` (confirmed blob-identical to the live site, sha256
`5d10802e...4804b82`): an unanchored `.vercelignore` pattern silently 404ing committed
assets, three fabricated/mismatched numbers in the page copy, and three missing site-hygiene
files.

**Measured evidence.**
1. `.vercelignore`'s unanchored `data/`/`pipeline/`/`datasets/` patterns matched
   `public/assets/data/*` at any depth (git's own ignore engine, same syntax Vercel
   documents), 404ing 4 committed, non-empty files that sit inside `outputDirectory
   "public"`. Reproduced with `git check-ignore -v` against a scratch tree: unanchored
   `data/` matched `public/assets/data/hoops.json`; anchored `/data/` does not, while the
   sibling `public/assets/news/news_features.json` was never matched either way (why it
   already deployed fine). Anchored all three patterns to repo root.
2. Map toolbar pill read "● live canvas" next to a client-generated seeded-LCG scatter
   with zero network calls behind it (the footer already discloses this correctly one
   sentence down). Changed to "● demo canvas".
3. "MTNN v9.2" (hero kicker, deck, step-5 heading ×2, roster MODELS tile) matches no
   version on file in any of the six repos' `shipped_models.json` entries (real ones:
   hoops `mtnn_v5`, gridiron `v2`, pitch `v1.1`/`v3-target`, equities
   `_rebuild_d64_transformer`, unified `Stage 2.1`). Removed the fabricated version number,
   keeping "MTNN".
4. Footer misattributed vector-unified's combined three-sport row count (20,719) and a
   wrong dim (128) to hoops's own embedding. Per `shipped_models.json`, hoops's live
   embedding is 12,966 rows × 64-d, `mtnn_arch.json` `dIn=130`. Corrected "20719×128-d" to
   "12,966×130-d".
5. Roster point counts for gridiron ("2,000 pts") and pitch ("3,200 pts") matched no
   figure in `shipped_models.json`. Corrected to gridiron's own `assets/embedding.json`
   count (503) and pitch's own `assets/vectors_mtnn.json` count (2,430) — the same "own
   embedding row count" convention hoops/equities/unified's roster tiles already use.
6. `robots.txt`, `sitemap.xml`, `favicon.ico` all 404'd; the page's own `<link rel=icon>`
   was a blank `data:` URI. Added real files: `robots.txt` (allow-all + sitemap pointer),
   `sitemap.xml` (lists only `/` and `/game` — the two pages verified live 200 and
   byte-matched against this ref; the `vercel.json` rewrite targets `/play /model /trends
   /lab /dfs /players` 404 live today, a separate dashboard-config defect out of scope, so
   deliberately omitted rather than listed as if resolved), and a real `favicon.ico` (a
   solid 32×32 PNG-in-ICO in the page's own existing `--pop` token color `#C17C60`).

`index.html` and `public/index.html` are two manually-kept-in-sync committed copies (both
edited together in every prior japandi-v4 commit, e.g. `dc47078`) — edited both identically
to preserve that invariant.

**Verified, and how.**
- Worktree HEAD confirmed == `59d7ebb0380ba02f19af1b7eb651d2f1f0092e88` before editing.
- Served BEFORE (home checkout `public/`, port 8931) and AFTER (worktree `public/`, port
  8932) via `python -m http.server`; curled every touched URL both times (old strings
  present before / absent after, new strings absent before / present after; `robots.txt`,
  `sitemap.xml`, `favicon.ico` 404 before, 200 after). Both ports closed afterward
  (`Get-NetTCPConnection`: no matching connections).
- No formal test runner exists (no `package.json` test script); ran the repo's own
  `scripts/*.py` verifiers instead: `feed_check.py` passes (exit 0, unaffected by this
  change); `check_provenance_hashes.py` crashes on a pre-existing bug unrelated to this fix
  (several `assets/data/*.json` files are top-level lists, which the script's dict-only
  `.get()` call doesn't handle — none of those files were touched here);
  `verifier_hub_live_lines.py` and `verifier_pro_button_up.py` both fail against a legacy
  root-level PWA/live-lines design (manifest.json, sw.js, tokens.css) predating and
  unrelated to the current japandi-v4 markup — none of their ~50 checks reference any of
  the 7 lines this commit touches. Side-effect writes from running those scripts
  (`.scout/missions/_cron/timeline.jsonl`, `bundles/ultra/runs/.../timeline.jsonl`,
  hidden verifier json files) were reverted before this commit.
- Home checkout (`C:\Users\jcdav\vector-hub`) porcelain-empty before and after; HEAD
  unchanged at `59d7ebb`. No vector-hub job was queued or running in `qctl.py status` at
  any point during this lane.

**Explicitly NOT done** (not in the assigned defect list; noted for the operator): D1
`vercel.json` rewrites not honored live (dashboard fix, not code); D4 "PWA v67 offline13k
CORE20" claims with no manifest/sw.js wired to the hub root (product decision); D5 roster
a/b scorecard numbers with undefined units (product decision).

**Merge target and blocker.** Base: `origin/main` (`59d7ebb0`), 1 commit ahead, clean. No
blocker.
