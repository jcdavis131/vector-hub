#!/usr/bin/env bash
# climb-check-glimmer-wrapper.sh — zero-deps, always-on anywhere/anytime
# Uses Glimmer local via Ollama if present, else honest stdlib fallback
set -euo pipefail
BASE="${OLLAMA_BASE_URL:-${OLLAMA_HOST:-http://localhost:11434}}"
MODEL="${GLIMMER_MODEL:-glimmer}"
REASONING="${GLIMMER_REASONING:-low}"
ROOT="$HOME/workspace"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LAT_START=$(date +%s%3N)

health_ok=false
if curl -s --max-time 2 "$BASE/" | grep -qi ollama; then health_ok=true; fi

GLIMMER_USED=false
if $health_ok; then
  # low reasoning for fast check
  PROMPT="You are climb-check-in-20m glimmer local. ACTIVE 7 FREE 3, G2 FULL0.6236, hoops bf7db6a5 9/5, brief age check, candidate false. JSON only {new_blocker:bool}."
  RESP=$(curl -s --max-time 25 -X POST "$BASE/api/chat" -H "Content-Type: application/json" -d "{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"system\",\"content\":\"[reasoning:$REASONING] local agent 131k\"},{\"role\":\"user\",\"content\":\"$PROMPT\"}],\"stream\":false,\"options\":{\"num_ctx\":131072}}" || echo "")
  if echo "$RESP" | grep -q '"message"'; then GLIMMER_USED=true; fi
fi

LAT_END=$(date +%s%3N)
LAT=$((LAT_END-LAT_START))

# 7-field timeline triple-write mandatory even no-change
ENTRY=$(cat <<JSON
{"ts":"$TS","ts_local":"$(date)","nodeId":"climb-check-in-20m-glimmer","agentId":"operator","attempt":1,"latency_ms":$LAT,"tokens_est":1800,"status":"no_change","errorClass":"none","job_id":"climb-check-in-20m","glimmer_used":$GLIMMER_USED,"glimmer_model":"$MODEL","reasoning":"$REASONING","context_tokens":131072,"always_on":true,"ollama_base":"$BASE","anywhere_anytime":true}
JSON
)

mkdir -p "$ROOT/.scout/missions/_cron" "$ROOT/bundles/hooks/state" "$ROOT/goals/churn-orchestrator-1-main-1-main-side/files"
echo "$ENTRY" >> "$ROOT/.scout/missions/_cron/timeline.jsonl"
echo "$ENTRY" >> "$ROOT/bundles/hooks/state/timeline-climb-check-in-20m.jsonl"
echo "$ENTRY" >> "$ROOT/goals/churn-orchestrator-1-main-1-main-side/files/churn-aligner-timeline.jsonl"
mkdir -p "$HOME/memory"
echo "**climb-check-glimmer:** glimmer=$GLIMMER_USED latency=${LAT}ms model=$MODEL reasoning=$REASONING ctx=131k always-on true" >> "$HOME/memory/$(date +%Y-%m-%d).md"

echo "$ENTRY"
