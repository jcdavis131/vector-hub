# Spec: Vector Hub Real-Product Gateway

## Objective

Make `dumbmodel.com` a truthful methodology notebook for the hoops embedding
models. Visitors should understand what the served 64-d map measures, where
every headline number comes from, and that this site is an explanation notebook
— not a lab and not a six-product storefront.

`public/assets/data/products.json` still ships the six-product availability
record. It is gated for internal consistency, but it is not rendered as the
landing journey.

The approved scope is the served `public/` notebook. The investor, game,
soft-mirror, domain, and production-deployment surfaces are out of scope.

## Contract maintenance

The checker pins four things that must move together whenever served truth
changes:

- `EXPECTED` / `CANONICAL_COPY` / `AVAILABILITY_CHECKED_AT` — the product JSON
  record. Arcade joined the family with the midnight-garden rebuild; the JSON
  contract carries six products. Refreshing `products.json` without bumping the
  availability pin fails CI on purpose.
- `HEADLINE_CLAIMS` — the methodology home must keep 12,966 player-seasons,
  MTNN v5, incumbent 2026-07-25, 1,313 era-twin players, and macro-MAE 0.4382.
- Cut list — the home must not regrow product-hub framing or `*.dumbmodel.com`
  storefront CTAs.
- Accessibility — skip link, `:focus-visible`, 44×44 targets, reduced motion,
  overflow-wrap, and paper/ink contrast still apply, now against `drafting.css`.

`VERIFIED_COUNT_CLAIMS` is the one narrow carve-out from the
comma-formatted-count rule on the JSON record.

## Tech Stack

- Static HTML, CSS, JavaScript, and JSON
- No build step and no new runtime dependencies
- Vercel serves `public/` as configured by `vercel.json`
- Existing Japandi family tokens and system fonts

## Commands

- Static contract: `python -B scripts/check_gateway.py`
- Season Clock contract: `python -B scripts/check_season_clock.py`
- Checker regressions:
  `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s tests -p "test_gateway*.py" -v`
- Local server: `python -m http.server 4173 --directory public`
- Browser verification: run the gateway journey at 360, 768, and 1440 CSS pixels
- Existing package regression on Windows:
  `$env:PYTHONPATH="$PWD\packages\vector-core\src;$PWD\packages\vector-bench\src"; python -m pytest packages/vector-core/tests packages/vector-bench/tests -q`
- Diff hygiene: `git diff --check`

## Project Structure

- `public/index.html` — served methodology notebook home
- `public/drafting.css` — Drafting Board shell (paper + night-board)
- `public/season-clock.html` — Season Clock / sponsor-bridge timeline demo
- `public/assets/data/products.json` — verified product truth record
- `public/assets/data/season_clock_demo.json` — small committed Season Clock sample
- `scripts/check_gateway.py` — deterministic static acceptance gate
- `scripts/check_season_clock.py` — Season Clock page + demo JSON gate
- `tests/test_gateway_checker.py` — adversarial standard-library gate tests
- `.github/workflows/gateway.yml` — CI gate for served-site changes
- `docs/JAPANDI_DESIGN_SYSTEM.md` — family visual conventions
- `tasks/` — implementation plan and progress checklist

## Code Style

Use semantic HTML, native links and buttons, existing CSS custom properties, and
small dependency-free scripts. The methodology home pins headline numbers in
plain markup (no JavaScript required to read them) and links the ten notebook
sections. Product-hub cards, availability fetchers, and `*.dumbmodel.com`
storefront CTAs stay off this site: hoops.dumbmodel.com remains the product.

Season Clock (`public/season-clock.html`) is a standalone demo. After the
methodology overhaul it is not part of the notebook TOC.

## Testing Strategy

1. Add a static gate that fails against pinned base `209536a` for the generated
   map/specification journey, missing product truth fields, unsupported metrics,
   and accessibility-contract violations.
2. Make the smallest served-tree change that turns that gate green.
3. Run package regressions because the repository also publishes `vector-core`.
4. Serve the exact `public/` directory and verify links, console, keyboard flow,
   accessibility, overflow, and performance in an isolated browser.
5. Verify the Vercel preview separately; protected or unreachable previews do
   not count as runtime evidence.

## Boundaries

- Always:
  - use real product URLs and dated provenance;
  - label unknown, stale, unavailable, and checking states honestly;
  - preserve the Japandi palette and zero-build delivery model;
  - honor reduced motion and native keyboard behavior;
  - validate the exact `public/` tree.
- Ask first:
  - add dependencies, analytics, authentication, domains, or CI secrets;
  - update an existing pull request;
  - merge or deploy to production.
- Never:
  - present generated or synthetic data as a measured product result;
  - invent model scores, counts, freshness, or availability;
  - edit root duplicates as a substitute for the served tree;
  - touch existing worktrees or soft mirrors;
  - force-push, rewrite history, or bypass repository guards.

## Success Criteria

- The methodology home pins 12,966 / MTNN v5 / 2026-07-25 / 1,313 / 0.4382 and
  states that the site is an explanation notebook, not a storefront.
- All ten notebook sections exist, each with skip link, nav, main, footer, and
  one h1. MTNN v5 is documented champion copy, not a forbidden spec leak.
- `products.json` still contains exactly six evidence-backed records, each with
  an explicit point-in-time availability state, exact GET method, numeric HTTP
  status, non-future `availability_checked_at`, pinned evidence source, and
  distinct non-future repository `pushed_at`.
- The served notebook contains no generated 20,719-point map, fabricated roster
  score, `LCG`, `fusion 0.`, or news-tower copy.
- There is no horizontal overflow at 360, 768, or 1440 CSS pixels.
- The core journey is keyboard complete, focus-visible, and uses touch targets
  at least 44 by 44 CSS pixels (nav, brand, skip link, theme toggle).
- Automated accessibility reports zero serious or critical findings.
- Lab LCP is at most 2.5 seconds, CLS at most 0.10, and TBT at most 200 ms.
- Static, package-regression, browser, and preview gates pass before readiness.

## Open Questions

- Production deployment and rollback are intentionally unauthorized.
- Preview deployment is authorized, but preview access may still be blocked by
  the Vercel account boundary.
