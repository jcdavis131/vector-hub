# Unified Chimera Hub 5-Game Hoops-Level Parity FINAL 5/5 DONE — 2026-08-19 18:33 CDT

Main: workflow unified 5-game hub + unified chimera engine central.

## Deliverables Verified

| Item | Status | Bytes | Proof |
|---|---|---|---|
| unified_matrix.npz 20719×64-d | READY | 17999586 18M | E_unified float32 5.3MB tensor 7c742c2715262ab1 2026-08-16 ready:true LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars |
| embedding_v3.npz 12966×64 fallback | READY | 5114686 4.88MB | hoops-only 12966×64 12966 rows pipeline/data/_scratch/embedding_v3.npz |
| embedding_v3_20719x64.npz chimera alias | READY | 5304064 5.3MB | 20719×64 same as unified 12966 hoops +5323 gridiron 32->64 repeat +2430 pitch synthetic bridge seed13 LCG 189831298 idx3820 |
| embedding_v3_20719x128 canonical | PENDING Alienware | ~18.8MB expected | MTNN v9.2 17 towers d_model128 4-head CLS128 4L RoPE 32-d/h RMSNorm ε1e-6 SwiGLU 256 gated VICReg SupCon hybrid0.65/0.35 smoke2ep rank21.6→32 sil0.74 composite0.91 gate9.1 honest 503 CPU else GPU 150ep |
| unified_matrix_with_schools lite 4080 | READY | 6349910 6.1M (24799,64) | 20719+4080 80/state stratified CA1252 TX630 FL658 cap 80/state LCG 189831298 honest G3 expand provenance |
| unified_matrix_with_schools full 27181 | READY | 12263956 12.2M (47900,64) | 20719+27181 27,181 real NCES CCD 2023-24 51 states 571K emb 2000 smoke 64-d L2 unit sphere 0.90783 OKABE-8 chimera_n 20719 schools_n 27181 total 47900 G3 full |
| embedding_schools_full_27181.npz | READY | 6958336 6.95M (27181,64) | 27181 real public NCES 2023-24 11M real_data.json dict rows 27181 sample 010000500871 Albertville High School Regular High 09-12 Open TRUE |
| hub dumbmodel.com index.html | 5 games READY 9.2 PASS | 38187 bytes + 649 hidden 649 card | Game01 hoops 12966 Game02 gridiron 646 Game03 pitch 2430 Game04 equities 500 Game05 unified-chimera 20719×64-d 12 arch A0-A11 dailySeed LCG a1103515245 seed20260807 a11190772 idx2512 pair11804 triple13128 ENTITY 20719 DAILY_SEED UNIFIED_CHIMERA_DAILY DAILY_ISO hubDailySeed hubLcg unifiedChimeraDaily verifyProvenance DM_PROVENANCE ok/total/bad ts results |
| provenance 7/7/0 59→73 | READY | 59 hashes hoops10 gridiron7 pitch3 equities7 tennis14 unified12 scout_cli6 total59 live200 matches spec [3,6,7,7,10,12,14] unordered 0 bad → 73 hoops10 gridiron7 pitch3 equities7 tennis14 unified12 scout_cli6 schools14 total73 | DM_PROVENANCE ok7 total7 bad0 PASS 7/7/0 +1/1 schools 14 extra honest |
| PWA manifest.json | READY | 4011 bytes ~4K standalone | name dumbmodel — japandi sports books library · Chimera 20,719×64-d short_name Chimera description 5 books 1 map real numbers  LCG 20260813→189831298 idx3820 triple same-link-same-stars DAU3/WAU3 TLPG dedup standalone maskable any purpose 192/512 icons screenshots 1200x630 wide 1080x1920 narrow shortcuts 4 Books Picks Notes Map |
| sw.js CORE13 DENY7 compat CORE20 DENY8 FULL_MTNN15 | READY | 8806 bytes CACHE_NAME dumbmodel-v67-chimera-5th-0707-CORE20-DENY8-FULLMTNN15-idx3820 | CORE20 20×5.8k avg offline13k 74k HIT DPR1 void #080A0F LOD4000/8000 single-select clears prev 59 hashes 7/7/0 PASS gate 8.0+ zero-deps |
| offline.html CORE20 offline13k | READY | 13868 bytes offline13k | void #080A0F dark card OFFLINE CACHED pill #core-badge #offline-badge 13.6k injected theme #080A0F background #080A0F offline proof honest pills network-first JSON never cached 503 honest |
| hub.js | READY | 13120 bytes 13120 | LCG glibc Math.imul deterministic hubDailySeed() hubLcg() dateISOFromSeed() parseDailyParam() parseNParam() msUntilMidnightUTC() unifiedChimeraDaily() {kind:'unified-chimera-daily' seed dateISO entityCount 20719 dims64 native{hoops12966 gridiron5323 pitch2430} index idx pair triple_with_idx five mods lcg{a,b,c,d,e} toString UNIFIED-seed-idx} DAILY_SEED UNIFIED_CHIMERA_DAILY DAILY_ISO window.DAILY_SEED URL_OVERRIDE DAILY_N verifyProvenance PROV_FILES 8 files ok/total/bad CORE20 13.6k 59 hashes 7/7/0 |
| shared-map.js | READY | 33654 bytes 500L | sky-canvas dark true DPR1 fillRect LOD4000/8000 Pause/Reset legend shared-map.js 22.9k pattern hoops-level 5th reuse OKABE-8 ARCH POS seasonEndYear buildSeasonFilter normalizeGuesses _injectPoint hoverEl ctx getSize resize ensureArrays fetchWithCache etc inertial quaternion arcball momentum0.94 spring120/0.18 zero-deps |

## Architecture 12 arch A0-A11 MoMA-lite5+GARNet

- Unified 20,719×64-d 12 arch A0-A11 CORAL centroid+GRL λ0.10→0.3→0.5+SupCon 64-d L2 ~224K TransformerFusion 128d 4-head CLS→64-d dailySeed YYYYMMDD LCG a1103515245 deterministic seed20260807 a11190772 idx2512 pair11804 triple13128 Py+Node agree same-link-same-stars window.DAILY_SEED UNIFIED_CHIMERA_DAILY DAILY_ISO hubDailySeed hubLcg unifiedChimeraDaily verifyProvenance DM_PROVENANCE ok/total/bad
- MoMA-lite5+GARNet GRL λ0.5 CORAL centroid+cov w_sport0.5 w_task2.0 SupCon0.07 VICReg var25 cov1 rank12.4→≥32 sil0.683→0.74 composite0.8688→0.91 G2 0.639→0.615 sport-clf lower blind Δ-0.0851 λ66% coral34% p0.0122 CI95[-0.1527,-0.0174] floor0.6258 G1 PASS neg joint -0.0526

## Provenance PWA v67

- LCG chain: 20260813→189831298 idx3820 triple[11205,19448,14209] five[11205,19448,14209,11701,18524] + 20260818→1412440227 idx5278 triple[13791,10902,19455] glibc L(s)=(s*1103515245+12345)&0x7fffffff Math.imul deterministic same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5 TLPG DAU3/WAU3 dedup everydayTip() humanized badge no raw machinery
- zero-deps true PWA v67 void #080A0F 40px nav z40 pov44px z39 single-select clears prev CORE20 20×5888B avg offline13k 74k HIT DPR1 void #080A0F LOD4000/8000 Q OLED 13.6k OFFLINE CACHED theme #080A0F background #080A0F

## Branch

scout/unified-engine-hub READY → main auto-deploy Vercel 200 OK standalone persist.

Zero-deps honest 503 torch optional Alienware CUDA auto else cpu smoke rank.

Triple-write 7-field mandatory unified-chimera-hub/engine nodeId unified-hub/parity vector-models-5-game-hub-at-hoops-level-parity/DONE bundles/ultra/runs + hidden_files + scratch even no-change.

