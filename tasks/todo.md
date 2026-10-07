# Vector Hub Real-Product Gateway

## Task 1: Add the failing gateway contract

**Acceptance criteria**
- [x] The check validates exactly five products and all required truth fields.
- [x] The check rejects generated-map/specification copy and unsupported scores.
- [x] The check enforces static semantic, focus, motion, and touch-target rules.
- [x] Adversarial tests reject type, claim, URL-association, future-date,
  target-size, and overflow-clipping bypasses.

**Verification**
- [x] `python scripts/check_gateway.py` fails against pinned base `209536a`.

**Dependencies:** None
**Files:** `scripts/check_gateway.py`
**Scope:** Small

## Task 2: Deliver the truthful served gateway

**Acceptance criteria**
- [x] The five products render from a dated truth record.
- [x] The generated map and internal specification journey are removed.
- [x] Unknown and unavailable data states remain explicit.
- [x] Point-in-time HTTP availability includes its check timestamp.
- [x] Availability provenance records exact GET and numeric HTTP status.
- [x] Unified's measured 200 state exposes product CTA + evidence.

**Verification**
- [x] `python scripts/check_gateway.py`
- [x] Manual source review against `spec/vector-hub-real-product-gateway.md`

**Dependencies:** Task 1
**Files:** `public/index.html`, `public/assets/data/products.json`, `README.md`
**Scope:** Medium

## Task 3: Guard and verify delivery

**Acceptance criteria**
- [ ] Static-site changes run the gateway check in CI.
- [x] Exact `public/` output passes browser, accessibility, and performance gates.
- [ ] Preview is reachable and matches the reviewed commit, or the external
  access blocker is recorded without claiming success.

**Verification**
- [x] `python -B scripts/check_gateway.py`
- [x] `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s tests -p "test_gateway*.py" -v`
- [x] `$env:PYTHONPATH="$PWD\packages\vector-core\src;$PWD\packages\vector-bench\src"; python -m pytest packages/vector-core/tests packages/vector-bench/tests -q`
- [x] `git diff --check`
- [x] Browser checks at 360, 768, and 1440 CSS pixels

**Dependencies:** Task 2
**Files:** `.github/workflows/gateway.yml` plus verification artifacts outside git
**Scope:** Small

## Completion

- [x] Code review approves the scoped diff.
- [ ] Commit, push, PR, and preview actions are recorded.
- [ ] Merge, production deployment, and rollback are not performed.
