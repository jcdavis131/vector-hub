# Implementation Plan: Vector Hub Real-Product Gateway

## Overview

Replace the served landing page's generated-map/specification journey with a
small, evidence-backed product gateway. Add an executable contract first, then
implement the truthful product record and accessible UI, verify in a real
browser, and ship only to an authorized preview.

## Architecture Decisions

- Treat `public/assets/data/products.json` as the single presentation contract
  for product URL, state, evidence, and freshness.
- Keep the site zero-build and dependency-free.
- Validate `public/`, because `vercel.json` identifies it as the deployed tree.
- Prefer a content-first product list over decorative generated visualization.
- Keep CI narrowly scoped to the gateway contract and standard-library Python.

## Task List

### Phase 1: Prove the defects

- [x] Add `scripts/check_gateway.py` with negative tests against the pinned
  baseline for product truth, generated/specification copy, unsupported
  metrics, and static accessibility requirements.
- [x] Confirm the gate fails before changing the served page.
- [x] Add adversarial tests for rendered types and claims, pinned URL
  associations, future timestamps, target sizing, and overflow clipping.

### Checkpoint: Reproduction

- [x] Failure output names the real acceptance gaps.
- [x] No production source changed before the red gate was observed.

### Phase 2: Build the gateway

- [x] Add the five-product truth record with verified URLs, conservative
  availability states, evidence sources, and timestamps.
- [x] Rework `public/index.html` into a responsive, semantic, content-first
  gateway that consumes the truth record and handles unavailable data honestly.
- [x] Update README product count and gateway contract.

### Checkpoint: Static correctness

- [x] Gateway contract passes.
- [x] Diff contains no generated map, fabricated score, or spec-dump copy.
- [x] Repository package tests still pass.

### Phase 3: Runtime and delivery

- [x] Add a gateway CI workflow without adding dependencies.
- [ ] Serve `public/` and verify desktop/mobile journeys, console, keyboard,
  accessibility, overflow, and performance.
- [ ] Complete code review and secret/diff hygiene.
- [ ] Commit, push, open a PR, and validate the authorized Vercel preview.

### Checkpoint: Complete

- [ ] All specification success criteria pass or are recorded as blockers.
- [ ] Production deployment, merge, and rollback remain untouched.

## Risks and Mitigations

- Live product probes may be blocked by transient network or bot policy:
  represent uncertainty explicitly and retain the last verified timestamp.
- Existing root duplicates can create false confidence: all gates point at
  `public/`.
- Existing unrelated worktrees and pull requests may overlap: do not modify or
  adopt them; compare the final diff against pinned base `209536a`.
- Browser tooling can create artifacts: inventory and remove only attributable
  outputs before commit.

## Open Questions

- None block local implementation or preview deployment.
- Production promotion requires a separate environment-specific authorization.
