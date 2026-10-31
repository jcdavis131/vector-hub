# arxiviq.com Embedding Atlas — "Living Field" Critical Review, PRD, SPEC

**Status:** DRAFT for owner review. Nothing here touches the live atlas.
**Scope:** UX track only. Data pipeline, feeds, and the model program are out of scope.
**Vintage:** 2026-10-31. Figures quoted from the brief: ~410,000 entities, ~37,000 edges, ~129 MB, 64-d MTNN v5 serving; JEPA primary + contrastive twin auxiliary in training.

> **Review basis.** The UX mandala (`~/workspace/atlas-ux/HARADA.md`) and the `groundtruth` repo (`apps/map`) were not reachable from this session. This review is against the eight component names and the Living Field description in the brief, plus the standing constraints. Anything the mandala already settles that contradicts a default below: the mandala wins, and the owner should strike the item here.

---

## 0. Verdict in one paragraph

Living Field is buildable by a small team **only if "living" is redefined as "responds" rather than "idles."** As written, three parts of the direction contradict the standing constraints: (1) *drift and re-cluster on filter* either lies about the embedding or requires runtime layout that cannot hold 60 fps on a phone; (2) *spring physics pulling a neighborhood into focus* moves dots away from their true positions, which breaks "every number carries provenance"; (3) *geography as a ghost layer underneath* has no shared coordinate frame with an embedding projection, so the ghost is noise unless it is a second frame the user can morph to. Each has a concrete fix below, and the fixes also resolve the O'Gorman tension. The design survives review with those three changes. If any of the three fixes is rejected, recommend Instrument Panel.

---

## 1. Critical review

### 1.1 Where the direction breaks

| # | Claim in brief | Break | Severity |
|---|---|---|---|
| R1 | "Entities drift and re-cluster as the user filters" | A 2-D projection is a fixed function of the embedding set. If filtering changes positions, either positions were never honest, or the client is re-running layout (runtime compute approaching the spirit of the no-runtime-inference rule, and hopeless at 60 fps on mobile for >~2k nodes). Animated "drift" with no data change is decoration, which O'Gorman forbids. | **Blocking** |
| R2 | "Drift ... as the user scrubs time" | This one is honest *if and only if* each time slice has its own precomputed projection, aligned so the frame does not spin between slices. Nothing in the brief says the pipeline produces per-slice projections. Unaligned per-slice UMAP will produce violent, meaningless rotations. | **Blocking** until pipeline confirms aligned slices |
| R3 | "Selection pulls a local neighborhood into focus with spring physics" | If the neighbors move, their displayed position is no longer their embedding position. A user reading distance off the screen is reading a lie. | **Blocking** as stated; fixable as a lens (§3 C2) |
| R4 | "Geography fades in as a ghost layer underneath" | Embedding x/y and lat/lon are different frames. A faded world map under a UMAP cloud implies spatial correspondence that does not exist. | **Blocking** as stated; fixable as a frame morph (§3 C8) |
| R5 | "Organic motion, physics-based" vs. O'Gorman honest materials | Physics that never settles reads as screensaver. Overshoot and jiggle are ornament. | High, resolved in §1.3 |
| R6 | 129 MB vs. first paint <1.5 s on 4G | At a realistic ~1 MB/s, the first paint budget is ≲300 KB transferred. The full projection (410k × 2 × int16) alone is 1.6 MB. First paint cannot include the field; it must be a precomputed raster plus a sparse seed set. | High, resolved in C7 |
| R7 | "Every visible entity is inspectable" at 410k | At any zoom where you see the whole field, a dot is sub-pixel. "Visible" must be defined as "rendered at ≥ 2 px and hit-testable," and the aggregate must be inspectable as an aggregate (count, vintage, cluster id), or the rule is unenforceable. | Medium |
| R8 | New embeddings (JEPA primary) | JEPA latents are not trained for cosine-neighborhood geometry. Projection quality and neighbor lists may degrade vs. the contrastive twin head. The map must not assume the primary head produces the better picture. | Medium, OD-2 |
| R9 | Twin/comparison excludes whole person by `person_id` | Fine as a rule; it is a data-join rule, not a UI rule. The UI must *display* that exclusion happened (count removed + vintage) or the comparison looks arbitrarily sparse. | Low |
| R10 | 37,000 edges | Edges are sparse (0.09 per entity). Drawing them as a global layer is visually meaningless; they only make sense inside a selected neighborhood. | Low |

### 1.2 What is underspecified

- **U1.** What is an "entity"? Players only, or players + teams + games + papers? Time+place is asserted for all; inspection cards (C4) differ per type.
- **U2.** Time granularity for C3: season, week, game, day? This decides slice count and precompute size. Default in OD-4.
- **U3.** Which projection algorithm, and is it deterministic and aligned across slices and across model swaps (v5 → JEPA)? If not, every retrain scrambles the user's mental map.
- **U4.** Whether "visible entities" in the 60 fps bar means 5,000 *drawn* points or 5,000 *interactable* points. SPEC takes the stricter reading: 5,000 drawn and hit-testable at 60 fps, with the remainder drawn as a baked density raster.
- **U5.** What a comparison (C5) compares: two entities, an entity vs. a cluster, or two time slices of one entity. Default in OD-6.
- **U6.** Mobile: is the map the primary surface on a phone, or does the inspection card take over? Default: map stays primary, card is a bottom sheet.
- **U7.** Night-board dark: is it a user toggle, system preference, or both? Default: system preference with manual override.
- **U8.** Where does provenance live for a *position*? A dot's x/y has a model vintage, a projection vintage, and a slice vintage. The brief says every number carries provenance; positions are numbers.

### 1.3 The central risk: organic physics vs. Drafting Board + O'Gorman

Direct answer: **physics is permitted as a material property, never as a mood.** Concrete rules that make Living Field compatible with industrial functionalism:

1. **Nothing moves unless data changed.** At rest, zero motion. No ambient drift, no breathing, no idle jitter. The field is "living" because it responds, not because it fidgets.
2. **Critically damped only.** Springs never overshoot. One spring constant, one damping ratio, system-wide. Motion reads like a weighted instrument needle settling, not a bouncing ball.
3. **Motion is a readout.** When entities move between time slices, the UI shows the magnitude (e.g., "mean displacement 0.14 units, 2024 → 2025"). Movement you can read a number off is functional. Movement you cannot is decoration.
4. **Marks are honest.** Dots are flat discs. No glow, no bloom, no trails, no particles-with-tails. Size encodes one declared variable or nothing.
5. **Lens, not displacement.** Focus magnifies a region of the plane; it does not move entities relative to each other. Ghost markers show true positions whenever a lens distorts.
6. **Paper is the material.** Light mode: ink dots on paper with a drafting grid at 1 px, 8 % ink. Night-board: chalk-weight dots on slate. Strong color is spent only on selection, time cursor, and status (503 / stale).
7. **Fixed durations.** All transitions: 180 ms micro, 420 ms layout, 900 ms slice morph. No easing zoo. One curve.

If the team cannot hold rule 1 and rule 5 under pressure from "it looks dead," that is Kill Criterion K1.

---

## 2. PRD

### 2.1 Problem

The current atlas shows one static projection. Users cannot see how an entity's place in embedding space changed over time, cannot see who its neighbors are without leaving the map, and cannot trust what they see because positions carry no vintage. New embeddings will land and silently move every dot; today there is no way to communicate that.

### 2.2 Users

1. **The reader** (mobile, 60 % of sessions assumed; OD-1 to confirm with analytics). Arrives from a link to one entity. Wants: where is it, who is near it, how did it get here. Thirty seconds.
2. **The analyst** (desktop). Wants: filter, scrub, compare two entities or two seasons, export a neighbor list with vintage.
3. **The owner / model team** (desktop). Wants: see v5 vs. JEPA side by side, judge whether the new picture is better, catch regressions before ratifying.

### 2.3 Goals

- G1. A reader lands on an entity permalink and sees it in context in under 1.5 s on 4G.
- G2. Any dot on screen can be tapped and inspected; any aggregate can be inspected as an aggregate.
- G3. Scrubbing time shows honest movement with a readable magnitude.
- G4. Model swap is a visible event, not a silent reshuffle.
- G5. The whole thing holds 60 fps at 5,000 drawn points on a mid-range 2023 Android phone.

### 2.4 Non-goals

- No runtime inference, no client-side projection, no server-side re-layout on request.
- No new API keys or third-party tile services. Geography frame uses a self-hosted, precomputed simplified coastline (one static asset).
- No 3-D. No VR. No shaders beyond point sprites and a density raster.
- No redesign of the data pipeline. The SPEC lists what it needs *exported*; building the exporter is the platform track's job.
- No social features, annotations, or accounts.

### 2.5 Success metrics (each with provenance source)

| Metric | Bar | Source |
|---|---|---|
| First contentful paint, 4G, mid-range Android | p75 < 1.5 s | Lighthouse CI + WebPageTest run on each PR, archived |
| Frame time with 5,000 drawn points, pan + scrub | p95 ≤ 16.6 ms | In-app `PerformanceObserver` sample, posted to a static JSON per release |
| Dead ends | 0 non-inspectable rendered marks | Playwright crawl: click every drawn mark, assert card opens |
| Honest state | 0 renders of stale data without a vintage badge | Playwright: force slice fetch to 503, assert 503 panel, assert no dots from prior slice remain |
| Entity permalink survival across model swap | 100 % of permalinks resolve to the same entity | Script over export manifest |
| Reader task | 70 % of first-time users open an inspection card within 30 s | Privacy-safe event counter, first 2 weeks |

---

## 3. SPEC by component

Each component has: **Build**, **Depends on pipeline export**, **Evidence contract** (artifact, measurement, bar).

Shared data contract (exported by the platform track, consumed read-only here):

```
/atlas/v{N}/manifest.json         model_id, model_vintage, projection_id, projection_vintage,
                                  slices[], tile_scheme, entity_count, edge_count, sha256 per file
/atlas/v{N}/raster/{slice}.png    precomputed density raster, 1024x1024, 8-bit, ~40-80 KB
/atlas/v{N}/seed/{slice}.bin      top-K entities by salience, K=5000: id u32, x i16, y i16, type u8
/atlas/v{N}/tiles/{slice}/{z}/{x}/{y}.bin   quadtree tiles, same record format, ≤ 2,000 records each
/atlas/v{N}/neighbors/{id}.json   top-50 neighbors with distance, per head (jepa|contrastive|v5),
                                  person_id of each neighbor, vintage
/atlas/v{N}/entity/{id}.json      card payload: fields, time, place, provenance per field
/atlas/v{N}/geo/coast.json        simplified coastline, one file, ≤ 60 KB
```

Slice projections must be **aligned** (Procrustes to the reference slice, or parametric UMAP with shared weights). The manifest carries `alignment_method` and a per-slice `alignment_residual`. If residual exceeds the OD-5 threshold, the client refuses to animate between those slices and cross-fades instead, with a badge saying why.

### C1. Embedding-first map core

**Build.** One WebGL2 canvas, raw point-sprite shader, instanced draw of up to 5,000 interactable points over a baked density raster. Canvas2D fallback draws the raster only plus the selected neighborhood. No scene-graph library. Quadtree tile loader with LRU of 64 tiles. Hit-testing by color-ID offscreen pass (one pixel readback per pointer event, throttled to 30 Hz).

**Depends on.** manifest, raster, seed, tiles.

**Evidence contract.**
- Artifact: `evidence/c1-render-report.json` produced by Playwright on CI, per PR.
- Measurement: count of drawn points, frame-time p95 during a scripted 10 s pan/zoom, bytes transferred before first paint.
- Bar: 5,000 points drawn; p95 ≤ 16.6 ms on the reference device (Pixel 7a in BrowserStack or owner's device, OD-9); ≤ 300 KB before first paint.

### C2. Motion design language

**Build.** A single `motion.ts` exporting three durations (180 / 420 / 900 ms), one easing curve, one critically damped spring (ζ = 1.0, ω chosen so 95 % settle ≤ 420 ms), and a `reducedMotion` flag honoring `prefers-reduced-motion` (crossfade only). Focus is a **fisheye lens** on the view transform, not on entity coordinates: radius 120 px desktop / 96 px mobile, magnification 2.5×, with 1 px ghost rings at true screen positions of displaced marks. Slice morph interpolates positions linearly in projection space over 900 ms and renders a displacement readout.

**Depends on.** Nothing from pipeline.

**Evidence contract.**
- Artifact: `evidence/c2-motion-audit.md` plus a 10 s screen recording per PR touching motion.
- Measurement: idle frame diff (pixel delta between consecutive frames with no input) and overshoot (max spring value above target).
- Bar: idle pixel delta = 0 after settle; overshoot = 0; every motion in the recording is annotated with the data change that caused it.

### C3. Time scrubber

**Build.** Horizontal rail, one slice per tick, drag or arrow keys. Scrubbing prefetches ±1 slice seed. Position of the active slice shown with vintage. Between slices: morph if `alignment_residual` under threshold, else crossfade with badge. Displacement readout: mean and p95 of per-entity displacement among drawn points.

**Depends on.** slices[], aligned projections, per-slice seed + tiles.

**Evidence contract.**
- Artifact: `evidence/c3-scrub-honesty.json`.
- Measurement: for 200 sampled entities, screen displacement vs. projection-space displacement; correlation.
- Bar: Pearson r ≥ 0.99 (the screen never shows motion the data does not have); missing slice → 503 panel within 300 ms, zero stale dots.

### C4. Entity inspection

**Build.** Bottom sheet on mobile, right rail on desktop. Three sections: identity (name, type, time, place), neighbors (top-10 with distance and head used), provenance (model vintage, projection vintage, slice vintage, per-field source). Every number has a hover/tap that reveals source + vintage. Aggregate inspection: tapping a raster region with no interactable point opens an aggregate card (entity count in tile, dominant type, vintage).

**Depends on.** entity payload, neighbors payload.

**Evidence contract.**
- Artifact: `evidence/c4-dead-end-crawl.json`.
- Measurement: Playwright clicks every drawn mark and 50 random raster regions.
- Bar: 100 % open a card; 100 % of numbers on the card have a provenance tooltip; card fetch failure shows 503 panel, never an empty card.

### C5. Comparison mode

**Build.** Two-up: A vs. B. B may be another entity or the same entity in another slice (OD-6). Shared neighbor list with Jaccard overlap number. Twin exclusion applied by `person_id` server-side in the neighbors export; the client **displays** "n excluded (same person)" with the count from the payload. Lens applied to both.

**Depends on.** neighbors payload with `person_id` and `excluded_same_person_count`.

**Evidence contract.**
- Artifact: `evidence/c5-exclusion-audit.json`.
- Measurement: for 500 sampled entities, assert no neighbor shares `person_id` with the anchor; assert displayed count equals payload count.
- Bar: 0 violations.

### C6. Search and discovery

**Build.** Client-side prefix index over entity names, shipped as a sharded static trie (first shard ≤ 40 KB, loaded after first paint). Result selection flies to entity, opens card. "Similar to this" is just the neighbor list. No semantic search (would require runtime inference).

**Depends on.** name index export.

**Evidence contract.**
- Artifact: `evidence/c6-search-latency.json`.
- Measurement: keystroke-to-results on reference device; index bytes.
- Bar: p95 ≤ 80 ms; first shard ≤ 40 KB gz.

### C7. Performance budget

**Build.** Budgets enforced in CI via `size-limit` and Lighthouse CI. Budget table:

| Item | Budget |
|---|---|
| JS before first paint | ≤ 90 KB gz |
| CSS | ≤ 15 KB gz |
| First raster + seed | ≤ 150 KB |
| Total before first paint | ≤ 300 KB |
| Drawn interactable points | 5,000 max; degrade to 2,500 if p95 frame > 16.6 ms for 2 s |
| Tile LRU | 64 tiles, ~1 MB |
| Memory (mobile) | ≤ 150 MB heap |

**Evidence contract.**
- Artifact: Lighthouse CI report + `size-limit` output, per PR, archived under `evidence/c7/`.
- Measurement: as table.
- Bar: all green; a PR that reddens any row cannot carry the owner's merge-word.

### C8. Data-viz overlays (including geography)

**Build.** Overlays are toggles, exclusive where frames conflict:
- **Frame morph: embedding ↔ geography.** Not a layer under the field; a second coordinate frame. The user drags a frame slider; dots travel from projection x/y to lat/lon over 900 ms. At either end, the other frame's coastline is a 10 % ghost **only when the frame slider is between 0.3 and 0.7**, so a ghost never appears under a pure embedding view. This is how "geography fades in as a ghost" survives honesty.
- **Density raster** (always on at low zoom).
- **Edges** only within the selected neighborhood (R10).
- **Type color** (categorical, ≤ 6 hues, from the Drafting Board palette), or **one scalar** as size. Never both color and size on scalars.

**Depends on.** coast.json, lat/lon on entity records (place is asserted for every entity).

**Evidence contract.**
- Artifact: `evidence/c8-frame-audit.json` + screenshots at slider 0, 0.5, 1.
- Measurement: at slider 0 and 1, count of coastline pixels rendered.
- Bar: 0 at both ends; entities with no place fall out of the geo frame with a visible "n entities have no place" count.

---

## 4. Open decisions (numbered, bounded, defaulted)

| # | Decision | Bounds | Default |
|---|---|---|---|
| OD-1 | Mobile share assumption used for prioritization | 40 % / 60 % / 80 % | **60 %**; replace with analytics within 2 weeks |
| OD-2 | Which head drives positions and neighbors when JEPA lands | JEPA only / contrastive only / user toggle | **User toggle, contrastive default** until owner ratifies JEPA picture as better (R8) |
| OD-3 | Renderer | raw WebGL2 point sprites / deck.gl ScatterplotLayer / Canvas2D only | **Raw WebGL2** (bundle budget); deck.gl is the fallback if C1 misses frame bar after 2 sprints |
| OD-4 | Time slice granularity | season / month / week | **Season** (bounded slice count, aligned projections tractable); week is out of scope for v1 |
| OD-5 | Alignment residual threshold above which morph is refused | 0.05 / 0.10 / 0.20 of projection extent | **0.10** |
| OD-6 | Comparison B-side | entity only / entity or slice / up to 4 | **Entity or same-entity-other-slice**; no 4-up |
| OD-7 | Dark mode trigger | system only / manual only / both | **Both**, system first |
| OD-8 | Lens geometry | fisheye / rectangular magnifier / none | **Fisheye** with ghost rings; none if K2 trips |
| OD-9 | Reference device for all bars | Pixel 7a / iPhone 13 / Moto G Power 2023 | **Pixel 7a**, Chrome stable, 4G throttle in Lighthouse |
| OD-10 | Interactable point cap | 2,500 / 5,000 / 10,000 | **5,000** per QUICK bar; auto-degrade to 2,500 |
| OD-11 | Geography coastline source | self-hosted Natural Earth 110m / 50m | **110m**, one static file |
| OD-12 | Permalink key | entity id / entity id + slice / entity id + slice + head | **id + slice**; head is a query param, defaulted |

---

## 5. Kill criteria: abandon Living Field for Instrument Panel

Evaluate at the end of each sprint. Any **one** trips the kill.

| # | Criterion | Measurement | Trip |
|---|---|---|---|
| K1 | Motion discipline cannot be held | Motion audit (C2) finds ambient motion or overshoot in two consecutive PRs after being flagged | Trip |
| K2 | Lens confuses rather than helps | 5-user hallway test: ≥ 3 of 5 misread neighbor distance under lens vs. without | Trip |
| K3 | Frame bar unreachable | C1 p95 frame time > 25 ms on reference device after two sprints and the OD-3 fallback | Trip |
| K4 | Pipeline cannot export aligned slices | `alignment_residual` > OD-5 threshold for more than 30 % of slice pairs after platform track's attempt | Trip (C3 degrades to crossfade-only, which *is* Instrument Panel) |
| K5 | First paint bar unreachable | Lighthouse p75 FCP > 2.0 s on 4G after C7 budgets enforced | Trip |
| K6 | Honesty failure ships | Any release where stale dots render without a vintage badge, or any neighbor list violates `person_id` exclusion | Immediate trip and rollback |
| K7 | Schedule | Living Field C1–C4 not demoable on real v5 data in 6 weeks of one engineer plus half a designer | Trip |

Instrument Panel fallback is defined as: static aligned projection per slice, crossfade between slices, no lens, selection highlights neighbors in place, same cards, same budgets, same evidence contracts. Roughly 60 % of the work above carries over.

---

## 6. Build order (small team: 1 engineer, 0.5 designer)

1. **Week 1–2.** Export contract agreed with platform track. C7 budgets wired in CI first. C1 renders v5 seed + raster, static, no motion.
2. **Week 3.** C4 cards with provenance; dead-end crawl green. C6 prefix search.
3. **Week 4.** C2 motion module; lens with ghost rings; hallway test (K2 check).
4. **Week 5.** C3 scrubber on whatever slices the pipeline can export aligned; K4 check.
5. **Week 6.** C5 comparison with exclusion audit; C8 frame morph. Kill review. Owner's merge-word or Instrument Panel.
6. **Post-ratification.** Head toggle (OD-2) lights up when JEPA export lands; permalinks unchanged.

---

## 7. What this SPEC asks of the platform track (not designed here)

- Aligned per-slice projections with residuals in the manifest.
- Seed + quadtree tile export in the record format above.
- Neighbor export per head with `person_id` and exclusion count.
- Per-field provenance in entity payload.
- A 503 from any path when the artifact is missing or the manifest hash mismatches. Never a cached stale artifact without `stale: true` and its vintage.
