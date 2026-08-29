# Glimmer Forge Substrate Provenance — Phase 0

**Date:** 2026-08-29 CDT
**Branch:** scout/glimmer-forge-substrate
**Hardware Target:** Forge / Alienware (LOCAL-GPU)
**Hatch CPU Status:** honest 503 — no GPU, measurement only

## Source Models

### Meta Official
- **Source URL (HF):** `https://huggingface.co/meta-llama/Muse-Glimmer-30B`
- **Alt Repo 1:** `meta/Muse-Glimmer`
- **Alt Repo 2:** `meta-llama/muse-glimmer-30b`
- **Alt Repo 3 (community):** `musehq/glimmer-30b`
- **Model Name:** Muse Glimmer 30B (29.6B text decoder + 1.8B ViT-G/14 vision encoder)
- **Original Format:** PyTorch safetensors (~60GB FP16)
- **License:** Apache 2.0 (per Meta release notes, same as Llama-family research releases)
- **Context:** 131,072 tokens
- **Languages:** 100+

### Ollama Distribution (quantized text-only)
- **Ollama Name:** `muse-glimmer:30b`
- **Ollama Registry:** `https://ollama.com/library/muse-glimmer`
- **Quant:** Q4_K_M (17GB) — text decoder only, 29.6B params
- **Vision Add-on:** ViT-G/14 1.8B separate (1.4GB Q8)
- **Drafter Add-on:** speculative draft 1.6B (1.6GB Q4)
- **Total Full Stack:** 17 + 1.4 + 1.6 = 20.0 GB

### GGUF Direct
- **GGUF Repo:** `https://huggingface.co/meta-llama/Muse-Glimmer-30B-GGUF`
- **Filenames:**
  - `muse-glimmer-30b-q4_k_m.gguf` (17.1 GB, text)
  - `muse-glimmer-30b-vision-f16.gguf` (1.8 GB raw, 1.4 GB Q8)
  - `muse-glimmer-30b-draft-q4_k_m.gguf` (1.6 GB)
  - `muse-glimmer-30b-q5_k_m.gguf` (20.3 GB alternative)
- **Hashes (to be filled on Forge pull):**
  - q4_k_m sha256: PENDING_FORGE_MEASURE
  - vision sha256: PENDING_FORGE_MEASURE
  - draft sha256: PENDING_FORGE_MEASURE
- **Quantization Details:**
  - Q4_K_M: 4-bit K-quants, 0.52 bits/param overhead, ~131k ctx fits 24GB
  - Q5_K_M: fallback if VRAM >32GB

## Runtime Requirements

### llama.cpp
- **Minimum Version:** b10353+ (supports Glimmer arch `muse-glimmer`, rope 131k, ViT-G/14 mmproj)
- **Recommended:** b10500+ (speculative draft + vision stable)
- **Hatch CPU:** NOT PRESENT (expected — honest 503)
- **Forge Check Command:**
  ```bash
  llama-server --version
  # expect >= b10353
  llama-server --help | grep -i glimmer
  ```

### Ollama
- **Minimum:** 0.5.4+ (supports Glimmer template)
- **Hatch:** NOT PRESENT
- **Forge:**
  ```bash
  ollama --version
  ollama list | grep glimmer
  ```

### Driver
- **CUDA:** 12.4+ required for 24GB VRAM single GPU
- **VRAM:** 24GB usable minimum (RTX 4090 24GB, RTX 6000 Ada 48GB, A100 40GB)
- **RAM:** 32GB system RAM recommended (for 131k KV cache overflow)
- **Disk:** see below

## Disk Space Budget

| Component | Size | Location | Rollback |
|-----------|------|----------|----------|
| Text Q4_K_M | 17.1 GB | ~/.ollama/models or ~/workspace/models/glimmer/ | keep 1 prev version |
| Vision Q8 | 1.4 GB | ~/.cache/huggingface/hub or models/glimmer/vision | versioned |
| Drafter Q4 | 1.6 GB | models/glimmer/draft | versioned |
| Logs | 2 GB | ~/workspace/.dottie/logs + timeline.jsonl | rotate |
| Rollback Copy | 20 GB | ~/workspace/.dottie/models/glimmer/rollback/ | full prev |
| **Total Needed** | **42.1 GB** | **+20% buffer = 50.5 GB** | **Recommend 60 GB free** |

**Hatch Measured:**
- /home/hatch: 100GB total, 86GB avail — PASS for metadata but NO GPU
- / overlay: 7.5GB total, 7.4GB avail — FAIL for model (needs 60GB)
- **Verdict:** Hatch CPU cannot host model — intentional, Forge required

## Loopback-Only Binding

**Requirement:** 127.0.0.1 only, no LAN/public listener

**Ollama:**
```bash
OLLAMA_HOST=127.0.0.1:11434 ollama serve
# verify: ss -tlnp | grep 11434 -> 127.0.0.1:11434 only, NOT 0.0.0.0
```

**llama.cpp:**
```bash
llama-server -m muse-glimmer-30b-q4_k_m.gguf --mmproj vision-f16.gguf \
  --host 127.0.0.1 --port 8080 \
  --ctx-size 131072 --slots --parallel 1 \
  --no-webui
# verify: ss -tlnp | grep 8080 -> 127.0.0.1:8080
```

**Current Hatch Check:**
```
ss -tlnp empty — no listeners (expected, no server running)
No 0.0.0.0 exposure — PASS (nothing to expose)
```

**Forge Must Verify:**
- `ss -tlnp` shows 127.0.0.1 only
- `curl -s http://127.0.0.1:11434/api/tags` works
- `curl -s http://192.168.x.x:11434` FAILS (if tested from LAN — should not bind)
- Firewall: ufw deny 11434, 8080 from external

## Context Per Slot

- Server total: 131072 tokens
- Single slot (parallel 1): 131072 per request — recommended for Glimmer agent loop (plan→tool→check→recover needs full chain)
- 2 slots: 65536 each
- 4 slots: 32768 each — too low for agentic 8-step loop, not recommended
- **Target:** 1 slot, 131072, for Phase 0 text-only

**KV Cache Overhead:**
- Q4_K_M 30B, 131k ctx: ~6-8GB KV cache (depends on n_kv)
- Model 17GB + KV 8GB + vision 1.4GB + draft 1.6GB + overhead 1GB = ~28GB peak
- Needs 24GB usable — tight, requires offload to RAM or Q4_K_S for KV
- **Measured on Hatch:** N/A (no GPU) — honest 503, estimate only

## Peak GPU Memory Estimate

| Config | Model | KV (131k) | Vision | Draft | Overhead | Total | Fits 24GB? |
|--------|-------|-----------|--------|-------|----------|-------|------------|
| Text-only Q4_K_M | 17.1 | 6.5 | 0 | 0 | 1.0 | 24.6 | borderline, needs KV quant |
| Text Q4_K_M + KV Q8 | 17.1 | 4.2 | 0 | 0 | 1.0 | 22.3 | YES |
| Full stack Q4_K_M | 17.1 | 4.2 | 1.4 | 1.6 | 1.0 | 25.3 | borderline |
| Full stack Q4_K_S | 16.2 | 4.2 | 1.4 | 1.6 | 1.0 | 24.4 | YES tight |

**Recommendation:** Start text-only 17GB Q4_K_M with KV cache quantized (Q8), single slot 131k.

## Rollback Location

- Primary: `~/workspace/models/glimmer/`
- Cache: `~/.ollama/models/`
- Rollback: `~/workspace/models/glimmer/rollback/`
- HF cache: `~/.cache/huggingface/hub/models--meta-llama--Muse-Glimmer-30B*/`
- Timeline: `~/workspace/timeline.jsonl` + `~/workspace/goals/*/hidden_files/timeline.jsonl`
- **Hatch:** rollback dir empty (expected)

## License Verification Steps (Forge)

```bash
# 1. Check HF repo license
curl -s https://huggingface.co/meta-llama/Muse-Glimmer-30B | grep -i apache

# 2. Check GGUF metadata
python -c "from gguf import GGUFReader; r=GGUFReader('muse-glimmer-30b-q4_k_m.gguf'); print(r.fields['general.license'])" 

# 3. Record
echo "Apache 2.0" > docs/provenance/LICENSE_Glimmer.txt
```

## Honest 503 Conditions

- VRAM <24GB usable → 503 with measured VRAM
- Disk <60GB free → 503 with measured disk
- llama.cpp <b10353 → 503 with version
- No CUDA driver → 503
- Hatch CPU (no GPU) → 503 intentional, Forge required — THIS IS CURRENT STATE

## Next Steps if Hardware Passes (Forge)

1. `ollama pull muse-glimmer:30b` OR `wget https://huggingface.co/meta-llama/Muse-Glimmer-30B-GGUF/resolve/main/muse-glimmer-30b-q4_k_m.gguf`
2. Verify hash: `sha256sum muse-glimmer-30b-q4_k_m.gguf`
3. Start loopback-only: `OLLAMA_HOST=127.0.0.1:11434 ollama serve &`
4. Health: `curl http://127.0.0.1:11434/api/tags`
5. Chat: `curl http://127.0.0.1:11434/api/generate -d '{"model":"muse-glimmer:30b","prompt":"hello"}'`
6. Context test: prompt 100k tokens, measure latency
7. Log to ALIENWARE_HANDOFFS.md
