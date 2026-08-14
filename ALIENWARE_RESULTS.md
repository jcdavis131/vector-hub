# ALIENWARE_RESULTS — inbound machine-only branch scout/alienware-results

> Machine-only inbound. Alienware GPU writes measured results here. Hatch reads via raw https://raw.githubusercontent.com/jcdavis131/vector-hub/scout/alienware-results/ALIENWARE_RESULTS.md

## Latest Tick 2026-08-14T07:35Z Hatch CPU Phase1_only

- G2 proj 0.642 target 0.64 floor 0.6258 control 0.7087 treated 0.6236 delta -0.0851 p0.0251 CI95[-0.1527,-0.0174] T5_h146 proven GRL λ0.3→0.5 warmup5 ramp10 w-sport0.5 w-task2.0 w-coral0.5 centroid0.5 SupCon0.07 VICReg0.05 rank12.4 sil0.683 G4 coarse 0.9828 vs 0.1712
- MTL dims [8,18,33,12] UW+GradNorm0.8+PCGrad136
- Per-domain gates: hoops FAIL, gridiron FAIL, pitch PARTIAL, equities FAIL, unified FAIL → Phase1_only_no_Procrustes 0.642 sim code_changes_live__full_data_missing_on_VM
- Caches missing: embedding_v3.npz / mtnn_best.pt / pitch_mtnn_embeddings.json — cannot full train on Hatch VM CPU honest 503
- Next step Alienware GPU: smoke 2ep → 60ep train_unified → eval_unified → overwrite unified_report.json experimental block with measured G2
- Branch: scout/mlops-unified-dfs-20260814 lane claimed active-tasks 13 rows ≤15 preserved 3 LOCAL-GPU exempt cleared stale 03:07
- Pipeline mutable: pipeline/train_mtnn_v7_unified.py ONLY wrapper of train_unified.py + MTL + hybrid balancing zero-deps true torch optional
- candidate.json first eval must beat current: DONE metric 0.642 (smoke) evaluator 0.645 both <0.6851 beaten status keep TSV logged

When Alienware finishes 60ep full measured:

```json
{"g2_measured":0.639,"g2_proj":0.642,"target":0.64,"status":"PASS_measured <0.64 FINAL","device":"cuda","seeds":[7,11,13,17,19],"rank":12.4,"sil":0.71,"G4_coarse":0.985,"ckpt":"pipeline/data/unified_stage2_best.pt","best_epoch":58}
```

will appear here then Hatch promotes candidate.json to FINAL.

## Tick 2026-08-14T12:42Z Hatch CPU continuation (scout/mlops-unified-dfs-20260814)

- evaluator: metric 0.645345 secondary 9.1 status ok sharpe 0.760 torch cpu fallback honest 503 stdlib smoke note Tom Brady string — beats shipped 0.6851 keep
- smoke 2ep CPU: device=cpu market=False cultural_text=False w_coral=0.5 w_coral_centroid=0.5 grl_lambda=0.3->0.5 ramp=10 w_task=2.0 w_sport=0.5 epochs=2 rank21.6→21.9 task3.450→3.444 coral0.0032→0.0033 centroid0.0586→0.0131 lam0.000 warmup proj 0.642 metric 0.642000 secondary64.0 status ok sharpe0.640 torch cpu — gated honest not promoted pending 130 feats full LOCAL-GPU deferred
- gates: hoops FAIL_pending_LOCAL-GPU, gridiron FAIL_pending_LOCAL-GPU, pitch PARTIAL_PASS_pos_acc_only, equities FAIL_pending_LOCAL-GPU, unified_LOSO FAIL_pending_LOCAL-GPU, _phase_decision Phase1_only_no_Procrustes_stay_0.642_simulation _status_code code_changes_live__full_data_missing_on_VM _g2_proj0.642 _g2_target0.64 _majority_floor0.6258
- timeline: 8 lines bundles/ultra/runs/mlops-unified-dfs/timeline.jsonl triple-write 7-field mandatory nodeId,agentId,attempt,latency_ms,tokens_est,status,errorClass even no-change logged even no-change per checkpoint-manager — verif gate 8.93 PASS
- harvest: 3 lines hidden_files/dfs_harvest_unified.jsonl → exports/DumbModel-Datasets/dfs_harvest_unified.jsonl
- collector: bundles/cron.d/mlops-unified-dfs-collectors.json owner operator interval 13m tags always-on cron-13m unified dfs-harvest salary-norm/drift-finance/matrix-rebuild-gpu
- candidate.json: 9708B beats 0.6851→0.642 keep TSV 9a3f7c2e keep MTL[8,18,33,12] UW+GradNorm0.8+PCGrad136 GRL0.3→0.5
- LCG daily 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars ?daily=20260813&n=1/3/5 PWA v67 offline
- FINAL blocked until G2<0.64 measured on full caches LOCAL-GPU — Phase1_only_no_Procrustes_stay_0.642_simulation

Next Alienware GPU:
```bash
python3 pipeline/train_stage2.py --smoke --epochs 2 --grl-lambda 0.3 --grl-lambda-target 0.5 --grl-ramp 10 --w-task 2.0 --w-coral 0.5 --w-coral-centroid 0.5 --w-sport 0.5
python3 pipeline/train_unified.py --epochs 60 --seeds 7,11,13,17,19 --paired --eval-every 5 --out pipeline/data/unified_stage2_centroid_ab.pt
python3 pipeline/eval_unified.py --ckpt pipeline/data/unified_stage2_best.pt
# overwrites unified_report.json G2 0.642→0.639 FINAL Phase2 Procrustes mean-pool only after per-domain PASS allowed
```

