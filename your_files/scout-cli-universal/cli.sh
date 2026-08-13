#!/usr/bin/env bash
# bundles/cli.sh — single-source CLI shim so any Hatch agent/harness can call scout as one entrypoint.
# v3.3 universal SOTA — tries scout_cli_shim_v3.py OODA-Agentic-MoMA-Graph-Checkpoint first, falls back to bigbang.cli
# Also exposes ACNE contacts + GARNet relevantAgents + dev-scout-api
# Wraps `python3 scout_cli_shim_v3.py "$@"` from bundles/dev-api/ universal shim
# Resolves dottie root via sibling: ~/workspace/dottie/apps/scout-cli pip -e installed fallback
# Usage: bundles/cli.sh --json harness route "compare Stripe vs Lemon Squeezy Aug 2026"
#        bundles/cli.sh --json vector eval hoops
#        bundles/cli.sh contacts stats
#        bundles/cli.sh doctor
# Any harness agent can call this path without knowing pip/virtualenv details.
# LCG 20260813→189831298 idx3820 triple [11205,19448,14209] PWA v67 #080A0F CORE20 void dark free forever Knowledge→Edge→Money
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$HOME/workspace/dottie/apps/scout-cli" ]; then
  export PYTHONPATH="$HOME/workspace/dottie/apps/scout-cli${PYTHONPATH:+:$PYTHONPATH}"
fi
# prefer new shim v3.3 universal SOTA — OODA-Agentic-MoMA-Graph-Checkpoint + MoMA-lite 5 tiers + GARNet Map24 max3/4 pacing :01 ultra
if [ -f "$SCRIPT_DIR/dev-api/scout_cli_shim_v3.py" ]; then
  exec python3 "$SCRIPT_DIR/dev-api/scout_cli_shim_v3.py" "$@"
fi
if [ -f "$HOME/workspace/bundles/dev-api/scout_cli_shim_v3.py" ]; then
  exec python3 "$HOME/workspace/bundles/dev-api/scout_cli_shim_v3.py" "$@"
fi
# fallback classic bigbang discovery
exec python3 -m bigbang.cli "$@"
