# Active Tasks - Who's touching what

> One file, one truth. Write your claim BEFORE you edit, clear it when done.
> Format: | Agent | Repo / Area | Since (CT) | What / Why | Branch | Status |

| Agent | Repo / Area | Since | What / Why | Branch | Status |
|-------|-------------|-------|------------|--------|--------|
| Claude-Local | vector-hub / provenance checksums | 17:1x CDT | FREE-lane half only. scout_cli.json's source_hashes contains NO hashes — file sizes (4.6K) and version strings (v3.3-OODA-...) — and covers 6 of 11 source_files. DONE — scripts/check_provenance_hashes.py + audit. 3 arms (COVERAGE/SHAPE/TRUTH). Found 6 malformed + 5 uncovered on scout_cli.json AND 5 hash MISMATCHES across gridiron/equities/unified. NOT fixed: scout_cli is Scout's and its 6 values are all bundles/* which this box cannot resolve; the 5 mismatches need the page extractor re-run, which replaces live content = operator action. | local/hub-provenance | done |
| Scout | vector-hoops / MTNN v6 fusion | 22:08 CDT | Port transformer fusion + SupCon/VICReg, lift composite 0.7937→0.85 | scout/hoops-v6-fusion | in-progress |
| Scout | vector-gridiron / training pipeline | 22:08 CDT | Bring training in-repo, fix 16-d vs 32-d vs 64-d confusion | scout/gridiron-train-in-repo | in-progress |
| Scout | vector-unified + vector-hub | 22:08 CDT | Push G2 sport-blind 0.685→0.64, verify ablation table | scout/unified-g2-blind | in-progress |
| Scout | dottie / nano 1k + tech debt | 22:08 CDT | First real nano 1k steps, scrub cache, unify checkpoint paths | scout/dottie-nano-1k | in-progress |

## How to use
1. Add your row before editing
2. Keep main green - work on your own branch, PR or fast-forward only when tests pass
3. New assets = candidate.json -> promote only when eval beats current + gate passes
4. Log even if no change ("checked, no-op") so others know you looked
5. Clear row when done

## Free lanes right now
- vector-pitch / MTNN to game + difficulty retune (rank 1 hill-climb)
- vector-equities / v6_real README sync 0.174→0.7057 + forward IC eval
- vector-hub / daily 5th puzzle (unified chimera) + provenance checksums
- dottie / distilled reasoning optimizer traces→nano GRPO
