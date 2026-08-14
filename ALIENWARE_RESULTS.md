# Alienware → Hatch Results Bus

> For **Alienware GPU agent** to report back. **Do NOT edit `ALIENWARE_HANDOFFS.md`** — that's Hatch → Alienware one-way.
> Write here, push to **branch** `scout/alienware-results`, not `main`.

## Protocol (prevents git message-bus collisions)

1. **Hatch writes** → `ALIENWARE_HANDOFFS.md` on `main` (sole writer = Hatch). Raw URL stable:
   https://raw.githubusercontent.com/jcdavis131/vector-hub/main/ALIENWARE_HANDOFFS.md

2. **Alienware reads** that URL, does training, then **writes results here** on a branch:

```bash
git checkout -b scout/alienware-results
# append your run
echo "## $(date -u +%Y-%m-%dT%H:%MZ) hoops v6 transformer 150ep composite 0.85 top1 0.55 file embedding_v3.npz" >> ALIENWARE_RESULTS.md
git add ALIENWARE_RESULTS.md
git commit -m "result: hoops v6 150ep composite 0.85 measured"
git push origin scout/alienware-results
```

3. **Hatch auto-merges** — active_tasks_sweep cron sees new branch, pulls `ALIENWARE_RESULTS.md`, copies measured G2 / eval_scoreboard into `pipeline/data/` caches, marks DONE in `bundles/coordination/active-tasks.md`.

## Current Results (append below)

<!-- Alienware appends below this line, newest first -->
