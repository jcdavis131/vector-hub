# vector-hub

The landing page for **dumbmodel.com** — the arcade for the vector games.

Static. No build step, no dependencies.

| Path | What |
|---|---|
| `index.html` | The whole page |
| `assets/hub.css` | Neobrutalist styles aligned with the vector-games family (paper/ink, 2px borders, hard block shadows, orange/blue/purple data accents) — light only |
| `assets/hub.js` | Scroll-spy nav highlight (vanilla, no deps) |
| `vercel.json` | `www` → apex, plus `/hoops`, `/pitch`, `/gridiron` shortcuts |

The visual system mirrors the vector games themselves (`vector-hoops`/`-gridiron`/`-pitch`):
paper-white `#fafaf8` + near-black `#111` ink, 2px ink borders with hard
`4px 4px 0` block shadows, 10px radius, bold uppercase mono labels, and color
reserved for data — orange = Hoops, blue = Gridiron, purple = Pitch. The chrome
(`.site-nav`, `.site-footer`, `.vh-card`, `.vh-btn`, `landing-*`, `mode-card`,
`how-steps`, `credibility-strip`) reuses the games' token names and primitives so
the hub reads as part of the same family. Light only — the games are light only.

## Claims made on this page, and where they come from

Copy here asserts things about the models. Keep it true.

- **17 towers, 48-d embedding, 12,966 player-seasons** — `vector-hoops/assets/mtnn_arch.json`
  (`towerFamilies`, `dEmb`) and `assets/mtnn_meta.json` (`rows`, `dim`).
- **Multi-task heads** (archetype, position, profile reconstruction, salary, playoff
  riser, honors, per-skill towers) — `vector-hoops/pipeline/train_mtnn.py`.
- **Gridiron: shared trunk, 32-d embedding** — `vector-gridiron/pipeline/train_models.py`.
- **Pitch: MTNN 24-d (SupCon v1.1) additive export** — `vector-pitch/pipeline/train_mtnn.py`
  + `assets/pitch_mtnn_embeddings.json`. Live daily game board still PCA(3)+k-means via
  `build_vectors.py` / `assets/vectors.json` until the UI swaps.
- **Cross-sport joint embedding shipped (v0.1+)** — `vector-unified/assets/unified.json`
  (20,721 player-seasons × 64-d). G1/G3/G4 PASS; G2 sport-invariance deferred.
  Hub copy: shipped-with-caveats, not a joint daily puzzle yet.

Note: `train_mtnn.py`'s docstring says "gated attention fusion (not naive concat)", but
the promoted checkpoint is `mtnn_v5_concat_…` and `mtnn_arch.json` records
`"fusion": "concat"`. The shipped model concatenates. The docstring is stale — the page
deliberately says "fuses" and avoids naming the mechanism.

## Deploy

`vercel --prod`. The apex `dumbmodel.com` must be attached to this project.
