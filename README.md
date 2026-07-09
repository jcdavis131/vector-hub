# vector-hub

The landing page for **dumbmodel.com** — the arcade for the vector games.

Static. No build step, no dependencies.

| Path | What |
|---|---|
| `index.html` | The whole page |
| `assets/hub.css` | Styles; light + dark via `prefers-color-scheme` |
| `vercel.json` | `www` → apex, plus `/hoops`, `/pitch`, `/gridiron` shortcuts |

## Claims made on this page, and where they come from

Copy here asserts things about the models. Keep it true.

- **17 towers, 48-d embedding, 12,966 player-seasons** — `vector-hoops/assets/mtnn_arch.json`
  (`towerFamilies`, `dEmb`) and `assets/mtnn_meta.json` (`rows`, `dim`).
- **Multi-task heads** (archetype, position, profile reconstruction, salary, playoff
  riser, honors, per-skill towers) — `vector-hoops/pipeline/train_mtnn.py`.
- **Gridiron: shared trunk, 32-d embedding** — `vector-gridiron/pipeline/train_models.py`.
- **Pitch: PCA(3) + k-means(8), no neural net** — `vector-pitch/pipeline/build_vectors.py`.
  Do not describe Pitch as an MTNN. It isn't one.
- **No cross-sport joint embedding exists.** The page frames it as a goal, explicitly
  not shipped. Do not upgrade that to a claim.

Note: `train_mtnn.py`'s docstring says "gated attention fusion (not naive concat)", but
the promoted checkpoint is `mtnn_v5_concat_…` and `mtnn_arch.json` records
`"fusion": "concat"`. The shipped model concatenates. The docstring is stale — the page
deliberately says "fuses" and avoids naming the mechanism.

## Deploy

`vercel --prod`. The apex `dumbmodel.com` must be attached to this project.
