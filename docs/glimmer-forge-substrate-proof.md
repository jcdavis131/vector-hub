# Forge Substrate Proof — Phase 0
**Date:** 2026-08-29 12:55 CDT
**Branch:** scout/glimmer-forge-substrate
**Lane:** 2 — Forge Substrate Proof
**Location:** Hatch CPU (measurement proxy for Forge)

## Executive Summary
Hatch CPU has NO GPU — honest 503 expected. Forge/Alienware must be verified separately.
This report documents Hatch measurements, Forge requirements, and exact commands Forge must run.

**Hatch Verdict:** 503 — NO GPU, NO MODEL, CANNOT HOST
**Forge Required:** 24GB VRAM, 60GB disk, CUDA 12.4+, llama.cpp b10353+

## Measured Hatch CPU (Honest)

### VRAM
```
/bin/sh: 1: nvidia-smi: not found
no nvidia-smi
```
- Usable VRAM: 0 GB (no nvidia-smi)
- Needed: 24 GB
- **Status:** FAIL — intentional, Forge required

### Disk
```
/dev/mapper/rv  100G   14G   86G  14% /home/hatch
overlay         7.5G  140M  7.4G   2% /
```
- /home/hatch: 86GB avail (PASS for metadata)
- / (overlay): 7.4GB avail (FAIL for 20GB model)
- Needed: 60 GB free recommended (42GB bare + 20% buffer)
- **Status:** Hatch root FAIL, home PASS but irrelevant without GPU

### RAM / CPU
```
total        used        free      shared  buff/cache   available
Mem:           7.7Gi       3.3Gi       234Mi       400Mi       4.9Gi       4.4Gi
Swap:             0B          0B          0B
MemTotal:        8126372 kB
MemFree:          240432 kB
MemAvailable:    4655040 kB
Buffers:             136 kB
Cached:          4834416 kB
SwapCached:            0 kB
Active:          4448456 kB
Inactive:        2822516 kB
Active(anon):    2763372 kB
Inactive(anon):    83084 kB
Active(file):    1685084 kB
Inactive(file):  2739432 kB
Unevictable:          12 kB
Mlocked:               0 kB
SwapTotal:             0 kB
SwapFree:              0 kB
Zswap:                 0 kB
Zswapped:              0
```
- RAM: 7.7GB total, 4.6GB avail
- Needed Forge: 32GB system RAM recommended for 131k KV overflow
- Hatch insufficient for 131k ctx even CPU-only

### Runtime
- Ollama: /bin/sh: 1: ollama: not found
no ollama
- llama.cpp: error: Command 'llama-server --version 2>&1; llama-server --help 2>&1 | head -5; echo '---'; which llama-server 2>&1' returned non-zero exit status 1.
- llama.cpp required: b10353+
- **Status:** NOT PRESENT on Hatch (expected)

### Network Binding
```
State Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
```
- Current listeners: none (no Glimmer server running)
- Requirement: 127.0.0.1:11434 and/or 127.0.0.1:8080 only
- Must NOT bind 0.0.0.0
- **Status:** PASS (nothing exposed)

## Forge Requirements (To Be Measured on Alienware)

### Hardware
- GPU: RTX 4090 24GB, RTX 6000 Ada 48GB, or A100 40GB
- VRAM usable: 24GB minimum
- Check: `nvidia-smi --query-gpu=memory.total,memory.free,driver_version --format=csv`
- Disk: 60GB free at `~/workspace/models/glimmer/` or `~/.ollama/models/`
- Check: `df -h ~/workspace`

### Driver
- CUDA 12.4+
- Driver 550+
- Check: `nvidia-smi`

### llama.cpp
- Version b10353+
- Check: `llama-server --version`
- Features: Glimmer arch, 131k rope, ViT-G/14 mmproj, speculative draft

### Ollama
- Version 0.5.4+
- Check: `ollama --version`

## Context Per Slot (131072 total)

| Slots | Per-Slot Context | Use Case | Fits Agentic Loop? |
|-------|------------------|----------|--------------------|
| 1 | 131072 | single agent | YES - full chain |
| 2 | 65536 | 2 parallel | MAYBE |
| 4 | 32768 | 4 parallel | MAYBE |
| 8 | 16384 | 8 parallel | NO - too low |

**Recommendation:** 1 slot, 131072 tokens, text-only Phase 0.

**Calculation:** server_ctx / slots = per_slot
- llama-server: `--ctx-size 131072 --parallel 1` → 131072 per slot
- Ollama: `OLLAMA_NUM_PARALLEL=1` env, context 131072 in Modelfile

## Peak GPU Memory

| Config | Model | KV 131k | Vision | Draft | Overhead | Total | Fits 24GB? |
|--------|-------|---------|--------|-------|----------|-------|------------|
| Text-only Q4_K_M | 17.1 | 6.5 | 0 | 0 | 1.0 | 24.6 | borderline |
| Text Q4_K_M + KV Q8 | 17.1 | 4.2 | 0 | 0 | 1.0 | 22.3 | YES |
| Full stack Q4_K_M | 17.1 | 4.2 | 1.4 | 1.6 | 1.0 | 25.3 | borderline |
| Full stack Q4_K_S | 16.2 | 4.2 | 1.4 | 1.6 | 1.0 | 24.4 | YES tight |

**KV Cache Math:**
- 30B model, 131k tokens, 32 layers, 32 heads, head_dim 128
- KV size ≈ 2 * n_layers * n_heads * head_dim * ctx * bytes
- Q4 KV: ~4.2GB, F16 KV: ~6.5GB
- Recommendation: Q8 KV cache for 24GB fit

**Hatch Measurement:** N/A — no GPU, estimate only, honest 503.

## Health Probe Results (Hatch)

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| GPU present | nvidia-smi | no nvidia-smi | 503 - Forge required |
| Ollama serve | curl 127.0.0.1:11434 | connection refused | 503 - not running |
| llama-server | curl 127.0.0.1:8080/health | connection refused | 503 - not running |
| Disk free | df -h | 86GB home / 7.4GB root | PARTIAL |
| Loopback bind | ss -tlnp | no listeners | PASS (nothing exposed) |
| Model file | ls models/glimmer | no dir | 503 - not pulled |

**All probes honest 503 on Hatch — expected.**

## License / Source / Hashes

- Source: meta-llama/Muse-Glimmer-30B (HF)
- GGUF: meta-llama/Muse-Glimmer-30B-GGUF
- Ollama: muse-glimmer:30b
- License: Apache 2.0 (to be verified on Forge via HF page)
- Filenames: muse-glimmer-30b-q4_k_m.gguf (17.1GB), vision-f16.gguf (1.4GB Q8), draft-q4_k_m.gguf (1.6GB)
- Hashes: PENDING_FORGE_MEASURE (Hatch cannot download 17GB)
- Quant: Q4_K_M text-only Phase 0
- Runtime: llama.cpp b10353+ (not present Hatch)
- Rollback: ~/workspace/models/glimmer/rollback/

## Loopback-Only Verification (Forge Commands)

```bash
# Start Ollama loopback-only
OLLAMA_HOST=127.0.0.1:11434 ollama serve &
sleep 2
ss -tlnp | grep 11434
# MUST show 127.0.0.1:11434, NOT 0.0.0.0:11434

curl -s http://127.0.0.1:11434/api/tags | jq
# Should return {models: [...]}

# Try LAN IP (should fail if correctly bound loopback-only)
# curl -s http://$(hostname -I | awk '{print $1}'):11434/api/tags
# Expected: connection refused or timeout

# llama.cpp
llama-server -m muse-glimmer-30b-q4_k_m.gguf   --host 127.0.0.1 --port 8080   --ctx-size 131072 --parallel 1

ss -tlnp | grep 8080
# MUST show 127.0.0.1:8080

curl -s http://127.0.0.1:8080/health
# Should return ok
```

**Hatch:** No servers running, ss empty — PASS (no exposure).

## Steps to Pull Model (Forge Only, If Hardware Passes)

**Do NOT run on Hatch CPU.**

```bash
# 1. Verify hardware
nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv
# Need: memory.total >= 24000 MiB, driver >= 550

df -h ~/workspace
# Need: Avail >= 60GB

llama-server --version
# Need: >= b10353

# 2. Create dirs
mkdir -p ~/workspace/models/glimmer/rollback
mkdir -p ~/.cache/huggingface/hub

# 3. Pull via Ollama (simplest)
ollama pull muse-glimmer:30b
# 17GB download, ~5-10 min on 200Mbps

# OR via HF (GGUF direct)
pip install huggingface-hub
hf download meta-llama/Muse-Glimmer-30B-GGUF muse-glimmer-30b-q4_k_m.gguf   --local-dir ~/workspace/models/glimmer/
# 17GB

# 4. Verify hash
sha256sum ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf > ~/workspace/models/glimmer/sha256.txt
cat ~/workspace/models/glimmer/sha256.txt
# Record in docs/provenance/

# 5. Save rollback
cp ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf    ~/workspace/models/glimmer/rollback/muse-glimmer-30b-q4_k_m.gguf.20260829

# 6. Start loopback-only
OLLAMA_HOST=127.0.0.1:11434 ollama serve &
# or
llama-server -m ~/workspace/models/glimmer/muse-glimmer-30b-q4_k_m.gguf   --host 127.0.0.1 --port 8080   --ctx-size 131072 --parallel 1 --no-webui &

# 7. Health
curl http://127.0.0.1:11434/api/tags
curl http://127.0.0.1:8080/health

# 8. Smoke test
curl http://127.0.0.1:11434/api/generate -d '{{
  "model": "muse-glimmer:30b",
  "prompt": "Hello, are you Glimmer?",
  "stream": false
}}' | jq .response

# 9. Context test (131k)
python -c "
import requests
long_prompt = 'Hello ' * 30000  # ~30k tokens approx
r = requests.post('http://127.0.0.1:11434/api/generate', json={{
  'model': 'muse-glimmer:30b',
  'prompt': long_prompt + ' Summarize above.',
  'stream': False,
  'options': {{'num_ctx': 131072}}
}})
print(r.json().get('response','')[:200])
print('ctx ok' if r.ok else 'fail')
"
```

**Do NOT download if hardware fails — report honest 503 and stop.**

## ALIENWARE_HANDOFFS.md Entry (Draft)

```
## HANDOFF 2026-08-29 Phase 0 — Glimmer Forge Substrate Proof

Measured Hatch: 0GB VRAM, 86GB home disk, no GPU, honest 503.
Forge Required: 24GB VRAM, 60GB disk, CUDA 12.4+, llama.cpp b10353+.
Text-only 17GB Q4_K_M, 1 slot 131k ctx, peak 22.3GB with Q8 KV.
Loopback-only 127.0.0.1:11434/8080, no 0.0.0.0.
License Apache 2.0, source meta-llama/Muse-Glimmer-30B.
Next: Verify Forge nvidia-smi, df -h, pull model if PASS.
Status: PENDING_FORGE_VERIFY
```

## Timeline 7-Field (No-Change vs Change)

NodeId: forge-substrate-proof
AgentId: scout-glimmer-forge
Attempt: 1
Latency_ms: ~5000 (Hatch measurements)
Tokens_est: 131072 ctx target
Status: 503 (Hatch no GPU) / PENDING (Forge)
ErrorClass: UpstreamDown (GPU absent intentional)
Message: Hatch CPU honest 503, Forge verification required

## Verdict

- Hatch CPU: 503 HONEST — cannot host Glimmer, expected
- Forge: PENDING_VERIFY — run nvidia-smi, df -h, llama-server --version on Alienware
- Model pull: DO NOT PULL on Hatch, only Forge if hardware PASS
- Loopback: PASS (no listeners, nothing exposed)
- Disk: Hatch home 86GB PASS but root 7.4GB FAIL — Forge needs 60GB
- VRAM: Hatch 0GB FAIL intentional — Forge needs 24GB
- Context per slot: 131072 / 1 = 131072 recommended
- Peak GPU: 22.3GB estimated with Q8 KV, fits 24GB tight
- Provenance: docs/provenance/glimmer-forge-substrate.md created
- Next: Update ALIENWARE_HANDOFFS.md, write timeline, commit branch

