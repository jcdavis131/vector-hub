# Spec: Vector Hub Real-Product Gateway

## Objective

Make `dumbmodel.com` a fast, truthful gateway to the five-product family.
Visitors should understand the family, see each product's current availability
and evidence, and reach a product without navigating an internal implementation
specification or a generated stand-in visualization.

The approved scope is the served `public/` landing experience. The investor,
game, soft-mirror, domain, and production-deployment surfaces are out of scope.

## Tech Stack

- Static HTML, CSS, JavaScript, and JSON
- No build step and no new runtime dependencies
- Vercel serves `public/` as configured by `vercel.json`
- Existing Japandi family tokens and system fonts

## Commands

- Static contract: `python -B scripts/check_gateway.py`
- Checker regressions:
  `$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s tests -p "test_gateway*.py" -v`
- Local server: `python -m http.server 4173 --directory public`
- Browser verification: run the gateway journey at 360, 768, and 1440 CSS pixels
- Existing package regression on Windows:
  `$env:PYTHONPATH="$PWD\packages\vector-core\src;$PWD\packages\vector-bench\src"; python -m pytest packages/vector-core/tests packages/vector-bench/tests -q`
- Diff hygiene: `git diff --check`

## Project Structure

- `public/index.html` — served gateway UI
- `public/assets/data/products.json` — verified product truth record
- `scripts/check_gateway.py` — deterministic static acceptance gate
- `tests/test_gateway_checker.py` — adversarial standard-library gate tests
- `.github/workflows/gateway.yml` — CI gate for served-site changes
- `docs/JAPANDI_DESIGN_SYSTEM.md` — family visual conventions
- `tasks/` — implementation plan and progress checklist

## Code Style

Use semantic HTML, native links and buttons, existing CSS custom properties, and
small dependency-free scripts. Keep complete product truth in semantic markup
for the no-JavaScript path, and require it to match the JSON record exactly:

```html
<a class="product-link" href="https://hoops.dumbmodel.com/">
  <span>Hoops</span>
  <span class="availability" data-state="available">
    Available — GET returned HTTP 200 at check time
  </span>
  <time datetime="2026-09-09T03:48:23Z">
    Availability checked: 2026-09-09T03:48:23Z
  </time>
  <time datetime="2026-09-07T16:33:45Z">
    Repository last pushed: 2026-09-07T16:33:45Z
  </time>
</a>
```

The UI may update a checked state from the local truth record, but it must
render the recorded `availability_method` and numeric
`availability_http_status` as a point-in-time HTTP result rather than
continuous monitoring. Unavailable products retain only their pinned evidence
anchor and expose no other anchor or product CTA.

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

- Exactly five products are presented, each with an explicit point-in-time
  availability state, exact method, numeric HTTP status, non-future
  `availability_checked_at`, pinned evidence source, and distinct non-future
  repository `pushed_at`.
- Available products expose their pinned HTTPS product URL; unavailable
  products expose no product CTA.
- The served landing journey contains no generated 20,719-point map, fabricated
  roster score, or internal `LCG`/fusion/layout specification copy.
- Product counts shown to users are sourced by the truth record or omitted.
- There is no horizontal overflow at 360, 768, or 1440 CSS pixels.
- The core journey is keyboard complete, focus-visible, and uses touch targets
  at least 44 by 44 CSS pixels.
- Automated accessibility reports zero serious or critical findings.
- Lab LCP is at most 2.5 seconds, CLS at most 0.10, and TBT at most 200 ms.
- Static, package-regression, browser, and preview gates pass before readiness.

## Open Questions

- Production deployment and rollback are intentionally unauthorized.
- Preview deployment is authorized, but preview access may still be blocked by
  the Vercel account boundary.
