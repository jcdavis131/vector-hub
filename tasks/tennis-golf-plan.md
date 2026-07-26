# DumbModel Expansion Plan: Vector Tennis + Vector Golf

> Status: Approved for autonomous execution on 2026-07-11
> Product owner decisions:
> - Tennis: strictly noncommercial; source-derived assets are CC BY-NC-SA 4.0.
> - Golf: open-data Course Cipher and Course MTNN now; player-performance MTNN stays provider-ready and untrained until rights-cleared data exists.
> - Hub: preserve existing uncommitted Unified/Pitch changes and integrate additively.

## 1. Objective

Add two complete, honest, replayable individual-sport products to dumbmodel.com:

- **Vector Tennis** models player style and matchup behavior from rights-compatible public data.
- **Vector Golf** models course identity and geometry from open course/context data. It does not claim to predict current PGA, LIV, or DP World performance without licensed inputs.
- Both products ship as static browser-first sites, use Python/NumPy/PyTorch pipelines, expose their actual model architecture and evaluation evidence, and preserve deterministic daily/free-play separation.
- The hub expands from three to five sports only after both sport previews pass their gates.
- Unified-space integration is additive and occurs only after each standalone embedding passes its native gates.

## 2. Non-negotiable truth boundaries

### Tennis

- Sackmann/Tennis Abstract inputs and derived data assets remain noncommercial and ShareAlike.
- Attribution, source revision, modification notice, and CC BY-NC-SA 4.0 license are visible in the product and machine-readable manifest.
- Official ATP/WTA sites are not scraped.
- The frozen comparative test ends in 2024 so ATP/WTA evaluation remains symmetric.
- Match, ranking, and rolling features use only observations timestamped before the target.
- Match Charting Project coverage is represented by masks and coverage badges; charted status is never treated as player skill.

### Golf

- PGA TOUR/ShotLink, LIV, DP World Tour, OWGR, Data Golf, and undocumented ESPN endpoints are excluded from production ingestion unless a written contract permits training and derived-browser exports.
- OpenGolfAPI, Wikidata, Open-Meteo, and other open inputs retain their required attribution and license metadata.
- The promoted model is a **Course MTNN**, not a professional-player performance model.
- A provider adapter, schema, tests, and promotion contract may exist for a future player MTNN, but no restricted data, fabricated training rows, or performance claims ship.

## 3. Ownership and collision boundaries

| Lane | Owner | Writable scope | Read-only dependencies |
|---|---|---|---|
| Tennis | Tennis build agent | `C:\Users\jcdav\vector-tennis\**` | Existing vector repos |
| Golf | Golf build agent | `C:\Users\jcdav\vector-golf\**` | Existing vector repos |
| Shared | Parent agent | `vector-hub/**`, later `vector-unified/**` | All sport repos |
| Review | Reviewer/test agents | No writes unless explicitly delegated | Diff + test evidence |

Sport agents maintain their own `tasks/todo.md`, keep exactly one item in progress, and verify each slice before advancing. They do not deploy production or edit the hub.

## 4. Shared sport integration contract

Each sport must publish `docs/SPORT_INTEGRATION_CONTRACT.md` with:

1. slug, title, game number, subdomain, accent token, and 40x40 glyph;
2. product scope and explicit non-goals;
3. cadence, puzzle epoch, UTC seed algorithm, replay identity, and daily/practice storage keys;
4. model ID, embedding dimension, corpus row count, temporal/context split, and primary promotion metric;
5. boot assets, schemas, checksums, maximum bytes, and cache policy;
6. page topology and required routes;
7. source attribution text and source-manifest path;
8. telemetry policy (default: none unless separately verified);
9. hub card hook, pitch, pill, model claim, and evidence fields;
10. preview smoke command, rollback artifact, and production readiness boolean.

The hub consumes only evidence-backed values from these contracts/manifests.

## 5. Dependency graph

```text
source decision
  -> source manifest + fixtures
  -> canonical corpus/entities
  -> leak-free features + transparent baseline
  -> model tests
  -> bounded hill-climb
  -> promotion report
  -> browser assets
  -> game logic tests
  -> UI + methods/model/player pages
  -> preview deploy + browser/a11y/perf gates
  -> hub five-sport integration
  -> optional unified registry/adapters
  -> production deploy + smoke + rollback evidence
```

Tennis and Golf execute independently through preview readiness. Hub and Unified work remain sequential shared lanes.

## 6. Vector Tennis execution plan

### T0 — Contract, license, and scaffold

Deliverables:
- repository hygiene files matching siblings;
- `docs/SPEC.md`;
- `docs/SPORT_INTEGRATION_CONTRACT.md`;
- `docs/DATA_SOURCES.md`;
- `LICENSE-DATA.md`;
- `tasks/plan.md` and `tasks/todo.md`;
- offline fixture from the CC BY 4.0 UCI sample.

Acceptance:
- all six spec areas are complete;
- source manifest records code license separately from data-asset license;
- strict source audit fails closed on unknown or prohibited sources;
- no external source is fetched during unit tests.

### T1 — Acquisition and canonical corpus

Deliverables:
- pinned, resumable Sackmann ATP/WTA and optional Match Charting acquisition;
- immutable source metadata/checksums;
- canonical tour-qualified player IDs and aliases;
- player-season, pre-match, and masked charting tables;
- coverage report by tour/year/surface/family.

Acceptance:
- repeated acquisition resumes and produces identical checksums;
- incomplete cache cannot produce public assets;
- no duplicate `(tour, player_id, season)`;
- frozen evidence split is train through 2022, validation 2023, test 2024;
- later ATP-only rows are labeled refresh-only.

### T2 — Leak-free features and transparent baselines

Families:
- serve;
- return;
- opposition-adjusted strength;
- surface;
- shifted form;
- pressure with shrinkage;
- workload/rest;
- bio/career;
- match context;
- masked shot style;
- optional isolated cultural interest.

Baselines:
- era/tour normalized profile + PCA(3) + k-means;
- overall Elo;
- surface Elo;
- ranking-difference logistic regression;
- rolling serve/return logistic regression;
- next-profile persistence.

Acceptance:
- every predictive feature has `observed_at < target_start`;
- train-only normalization;
- no NaN/Inf in unmasked values;
- masks and coverage are exported;
- baseline report uses the same frozen rows as MTNN evaluation.

### T3 — Tennis MTNN and bounded hill-climb

Initial model:
- masked family residual towers;
- concat fusion;
- 32-dimensional L2-normalized embedding;
- next-season profile, surface profile, next-match win, margin, serve/return, career phase, and masked shot-style heads;
- adjacent-season contrastive continuity;
- matchup head over player/opponent vectors plus pre-match context.

Hill-climb:
- A transparent PCA incumbent;
- B flat two-layer MLP;
- C family towers + concat;
- D gated fusion only if C wins;
- embedding `{24,32,48}`, width `{16,24}`, dropout `{0.1,0.2}`, depth `{1,2}`;
- maximum 12 screening runs;
- finalists confirmed on seeds 7, 13, and 21;
- the 2024 test is touched once after selection.

Promotion:
- scorecard at least 70/100;
- match log-loss beats surface Elo;
- next-profile RMSE beats persistence;
- no ATP/WTA subgroup regresses more than 1%;
- directional agreement across all confirmation seeds;
- missing-family stress and license gates pass;
- incumbent retained on ambiguity.

### T4 — Tennis games and product

Required games:
1. **Centre Court Chimera** — identify two blended player-season style profiles.
2. **Surface Shift** — identify/order surface-specific transformations from profile cards.

Pressure Point is deferred unless point-level redistribution is confirmed and asset size/selection-bias gates pass.

Required routes:
- `/` or `index.html`;
- `/play`;
- `/surface`;
- `/map`;
- `/players`;
- `/player`;
- `/model`;
- `/methods`.

Acceptance:
- deterministic UTC daily puzzles and replay IDs;
- daily and practice stats use separate storage keys;
- rollover freezes the loaded daily puzzle;
- repeat guesses do not consume attempts;
- keyboard, focus-visible, reduced-motion, 375px mobile, and 44px touch-target gates pass;
- source/license and coverage caveats are visible.

### T5 — Tennis preview readiness

- all Python tests green with exact counts;
- JavaScript syntax and deterministic game-logic verification green;
- source/license audit green;
- asset checksums/schema/size budgets green;
- local browser smoke green with zero console errors;
- preview deploy only after all above pass.

## 7. Vector Golf execution plan

### G0 — Contract, rights ledger, and scaffold

Deliverables mirror T0, with a strict exclusion ledger for restricted providers.

Acceptance:
- every source states training, derivative-output, redistribution, attribution, and review/expiry terms;
- unknown rights fail closed;
- product copy explicitly says course model;
- future player-performance adapter is disabled by default.

### G1 — Open course/context corpus

Primary granularity:
- one canonical course record;
- hole-level geometry/profile rows where available;
- weather/climate normals with attribution;
- optional historical participation data only when its license permits derived publication.

Deliverables:
- pinned OpenGolfAPI acquisition;
- Wikidata metadata adapter;
- Open-Meteo context adapter with request/cache limits;
- canonical course/entity resolver;
- immutable bronze, normalized silver, and model-ready gold outputs;
- provenance and coverage reports.

Acceptance:
- stable course IDs and no duplicate canonical courses;
- per-source checksums and attribution;
- missing geometry/context represented by masks;
- offline fixtures rebuild the complete sample pipeline;
- no restricted provider endpoint appears in production configuration.

### G2 — Transparent course vectors and baselines

Families:
- layout/geometry;
- par and yardage shape;
- hole sequencing;
- hazard/terrain metadata when licensed;
- location/elevation;
- climate/weather normals;
- course history/era;
- source coverage/missingness.

Baselines:
- normalized profile + PCA(3);
- k-means course archetypes;
- nearest-neighbor retrieval;
- simple region/course-type classifiers;
- profile persistence/reconstruction.

Acceptance:
- deterministic vectors and archetypes;
- train-only normalization;
- no missing unmasked values;
- held-out course reconstruction/retrieval report;
- thin-source coverage downgrades claims rather than silently passing.

### G3 — Course MTNN and bounded hill-climb

Initial model:
- masked family residual towers;
- concat fusion;
- 24- or 32-dimensional L2-normalized course embedding;
- normalized profile reconstruction;
- par/yardage-shape reconstruction;
- region/climate/course-type auxiliary heads;
- masked family reconstruction;
- contrastive views generated only from safe feature masking, not fabricated courses.

Hill-climb:
- A PCA incumbent;
- B flat MLP;
- C residual towers + concat;
- D gated fusion only if C wins;
- maximum eight screening configurations;
- finalists confirmed on seeds 7, 13, and 21.

Promotion:
- course retrieval/reconstruction composite improves at least two points over the strongest baseline;
- no source-region subgroup regresses more than 2%;
- embedding effective rank and neighbor diversity floors pass;
- three-seed stability, license, artifact, and browser budgets pass.

Future player-performance MTNN:
- schema, provider protocol, temporal tests, and promotion scorecard may be implemented;
- training command must fail closed with `RIGHTS_CLEARED_DATA_REQUIRED`;
- no checkpoint, projection, or professional-tour prediction ships.

### G4 — Golf games and product

Required games:
1. **Course Cipher** — identify a course from progressively revealed par, yardage, geography, climate, and shape clues.
2. **Routing Room** — match/order anonymized hole-sequence or course-profile cards using the learned course embedding.

Cutline and Sunday Pressure remain explicitly deferred pending a licensed historical performance/scorecard feed.

Required routes:
- `/` or `index.html`;
- `/play`;
- `/routing`;
- `/map`;
- `/courses`;
- `/course`;
- `/model`;
- `/methods`.

Acceptance mirrors Tennis plus:
- every clue traces to an allowed source field;
- attribution is shown in reveal views;
- no PGA/LIV/DP World performance claim appears;
- daily/free-play state and deterministic replay are verified.

### G5 — Golf preview readiness

Same technical gates as T5 plus strict restricted-source string/config audit.

## 8. Shared hub integration

Only after both integration contracts report `previewReady: true`:

1. add green/yellow Tennis and green/gold Golf data accent tokens;
2. add two cards while preserving existing Unified/Pitch edits;
3. change hard-coded three-sport copy, stats, OG metadata, footer, and hero facts to five-sport evidence;
4. add `/tennis` and `/golf` redirects;
5. use an additive `games.manifest.json` if it reduces claim drift without complicating the static hub;
6. make the card grid responsive at 375px, 900px, and 1200px;
7. reconcile “no tracking” copy with any game telemetry (default for new sports is no telemetry);
8. keep cards hidden until each production subdomain returns its required assets successfully.

Hub gates:
- HTML/CSS/JS remain dependency-free;
- keyboard and focus behavior pass;
- hub transfer remains below 50KB gzip excluding HTML-inlined SVG;
- all five cards and redirects pass;
- claims byte-match sport manifests;
- existing three cards remain unchanged except necessary shared layout/copy.

## 9. Unified integration

This is post-standalone and additive:

1. replace hard-coded sport tuples with a registry adapter contract;
2. add Tennis player-season embeddings;
3. add Golf course embeddings only if the unified product explicitly supports entities beyond players; otherwise document non-action and leave Golf standalone;
4. pre-author defensible analogy mappings and `n/a` masks;
5. preserve fingerprints for existing Hoops/Gridiron/Pitch rows;
6. run native non-inferiority, cross-sport coherence, collapse, and curated analogy gates;
7. export a new versioned unified asset without overwriting the current shipped revision until gates pass.

No claim may say sport identity is erased; current G2 remains unresolved.

## 10. Deployment and rollback

Deployment order:
1. Tennis preview;
2. Golf preview;
3. browser/a11y/performance review;
4. create/link Vercel projects;
5. attach `tennis.dumbmodel.com` and `golf.dumbmodel.com`;
6. production-deploy sport sites;
7. verify subdomains and required assets;
8. preview hub integration;
9. production-deploy hub;
10. post-deploy smoke all five products.

Rollback:
- retain the previous production deployment for each project;
- a failing sport is removed/hidden from the hub before DNS changes;
- hub rollback is independent of sport rollback;
- no data/model asset is promoted in-place without a stamped prior checksum.

Production is a guarded action. Preview evidence must pass first.

## 11. Global Definition of Done

- Both repositories contain approved living specs, plans, source manifests, tests, and reproducible offline fixtures.
- Tennis has a promoted evidence-backed player MTNN and two verified replayable games.
- Golf has a promoted evidence-backed Course MTNN and two verified replayable games.
- Golf player-performance training remains visibly blocked until licensed data is supplied.
- Each product has truthful Methods/Model/entity pages and source attribution.
- Both preview and production subdomains pass smoke, console, network, mobile, accessibility, and performance checks.
- dumbmodel.com displays five verified sport cards and working redirects.
- Shared integration preserves existing user changes.
- A final code-quality review finds no unresolved P0/P1 issues.
- Readiness report lists commands, metrics, source/license boundaries, deployment IDs, URLs, rollback targets, and any explicit non-actions.
