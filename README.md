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
