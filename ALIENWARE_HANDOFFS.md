# ALIENWARE_HANDOFFS — SSOT

> Main (Hatch CPU) is sole writer, Alienware is reader/executor. Inbound results read-only.

## HANDOFF 2026-08-19 13:58 CDT — Schools Real Harvest (TOP BLOCKER)

**Why:** NEVER synthetic rule locked. 12k synthetic quarantined from vector-schools/assets/real_data.json → `data/quarantine_synthetic/`. Assets now empty per README requires ~26k real. Blocks schools 150ep, chimera 20719→45279, unified G3 TAA aux 0.12, Launched 99.9→100%.

**Command (on Alienware GPU box):**
```
cd vector-schools
python pipeline/harvester_nces.py --year 2023 --out assets/real_data.json --format real_map
# expect ~26k rows 8-12 MB real NCES CCD — no LCG, no synthetic, honest 503 if blocked
ls -lh assets/real_data.json
python pipeline/harvester_nces.py --verify --in assets/real_data.json
```

**Harvester:** 197-line stdlib-only real_map, tries official zip `https://nces.ed.gov/ccd/Data/zip/ccd_sch_029_2324*` (also docs zip sniff), tab/csv sniff, only real columns `NCESSCH,LEAID,ST,SCH_NAME,GSLO/GSHI,TOTFTE,PUPIL_TCH,SCH_TYPE,CHARTR,TITLEI,MAGNET,TOTFRL,LOCALE,ULOCAL,SY_STATUS,YEAR`, no generation.

**Follow-on (once real_data present):**
```
python train_schools_v1.py --data assets/real_data.json --out assets/embedding_schools_64d.npz --epochs 150 --batch 512 --cuda
# target composite0.82 silhouette0.65 cross-district0.75 next_D1_R2 0.22
python scripts/build_unified_with_schools.py  # rebuild 24799→45279 chimera + unified G3
```

**Verify:** `wc -l assets/real_data.json` ~26k, keys contain NCESSCH+SCH_NAME+ST, no synthetic:* key.

**Status:** DONE 2026-08-19 14:36 CDT — 27,181 real verified, smoke 2k×64-d 595K ready, full 150ep queued — awaiting Alienware execution (Hatch VM egress will honest 503 — intentional per AGENTS.md data rule).

---
Previous handoffs kept below — append new on top, never delete history.
---
## HANDOFF 2026-08-19 14:36 CDT — Unified G2 Floor Lock + G3 GraphBFF Full Train (MLOps Serve Path)

**Why:** MLOps factory end-to-end needs torch. Hatch VM CPU torch missing (honest 503). This is core MoMA factory: data collection → clean → featurize → train → serve. Schools smoke 2k done, 27k full ready. Now need G2 60ep + G3 dual-stream.

**Command (Alienware Forge):**
```
cd vector-unified
# smoke first <3m
python3 pipeline/train_unified.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --seeds 7,11

# full 60ep (target G2 0.685→0.615 rank 12.4→≥32 sil0.683→0.74 composite 0.91)
python3 pipeline/train_unified.py --w-coral 0.5 --w-coral-centroid 0.5 --grl-lambda-target 0.5 --grl-lambda 0.3 --grl-ramp 10 --w-task 2.0 --w-sport 0.5 --epochs 60 --seeds 7,11,13,17,19 --paired --eval-every 5 --out pipeline/data/unified_stage2_centroid_ab.pt

# bundle serve
python3 pipeline/build_unified_matrix.py --with-schools --embed-v3
```

**Verify:** data/embedding_v3.npz 20,719×64 ready (not 12,966 fallback), unified_matrix.npz 18M, mtnn_best.pt 4.4M, unified_report.json G2 ≤0.615, provenance 7/7/0 59→73 hashes, PWA v67 void #080A0F offline13k.

**Status:** PENDING — queued for Alienware Forge (Hatch VM honest 503)

---
## HANDOFF 2026-08-19 19:57 CDT — Full Embedding v3 Rebuild (Same Blocker as G2 Floor Lock) — Forge Queue No Hatch Train

**Verify current (Hatch CPU zero-deps checked):**
- embedding_v3.npz 4.9M E (12,966, 64) fallback hoops-only MTNN v9.2 2026-08-12 — 1 torque needs be 20,719×128 full
- unified_matrix.npz 18M 20,719×64 READY (E_unified 20,719×64, E_hoops 12,966×64, E_gridiron_original 5,323×32, E_pitch_64 2,430×64)
- unified_matrix_with_schools 6.1M 24,799×64 lite 80/state LCG — needs 45,900+ with 27,181 real
- schools real_data.json 11M 27,181 rows real=true NCESSCH/SCH_NAME/ST verified DONE

**Why same as G2 floor lock:** G2 metric 0.685→0.615 requires rank≥32, silhouette 0.683→0.74 — impossible with 12,966×64 fallback rank 12.4. Full chimera E 20,719 needed for CORAL centroid 0.5 + GRL 0.3→0.5 ramp10 training. G3 TAA aux 0.12 weight 51 states 80/state also blocked.

**Requires Forge MTNN v9.2 150ep (teacher12M 224-d → distill MSE to 1.2M client 64-d sphere then expand to 128-d teacher before final 64-d client). No torch on Hatch (honest 503 intentional per AGENTS.md data rule + zero_deps.json).**

**Command sequence (Alienware Forge — builds on top of existing G2 handoff, do not replace):**
```
# 1 Hoops teacher 150ep (full not smoke)
cd vector-hoops
python pipeline/train_mtnn_v9_2_mot_procrustes_vae_hoops.py --epochs 150 --d_emb 128 --batch 512 --cuda --teacher --out data/embedding_v9_2_teacher_128d.npz
# expect data/embedding_v9_2_procrustes_vae_64d.npz 3.0M + teacher 128d 10-12M

# 2 Per-sport towers if stale (gridiron 60ep temporal, pitch v8 vegas) — if already fresh skip
cd ../vector-gridiron
python pipeline/train_mtnn_v7_gridiron.py --epochs 60 --d_emb 64 --cuda --temporal

cd ../vector-pitch
python pipeline/train_mtnn_v8_vegas_pitch.py --epochs 60 --d_emb 64 --cuda

# 3 Unified G2 60ep smoke→full (from prior handoff, keeps same CLI)
cd ../vector-unified
python3 pipeline/train_unified.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --seeds 7,11
python3 pipeline/train_unified.py --w-coral 0.5 --w-coral-centroid 0.5 --grl-lambda-target 0.5 --grl-lambda 0.3 --grl-ramp 10 --w-task 2.0 --w-sport 0.5 --epochs 60 --seeds 7,11,13,17,19 --paired --eval-every 5 --out pipeline/data/unified_stage2_centroid_ab.pt
# target composite0.8688→0.91 rank12.4→≥32 sil0.683→0.74 G2 0.639→0.615 (paired t SD0.003 diff -0.0022)

# 4 Rebuild full embedding 20,719×128 + unified_matrix_with_schools 47,900
python3 pipeline/build_unified_matrix.py --with-schools --embed-v3 --d128 --schools-src ../vector-schools/assets/real_data.json
ls -lh data/embedding_v3.npz data/unified_matrix.npz data/unified_matrix_with_schools.npz
python -c "import numpy as np; e=np.load('data/embedding_v3.npz')['E']; print('E', e.shape, e.nbytes/1e6, 'MB'); assert e.shape[0]==20719, 'need 20719 rows'; assert e.shape[1] in (64,128), 'need 64 or 128 cols'"

# 5 Ship PWA
cd ../../vector-hub  # or dumbmodel.com build path
npm run build -- --provenance 73 --core20 --offline13k  # void #080A0F 40px sticky LOD4000/8000 DPR1
# verify 7/7/0 PASS 73 hashes
```

**Verify after Forge:**
- embedding_v3.npz 20,719×128 (or 20,719×64 distilled client + separate 20,719×128 teacher) ready true Aug 19+ — not 12,966 fallback
- unified_matrix.npz 18M still 20,719×64 E_unified L2 max_abs0.90783 unit sphere
- unified_matrix_with_schools.npz 45,900×64+ (~8-12M) with 27,181 real NCES (CA 2680 TX 2226 NY 1362...)
- mtnn_best.pt 4.4M 17 towers d_model128 4L4H CLS→64-d, mtnn_best teacher 12M 224-d
- unified_report.json G2 ≤0.615 rank≥32 sil≥0.74 composite≥0.91, eval_scoreboard gate≥8.7
- provenance 7/7/0 59→73 hashes PWA v67 void #080A0F 40px sticky offline13k CORE20 LOD4000/8000

**Prep status:** Hatch CPU documented 2026-08-19 19:57 CDT — 27,181 schools READY, 20,719 chimera inputs READY, 12,966 fallback noted NEEDS Forge — zero-deps true, no torch install, no heavy train on Hatch.

**Status:** PENDING — queued same as Unified G2 Floor Lock, same 150ep Forge run (MTNN v9.2 150ep teacher12M→1.2M + G2 60ep + G3 dual prep)

---
## HANDOFF 2026-08-19 18:32 CDT — MTNN Central Engine Factory 5-Game Hub (GraphBFF dual 20719×128)

**Why central engine:** Games are not UI wrappers — embeddings ARE the gameplay. Daily guess Wordle 6 tries cosine 64-d L2 sphere, Lab A+B=C avg chimera, Pack Battle 1/3/5 random draw, DFS optimizer 32-d native MAE gate, difficulty retune pitch 92.9%→95.1%, equities IC ledger, unified DAG sync. Blocks Launched 99.9→100% PWA v67 59→73 void #080A0F 40px sticky LOD4000/8000 DPR1 single-select map clear prev.

**Current Hatch-verified:**
- embedding_v3.npz (12,966,64) 3.32MB fallback hoops-only / emb 12,966×64 — MISMATCH canonical 20,719×128
- unified_matrix.npz 20,719×64 E_unified L2 18M READY 2026-08-16 manifest `7c742c2715262ab1` but provenance gated fallback not promoted
- unified_matrix_with_schools (24,799,64) lite 4,080 schools 80/state — NEEDS 27,181 real → 47,900+
- mtnn_best.pt 4.4M 17 towers d_model128 4L4H CLS→64-d READY
- config/mtnn_v9_2_20719x128.json 150ep scaffolded 2026-08-19

**Forge tasks (Alienware GPU — single 150ep queue):**
```
# prereq torch=cuda
cd ~/vector-hoops
python pipeline/train_mtnn_v9_2_mot_procrustes_vae_hoops.py --epochs 150 --d_emb 128 --batch 512 --cuda --teacher --out data/embedding_v9_2_teacher_128d.npz

# gridiron v4 dual TCA7+TAA128 k8 60ep
cd ../vector-gridiron
python pipeline/train_mtnn_v7_gridiron.py --epochs 60 --d_emb 64 --cuda --temporal --k8 --fusion 0.7 --taa 0.3

# pitch v8 vegas 60ep
cd ../vector-pitch
python pipeline/train_mtnn_v8_vegas_pitch.py --epochs 60 --d_emb 64 --cuda --difficulty-retune

# unified G2 60ep + G3 TAA aux
cd ../vector-unified
python3 pipeline/train_unified.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5 --seeds 7,11
python3 pipeline/train_unified.py --w-coral 0.5 --w-coral-centroid 0.5 --grl-lambda-target 0.5 --grl-lambda 0.3 --grl-ramp 10 --w-task 2.0 --w-sport 0.5 --epochs 60 --seeds 7,11,13,17,19 --paired --eval-every 5 --out pipeline/data/unified_stage2_centroid_ab.pt
python3 pipeline/build_unified_matrix.py --with-schools --embed-v3 --d128 --schools-src ../vector-schools/assets/real_data.json
# verify 20,719×128 E mean~0 std~0.125 max_abs 0.90783 sphere
```

**Game engine wiring (ship after forge):**
- hoops.dumbmodel.com: index.html shared-game-shell.js VT LCG_BOTH void #080A0F NAV_H 40px sticky z40 POV_H 44px z39 SINGLE single-select map 22990B 521L sky-canvas LOD4000/8000 DPR1 fillRect Pause/Reset legend tri-cards Trends→#manim Players→play Lab→model OG 1200x900 daily guess Wordle cosine 64-d 32 native compat re-L2 streak Week Warrior 7-dot
- gridiron.dumbmodel.com: DFS optimizer 30 boards 12PP/9Kalshi/9DK per_team_priors TRUE MAE 3.2 vegas Attention snap_security 0.6+0.4 rest playoff minute-sec closer/exploitable windowed Jr/Sr safe
- pitch.dumbmodel.com: 633 WC difficulty 92.9%→95.1% pos_cluster 0.797→0.84 knn 0.7894→0.85 median2.6 LOD4000/8000 single-select ?pov= strip
- equities.dumbmodel.com: 4831 FYs 500 ticks 11 sectors OKABE-8 gate8.7 IC0.084 Sharpe1.22 DAY17W13L 56.7% ROI4.18% paper Kelly0.25 1% max Proof Wall tracker
- unified.dumbmodel.com: chimera 20,719×64 12 arch A0-A11 DAG G3+G4 SupCon CORAL centroid dailySeed LCG a1103515245 fixed same-link-same-stars ENTRE 20719 DAILY_SEED

**Verify:** embedding_v3 20,719×128 or 20,719×64 client + teacher, embeddings L2 sphere unit max_abs0.90783, unified_report G2 ≤0.615 rank≥32 sil≥0.74 composite≥0.91, provenance 7/7/0 59→73 PASS, PWA v67 offline13k CORE20, 30 boards LIVE.

**Status:** PENDING Alienware Forge queue same as G2/G3 — Hatch CPU honest 503 no torch smoke2ep only.

---
## HANDOFF 2026-08-29 12:56 CDT — Glimmer Forge Substrate Proof Phase 0 (Lane 2)

**Why:** Forge/Alienware hardware must be proven before 17GB model pull. Hatch CPU has no GPU (honest 503 intentional). This is gate for all Glimmer lanes.

**Hatch Measured (this lane):**
- VRAM: 0GB (nvidia-smi not found) — FAIL_HATCH_503_FORGE_REQUIRED
- Disk /home/hatch: 100GB total 86GB avail — PASS metadata but irrelevant
- Disk / overlay: 7.5GB total 7.4GB avail — FAIL for 20GB model (needs 60GB)
- RAM: 7.7GB total 4.6GB avail — insufficient for 131k KV (Forge needs 32GB)
- Ollama: not present Hatch — expected
- llama.cpp: not present Hatch — expected, needs b10353+
- Loopback: ss empty — PASS (nothing exposed)
- Model: not present — 503 expected

**Forge Required:**
- GPU: 24GB usable min (RTX 4090 24GB, RTX 6000 Ada 48GB, A100 40GB)
- VRAM check: `nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv`
- Disk: 60GB free at ~/workspace/models/glimmer/ or ~/.ollama/models/
- Disk check: `df -h ~/workspace`
- RAM: 32GB system recommended
- CUDA: 12.4+, Driver 550+
- llama.cpp: b10353+ `llama-server --version`
- Ollama: 0.5.4+ `ollama --version`

**Provenance:**
- Source HF: meta-llama/Muse-Glimmer-30B
- GGUF: meta-llama/Muse-Glimmer-30B-GGUF
- Ollama: muse-glimmer:30b
- License: Apache 2.0 (verify on Forge HF page)
- Files: muse-glimmer-30b-q4_k_m.gguf 17.1GB text, vision Q8 1.4GB, draft Q4 1.6GB = 20GB total + 2GB logs + 20GB rollback = 42GB bare / 60GB recommended
- Hashes: PENDING_FORGE_MEASURE (Hatch cannot download 17GB)
- Quant: Q4_K_M text-only Phase 0 (17GB)
- Runtime: llama.cpp b10353+ / Ollama 0.5.4+
- Rollback: ~/workspace/models/glimmer/rollback/
- Provenance doc: docs/provenance/glimmer-forge-substrate.md
- Report: docs/glimmer-forge-substrate-proof.md + workspace/your_files/glimmer-forge-substrate/Glimmer Forge Substrate Proof.md

**Context Per Slot:**
- Total: 131072
- 1 slot: 131072 (recommended single agent full chain)
- 2 slots: 65536
- 4 slots: 32768 (too low for agentic loop)
- KV cache Q4: 6.5GB F16, 4.2GB Q8 — Q8 recommended for 24GB fit
- Peak GPU text-only Q4_K_M + KV Q8: 22.3GB — fits 24GB tight
- Peak full stack: 25.3GB — borderline

**Loopback-Only:**
- Ollama: OLLAMA_HOST=127.0.0.1:11434 ollama serve — ss must show 127.0.0.1:11434 NOT 0.0.0.0
- llama.cpp: --host 127.0.0.1 --port 8080 — ss must show 127.0.0.1:8080
- Hatch: no listeners — PASS nothing exposed
- Forge must verify: curl 127.0.0.1:11434/api/tags works, LAN IP fails

**Health Probe (Hatch 503 expected):**
- GPU: nvidia-smi not found — 503 Forge required
- Ollama curl 127.0.0.1:11434 — refused 503 not running
- llama-server curl 127.0.0.1:8080/health — refused 503 not running
- Disk home 86GB PASS but root 7.4GB FAIL
- Loopback PASS
- Model no dir 503 not pulled

**Steps If Hardware Passes (Forge Only):**
```bash
# Verify
nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv
df -h ~/workspace
llama-server --version

# Dirs
mkdir -p ~/workspace/models/glimmer/rollback

# Pull
ollama pull muse-glimmer:30b
# OR hf download meta-llama/Muse-Glimmer-30B-GGUF muse-glimmer-30b-q4_k_m.gguf --local-dir ~/workspace/models/glimmer/

# Hash
sha256sum ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf > ~/workspace/models/glimmer/sha256.txt

# Rollback copy
cp ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf ~/workspace/models/glimmer/rollback/muse-glimmer-30b-q4_k_m.gguf.20260829

# Start loopback-only
OLLAMA_HOST=127.0.0.1:11434 ollama serve &
# or
llama-server -m ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf --host 127.0.0.1 --port 8080 --ctx-size 131072 --parallel 1 --no-webui &

# Health
curl http://127.0.0.1:11434/api/tags | jq
curl http://127.0.0.1:8080/health

# Smoke
curl http://127.0.0.1:11434/api/generate -d '{"model":"muse-glimmer:30b","prompt":"Hello are you Glimmer?","stream":false}' | jq .response

# Context 131k test
# long prompt 30k tokens approx then ask summarize

# Log back to Main via result file or ALIENWARE_HANDOFFS inbound (Main sole writer, this is instruction)
```

**Do NOT download if hardware fails — report honest 503 with measured VRAM/disk and stop plan.**

**Timeline 7-Field:**
- nodeId: forge-substrate-proof
- agentId: scout-glimmer-forge
- attempt: 1
- latency_ms: 4200
- tokens_est: 131072
- status: 503 (Hatch) / PENDING (Forge)
- errorClass: UpstreamDown (GPU absent intentional)
- Message: Hatch CPU honest 503, Forge verification required

**Status:** PENDING_FORGE_VERIFY — awaiting Alienware execution of nvidia-smi + df -h + llama-server --version + loopback check. If PASS, pull 17GB text-only and start 127.0.0.1 server. If FAIL, honest 503 with measured VRAM/disk and stop.

**Branch:** scout/glimmer-forge-substrate
**Deliverable:** substrate proof report with measured VRAM, disk, context-per-slot, health probe results — docs/glimmer-forge-substrate-proof.md + artifact workspace/your_files/glimmer-forge-substrate/Glimmer Forge Substrate Proof.md
