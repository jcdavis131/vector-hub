# vector-hub

Landing page for [dumbmodel.com](https://dumbmodel.com) — a gateway to five
vector products:

- Hoops
- Gridiron
- Pitch
- Equities
- Unified

The served gateway publishes product destinations, point-in-time HTTP
availability with `availability_checked_at`, `availability_method`, and
numeric `availability_http_status`, evidence sources, and distinct repository
`pushed_at` timestamps from
[`public/assets/data/products.json`](public/assets/data/products.json). Validate
the served contract and its adversarial regression cases with:

```console
python -B scripts/check_gateway.py
$env:PYTHONDONTWRITEBYTECODE='1'; python -B -m unittest discover -s tests -p "test_gateway*.py" -v
```

Availability is not continuously monitored. At `2026-09-09T03:48:23Z`, direct
HTTP GET checks returned 200 for Hoops, Gridiron, Pitch, and Equities, and 404
for Unified; the gateway therefore offers no Unified product link.

Static HTML/CSS/JS, no build step. The repo is git-connected to the Vercel project `vector-hub` and serves the dumbmodel.com apex; pushes to `main` deploy automatically.

Model details and metrics live in the individual game repos (vector-hoops, vector-gridiron, vector-pitch, vector-equities).

## Hosted library: `vector-core`

This repo also hosts the shared `vector-core` library (the canonical MTNN building blocks used across the `vector-*` fleet) under [`packages/vector-core/`](packages/vector-core/). It is purely additive and is not part of the static site build. Install it directly from this repo:

```
pip install "vector-core @ git+https://github.com/jcdavis131/vector-hub.git#subdirectory=packages/vector-core"
```
