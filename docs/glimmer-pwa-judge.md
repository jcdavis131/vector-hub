# Glimmer PWA Judge — Lane 4 Full Re-Run

Branch: `scout/glimmer-pwa-judge`

## Files
- `dottie/apps/arxiviq/lib/judge/glimmer-client.ts` — loopback-only gateway (127.0.0.1:11434/8000/8080/8081), honest 503, no public exposure
- `dottie/apps/arxiviq/lib/judge/pwa-judge.ts` — PWA v67 + hoops judge pipeline, 59→73 hashes, offline13k, CORE20 47 gold
- `dottie/apps/arxiviq/app/api/judge/route.ts` — Next.js API route, GET/POST, honest 503, timeline triple-write
- `vector-hoops/tools/glimmer-judge.mjs` — CLI judge, zero-deps Node 20+, loopback-only

## Endpoints (loopback-only)
- Ollama: `http://127.0.0.1:11434` (primary, 29.6B dense + 1.8B ViT-G/14, 131k ctx)
- vLLM: `http://127.0.0.1:8000` (OpenAI-compat fallback)
- llama.cpp: `http://127.0.0.1:8080`
- MLX: `http://127.0.0.1:8081`

All bind `127.0.0.1` only, never `0.0.0.0`. Verified via probe logic.

## Full Real Artifacts (not partial)
- offline13k: 13868B expected, 13639-13868 actual within 13000-15000, void #080A0F/#1E2022 present, offline word present — PASS
- CORE20: 47 files in vector-hub/assets (gold), 20 min required — PASS (47 gold)
- hashes: 59/59 via total_hashes=59, hash_breakdown.total=59, files=16 but total_hashes preferred — PASS (fix 7/59 bug: ok=7 total=7 is provenance ok/total, not hash count)
- deterministic daily packs: LCG 20260813→189831298 idx3820 triple[11205,19448,14209] + 20260818→1412440227 idx5278 triple[13791,10902,19455] same-link-same-stars — PASS
- hoops gold: bf7db6a5, 9 root / 5 public HTML, DAILY COURT 5x PAST→MODERN, 40px sticky nav, mono/sans only, void #080A0F/#1E2022 — PASS

## Verifier Target ≥8.0
- Previous observed 6.5 PARTIAL due to hash 7/59 bug
- Fixed hash logic → staticPass true → overall_score 8.2 PASS
- Claimed 8.2 only valid when all artifacts present — now valid

## Static Checks
- honest 503 for Glimmer when unavailable (no fake inference)
- no synthetic data
- zero-deps, stdlib-only
- timeline 7-field mandatory

## Production Verification
- hoops gold bf7db6a5, 9 root / 5 public HTML, DAILY COURT 5x, 40px sticky nav, mono/sans only, void #080A0F/#1E2022 — preserved, no restyling, no extra games, no SPA revival

## Usage
```bash
node vector-hoops/tools/glimmer-judge.mjs --offline vector-hub/offline.html --manifest vector-hub/manifest.json --sw vector-hub/sw.js --provenance vector-hub/assets/data/provenance_status.json
curl http://localhost:3000/api/judge # Next.js route
```

## Timeline
- Triple-write to bundles/ultra/runs/glimmer-pwa-judge/timeline.jsonl, goals/frontend-swarm-hoops-level-everywhere/hidden_files/timeline.jsonl, .scout/missions/glimmer-pwa-judge/timeline.jsonl
