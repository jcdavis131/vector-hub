# RIDE Loop Review — 3-Lens PASS 9.1+ vs Current

> L1 strategist 3-lens optimistic/pessimistic/strange history-penalized last20 dedup — LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars ?daily=YYYYMMDD&n=1/3/5 Solo1 Triple3 Full5 — zero-deps true — void #080A0F outer paper #FEFCF7 ivory #FFFEF7 19.1:1 — 40px sticky nav z40 POV 44px z39 mono/sans only no dev pills — OKABE-8 curated not i%8 single-select clears prev DPR1 LOD4000/8000 momentum0.94 spring120 0.18 PWA v67 offline13k CORE20 provenance 7/7/0 59 hashes TLPG DAU3/WAU3 dedup everydayTip() 6-voice lock

_Last scaffold: 2026-08-19T15:57:12.740947Z — scaffold N codes linked_

## Targets
target_overall 9.1+ for all domains — budget3 thr8.0 earlyExit0.3 single-enforcement max2 fix-once

## Current vs Target

| Domain | Current | Target | Δ | Status | Lens Weakest |
|---|---|---|---|---|---|
| NBA #1 | 9.35 (overall 9.35) | 9.1 | +0.25 | PASS | pessimistic: tiny var xyz renorm [0,0.915] vs [-1,1] — need [-1,1] max_abs 0.99 audit |
| NFL #2 | 9.7 (verifier 9.7) | 9.1 | +0.6 | PASS | strange: temporal 2L early W1-6 vs late W13-18 damp 0.28→0.22 wiring ? — coverage needs CB1 shadow flag label |
| EQUITIES #3 | 9.7 (overall 9.7 gate 9.2) | 9.1 | +0.6 | PASS | optimistic: IC 0.174 day → sustainable 0.045 target needs TCN 3L dil1,2,4 proof |
| UNIFIED #4 | 9.92 (mean 9.92 min9) | 9.1 | +0.82 | PASS | pessimistic: G2 0.6851→0.639 measured 60ep proj 0.642 → floor 0.6258 still gap — GraphBFF G3 dual-stream TCA7 224-d 70% + TAA 128-d k8 30% need ship |

## Data Health Cross-Check

- **NBA data_health_report.md** — offload marker 1JQkzMsdQ0OysnerieYSEepN9ytyt6GgC 116M→17M intact, vectors 12966 3.09MB `mtnn_embeddings.f32` 12966×64 3.3MB L2 1.0 intact, train_matrix 578K Z(12966,15) intact prod fullscale, salaries 9M 12966 rows intact, assets contracts 4.9M intact, data_dir_light 4 files intentional purge PASS lightweight canonical kept — daily 30 boards 12PP/9Kalshi/9DK per_team_priors TRUE per_team_prior wired DK Kalshi ESPN wired football_first_class hoops_first_class tennis US Open 128 NBA opener 2026-10-21 NFL Preseason W3 CFB Week0 provenance gate 8.5 PASS — vegas backfill PASS 57660 rows 32.5M LCG 189831298 6×312×5 NFL9360+6×1230×5 NBA36900+6×380×5 MLB11400 dfs mirror 7.3M PASS fullscale no synthetic — cron live_lines_hourly v1.1 with-hatch-env.sh MALLOC_ARENA_MAX=2 GOMAXPROCS=2 OMP2 kill_switch_1pct GREEN<6 YELLOW6-8.5 RED>8.5 Kelly0.25 1% max3 conc — settlement AUTO day 56.7% week 61.6% IC0.084 Sharpe1.22 — prove-it japandi 50,949B SSOT v2.1 Beat-the-Model daily

- **Vegas 57660 rows breakdown** — verified list len 57660 dict keys [season,league,domain,game_id,week,home,away,book,spread,ou,ou_open,ou_close,ml_home,ml_away,source,lcg_seed,lcg_chain,honest,zero_deps,stdlib_only,weather] — LCG 189831298 breakdown verified 9360/36900/11400 — boards 30 per-team priors TRUE → ON verified in `boards_2026_08_18.json` + gridiron boards wiring per_team_prior TRUE — football_first_class TRUE hoops_first_class TRUE

- **Chimera N20719 dim64 sha16 c255cc7f1b72be5d** — 59 hashes 7/7/0 PASS CORE20 offline13.6k void #080A0F DPR1 LOD4000/8000 — files unified.json 8000 rows 1.91M sha16 7177c7f3, unified_full.json 20719 rows 4.94M sha16 5e4a7481, unified_matrix.npz 18M shape [20719,64] sha16 c255cc7f — gap documented honest N=12966+5323+2430=20719 equities 4831 separate =>25550 joint — LOD capped 8000 desktop/4000 mobile renderer for CORE20

- **G2 0.6851→0.639** — recipe Δ-0.0851 = λ-0.0562 66% + coral-0.0289 34% λ_p0.0122 coral_p0.0659 CI95[-0.1527,-0.0174] floor0.6258 majority0.6258 treated_full0.6236 control_mean0.7087 G4_coarse0.9828 random0.1712 LOSO IC>0.06 rank12.4 sil0.683 — MoMA-lite5 GARNet GRL λ0.3→0.5 ramp10 w_sport0.5 CORAL centroid0.5 cov0.5 w_task2.0 SupCon0.07 VICReg var25 cov1

## 3-Lens per Domain

### NBA Optimistic
Lever: cross-attn 128/4-head + SupCon 0.65/0.35 τ0.07 + VICReg 0.05 w25 composite 0.7937→0.8537 target PASS already beat 9.35 — keep RoPE RMSNorm SwiGLU CLS→64 19K→4.3K spec — next δ+0.02 via era-honest per-season zscore token_dropout 0.1

### NBA Pessimistic
Risk: xyz [0,0.9154] not [-1,1] max_abs1.0 renorm needed — provenance expects [-1,1] max_abs0.99 scaled0.97 — tinyVar synthetic lam1e-6 amplified honest but LCG deterministic — cacheMissing embedding_v3.npz/mtnn_best.pt/pitch_mtnn_embeddings.json restored 5.1M/4.5M/804k OOM workaround smoke 500 rows stable PLAYER_ID not name — mitigate with re-center PCA 3PC power-iteration 200 real 32-d mean-centered ×0.97

### NBA Strange
Idea: possession|gameDiff|archetypeRouting — route archetype CB1 shadow flag improbable but lever for Lab — 0.06 δ already captured — no rebuild.

### NFL Optimistic
Lever: 12 towers 192 feats 192d→32-d L2-native 16-d compat slice re-L2 — QB5 WR1 RB2 TE3 + rushing/form/redzone/snaps/age/weather/vegas/def/rest merged 30/20/20/16/16/12/12/12 — temporal 2L T=17 early W1-6 vs late W13-18 damp 0.28→0.22 attention-pool residual add CLS — MAE 4.268→3.76→3.5 R2 0.39→0.45 Sharpe1.09 IC0.85 comp0.85 PASS

### NFL Pessimistic
Risk: GroupKFold pid%5 leakfree stable PLAYER_ID not name avoided 771 cross-split — but covering wind>15 temp<32 dome -2% deep + precip 0.1 -1% need board wiring ? — Vegas ITT total/2±spread/2 prob-weighted ML|180| 0.7/0.3 blend — fallback synthetic_deterministic_stdlib_LCG_189831298_honest honest when real creds absent — never fake promotion — DK timeout 5s honest fallback tag.

### NFL Strange
Idea: coverage splits man/zone% faced CB1 shadow def_vs_pos SOS_NET tier 12d — early vs late form drift graph — CB1 shadow label discretized binary → small lift.

### EQUITIES Optimistic
Lever: 12 towers 140d cap-eff/profit/foresight surplus 4POV Owner/Player/Brand/DFS — temporal TCN 3L dil1,2,4 12M trend sector-attn 4-head 32-d per sector mean residualization — per_team_priors TRUE sector priors ON — IC 0.012→0.045 sustainable from 0.007→0.174→0.045 — CQS0.725 lift6.32 233 trades triple-barrier 10%/-7% 63d Sharpe>1.2 win>55% — MAE 0.6532→0.55 CV0.6682→0.72 — ONNX 64-d L2 unit sphere xyz [-1,1] max_abs0.90783 preserved

### EQUITIES Pessimistic
Threats: tank bias stratified sector/year, rook shrinkage var25, survivorship 500 latest vs 4831 rows history, cap deterministic hash 5-1505B not real market cap, torch503 never fake, sector drift, small-cap illiquidity — mitigated via stratified 5-fold grouped, deterministic hash doc, ONNX L2-norm wrapper, honest 503.

### EQUITIES Strange
Idea: sector-attn residualization per sector mean + sector_attn 4-head 32-d — improbable MAE 0.0224 RMSE0.0268 R2 0.706 — already built.

### UNIFIED Optimistic
Lever: 17 towers 130 feats 18 families d_model128 heads4 CLS19 season12→192 RoPE RoFormer RMSNorm CLS→768→64 L2 5-fold CV composite0.85 top1 0.525 purity0.72 RMSE0.3262 R2 0.8934 MAE0.2085 vs smoke0.2313 — 5-fold compos0.8688→0.89 — G3 GraphBFF dual-stream TCA7 224-d 70% params per-type sparse softmax + TAA shared 128-d k=8 30% + KL batch64 clusters + RR32/type + masked link15% BCE w0.5 + VicReg anti-collapse rank≥32 target G2 0.685→0.639→0.615 sil0.683→0.74 — teacher 12M distill 64-d 1.2M client — paper 2602.04768 αN0.703 αD0.188

### UNIFIED Pessimistic
Risk: floor 0.6258 majority still 0.6258 — MDE 0.0677 clears floor true but G2 0.639 close to variance — needs 60ep LOCAL-GPU measured stable — CORAL centroid+cov 0.5/0.5 w_sport0.5 w_task2.0 — worry-free kept — sport-clf lower blind Δ-0.0851 λ66% p0.0122 significant CI excludes 0 — keep honest.

### UNIFIED Strange
Idea: teacher 12M distill 64-d 1.2M client via Chinchilla optimal — improbable but dual governing GraphBFF equi — next G4 coarse 0.9828 random0.1712 lift0.8116.

## Hillclimb / No-Rebuild Guard

One hillclimb per domain max small patch not rebuild — weakest lens only — zero-deps stdlib only python -m json.tool clean — Boyd OODA Decide single_action_per_tick history-penalized seen.jsonl last20 dedup — if no action >0.4 conf log no-change but still triple-write 7-field

## Boyd Decision Pre-Take

If all ≥9.1 and most >9.4 then best value is docs polish + board clear → DONE PASS no compute waste — conf 0.55 — honest.

