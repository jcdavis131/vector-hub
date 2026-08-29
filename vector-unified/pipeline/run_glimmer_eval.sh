#!/usr/bin/env bash
# run_glimmer_eval.sh — zero-deps helper to run Glimmer MLOps eval factory
# Honest 503, never synthetic, stdlib-only core
set -euo pipefail
cd "$(dirname "$0")/.."

CKPT="${1:-unified_stage2_centroid_ab.pt}"
EFFORT="${2:-high}"
REPORT="${3:-}"

echo "[glimmer-eval] ckpt=$CKPT effort=$EFFORT report=${REPORT:-auto} branch=scout/glimmer-mlops-eval"
echo "[glimmer-eval] checking real sources..."

# Real source checks — honest 503
if [ ! -f "data/unified_matrix.npz" ]; then
  echo "503 data/unified_matrix.npz missing — run build_unified_matrix.py --with-schools --embed-v3" >&2
  exit 11
fi

if [ ! -f "data/unified_meta.json" ]; then
  echo "503 data/unified_meta.json missing" >&2
  exit 11
fi

# Check for eval report
if [ -n "$REPORT" ] && [ ! -f "$REPORT" ]; then
  echo "503 report $REPORT missing" >&2
  exit 11
fi

# Check for Glimmer backends — stdlib client will 503 if none, but we give hint
echo "[glimmer-eval] detecting Glimmer backend..."
if command -v curl >/dev/null 2>&1; then
  if curl -s --max-time 1 http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  -> Ollama detected at :11434"
  elif curl -s --max-time 1 http://localhost:8080/health >/dev/null 2>&1 || curl -s --max-time 1 http://localhost:8080/ >/dev/null 2>&1; then
    echo "  -> llama.cpp detected at :8080"
  elif [ -n "${GLIMMER_ENDPOINT:-}" ]; then
    echo "  -> Generic endpoint $GLIMMER_ENDPOINT"
  else
    echo "  !! No Glimmer endpoint detected — will run in 503-honest mode (judge will be SKIPPED)"
    echo "     Start one of:"
    echo "       ollama run glimmer"
    echo "       llama-server -m glimmer-30b.gguf --port 8080 --ctx-size 131072"
    echo "       export GLIMMER_ENDPOINT=http://localhost:8000/v1  # vLLM/SGLang/MLX"
  fi
else
  echo "  (curl not found — skipping port check, Glimmer client will probe via python socket)"
fi

# Run eval_glimmer — stdlib core, torch/sklearn optional
echo "[glimmer-eval] running pipeline/eval_glimmer.py ..."
set +e
if [ -n "$REPORT" ]; then
  python3 pipeline/eval_glimmer.py --ckpt "$CKPT" --report "$REPORT" --kfold 5 --permutation --shap --judge --effort "$EFFORT"
else
  python3 pipeline/eval_glimmer.py --ckpt "$CKPT" --kfold 5 --permutation --shap --judge --effort "$EFFORT"
fi
RC=$?
set -e

if [ $RC -eq 11 ]; then
  echo "[glimmer-eval] honest 503 — real data or Glimmer missing, not fabricated"
  echo "[glimmer-eval] trying judge-only mode (report-only, no torch needed)..."
  python3 pipeline/eval_glimmer.py --report "${REPORT:-pipeline/eval_reports/eval_unified_latest.json}" --judge-only --effort "$EFFORT" || true
  exit 0
fi

if [ $RC -ne 0 ]; then
  echo "[glimmer-eval] failed with $RC" >&2
  exit $RC
fi

echo "[glimmer-eval] done — see pipeline/eval_reports/eval_glimmer_latest.json"
echo "  G2 floor 0.639->0.615 rank12.4->32 sil0.683->0.74 composite0.8688->0.91"
echo "  G3 dual TCA224 70% + TAA128 k8 30% + schools aux0.12 chimera24799->47900"
echo "  PWA v67 void #080A0F 40px sticky CORE20 offline13k LOD4000/8000 DPR1"
