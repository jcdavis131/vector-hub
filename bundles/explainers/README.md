# Explainers — SHAP + LIME per-prediction narrative
Zero-deps true — stdlib JS + python — KernelSHAP approx + LIME tabular perturbation
LCG 20260813→189831298 idx3820 triple[11205,19448,14209] same-link-same-stars

- explainer.js : JS browser + node — explainPrediction(x, names, predFn, opts) → {prediction,baseline,shap_values,lime_values,fidelity,narrative}
- explainer.py : Python stdlib pure — same API
- Audit: vector-*/assets/explainer_audit.json — 10 samples each, fidelity <5e-10 PASS
- UI: lab.html #explainers-shap-lime collapsible Owner/Player/Brand/DFS + bars
- API: /api/predict_explained.js returns {pred,shap,lime,narrative}

Construct validity 2026-08-08 rule: real models ≥2, 5-fold CV, SHAP/permutation, glass-box log.
Everyday language narrative: "projects +2.1 wins above slot because elite rim rate (SHAP +1.3) outweighs age penalty (−0.4, LIME confirms locally)..."
